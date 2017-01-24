"""
.. module:: elasticsearch
   :synopsis: Elasticsearch event output

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
import datetime

from twisted.internet import defer, task
from twisted.python import log

from duct.protocol import elasticsearch

from duct.objects import Output


class ElasticSearch(Output):
    """ElasticSearch HTTP API output

    **Configuration arguments:**

    :param url: Elasticsearch URL (default: http://localhost:9200)
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
    :param index: Index name format to store documents in Elastic
                  (default: duct-%Y.%m.%d)
    :type index: str
    """
    def __init__(self, *a):
        Output.__init__(self, *a)
        self.events = []
        self.timer = task.LoopingCall(self.tick)

        self.inter = float(self.config.get('interval', 1.0))  # tick interval
        self.maxsize = int(self.config.get('maxsize', 250000))

        self.user = self.config.get('user')
        self.password = self.config.get('password')

        self.url = self.config.get('url', 'http://localhost:9200')

        maxrate = int(self.config.get('maxrate', 100))

        self.index = self.config.get('index', 'duct-%Y.%m.%d')

        self.client = None

        if maxrate > 0:
            self.queueDepth = int(maxrate * self.inter)
        else:
            self.queueDepth = None

    def createClient(self):
        """Sets up HTTP connector and starts queue timer
        """

        self.client = elasticsearch.ElasticSearch(self.url, self.user,
                                                  self.password, self.index)

        self.timer.start(self.inter)

    def stop(self):
        """Stop this client.
        """
        self.timer.stop()

    def transformEvent(self, event):
        """Transform an event into a format useful to Elasticsearch
        """
        data = dict(event)
        timestamp = datetime.datetime.utcfromtimestamp(event.time)
        data['metric'] = float(event.metric)
        data['@timestamp'] = timestamp.isoformat()

        if 'ttl' in data:
            # Useless field to Elasticsearch
            data.pop('ttl')

        return data

    def sendEvents(self, events):
        """Send events to Elasticsearch in bulk
        """
        return self.client.bulkIndex([self.transformEvent(event)
                                      for event in events])

    @defer.inlineCallbacks
    def tick(self):
        """Clock tick called every self.inter
        """
        if self.events:
            if self.queueDepth and (len(self.events) > self.queueDepth):
                # Remove maximum of self.queueDepth items from queue
                events = self.events[:self.queueDepth]
                self.events = self.events[self.queueDepth:]
            else:
                events = self.events
                self.events = []

            try:
                result = yield self.sendEvents(events)
                if result.get('errors', False):
                    log.msg(repr(result))

            except Exception as ex:
                log.msg('Could not connect to elasticsearch ' + str(ex))
                self.events.extend(events)

# Backward compatibility stub
ElasticSearchLog = ElasticSearch
