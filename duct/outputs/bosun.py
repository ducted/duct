"""
.. module:: bosun
   :synopsis: Bosun output

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""


import json
import base64

from twisted.internet import defer

from duct.outputs import opentsdb
from duct.utils import HTTPRequest

class Bosun(opentsdb.OpenTSDB):
    """Bosun HTTP API output

    **Configuration arguments:**

    :param url: URL (default: http://localhost:4242)
    :type url: str.
    :param maxsize: Maximum queue backlog size (default: 250000, 0 disables)
    :type maxsize: int.
    :param maxrate: Maximum rate of documents added to index (default: 100)
    :type maxrate: int.
    :param interval: Queue check interval in seconds (default: 1.0)
    :type interval: int.
    :param user: Optional basic auth username
    :type user: str.
    :param password: Optional basic auth password
    :type password: str.
    :param debug: Log tracebacks from OpenTSDB
    :type debug: bool.
    """
    def __init__(self, *a):
        opentsdb.OpenTSDB.__init__(self, *a)

        self.url = self.url.rstrip('/')

        self.metacache = {}

    def createMetadata(self, metas):
        """Create metadata objects for new service keys
        """
        headers = {}
        path = '/api/metadata/put'
        if self.user:
            authorization = base64.b64encode('%s:%s' % (self.user,
                                                        self.password)
                                            ).decode()
            headers['Authorization'] = ['Basic ' + authorization]

        return HTTPRequest().getBody(self.url + path, 'POST', headers=headers,
                                     data=json.dumps(metas).encode())

    @defer.inlineCallbacks
    def sendEvents(self, events):
        tsdbEvents = []
        metadataBatch = []
        for event in events:
            if not self.metacache.get(event.service):
                metadataBatch.append({
                    "Metric": event.service,
                    "Name": "rate",
                    "Value": "gauge"
                })
                self.metacache[event.service] = True

            tsdbEvents.append(self.transformEvent(event))

        if metadataBatch:
            yield self.createMetadata(metadataBatch)

        result = yield self.client.put(tsdbEvents)

        defer.returnValue(result)
