import time
import json
import datetime

from twisted.internet import reactor, defer, task
from twisted.python import log

try:
    from OpenSSL import SSL
    from twisted.internet import ssl
except:
    SSL=None

from duct.objects import Output
from duct.protocol.opentsdb import OpenTSDBClient

from duct.outputs import opentsdb
from duct.utils import HTTPRequest

class Bosun(opentsdb.OpenTSDB):
    """Bosun HTTP API output

    **Configuration arguments:**

    :param url: URL (default: http://localhost:4242)
    :type url: str
    :param maxsize: Maximum queue backlog size (default: 250000, 0 disables)
    :type maxsize: int
    :param maxrate: Maximum rate of documents added to index (default: 100)
    :type maxrate: int
    :param interval: Queue check interval in seconds (default: 1.0)
    :type interval: int
    :param user: Optional basic auth username
    :type user: str
    :param password: Optional basic auth password
    :type password: str
    :param debug: Log tracebacks from OpenTSDB
    :type debug: str
    """
    def __init__(self, *a):
        opentsdb.OpenTSDB.__init__(self, *a)

        self.url = self.url.rstrip('/')

        self.metacache = {}

    def createMetadata(self, metas):
        headers = {}
        path = '/api/metadata/put'
        if self.user:
            authorization = b64encode('%s:%s' % (self.user, self.password)).decode()
            headers['Authorization'] = ['Basic ' + authorization]

        return HTTPRequest().getBody(
            self.url + path, 'POST', headers=headers, data=json.dumps(metas).encode())

    @defer.inlineCallbacks
    def sendEvents(self, events):
        tsdbEvents = []
        metadataBatch = []
        for e in events:
            if not self.metacache.get(e.service):
                metadataBatch.append({
                    "Metric": e.service,
                    "Name": "rate",
                    "Value": "gauge"
                })
                self.metacache[e.service] = True

            tsdbEvents.append(self.transformEvent(e))

        if metadataBatch:
            meta = yield self.createMetadata(metadataBatch)

        #result = yield self.client.put(tsdbEvents)
        result = {}

        defer.returnValue(result)
