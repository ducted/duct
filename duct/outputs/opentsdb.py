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

class OpenTSDB(Output):
    """OpenTSDB HTTP API output

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
        Output.__init__(self, *a)
        self.events = []
        self.t = task.LoopingCall(self.tick)

        self.inter = float(self.config.get('interval', 1.0))  # tick interval
        self.maxsize = int(self.config.get('maxsize', 250000))

        self.user = self.config.get('user')
        self.password = self.config.get('password')

        self.url = self.config.get('url', 'http://localhost:4242')

        maxrate = int(self.config.get('maxrate', 100))

        if maxrate > 0:
            self.queueDepth = int(maxrate * self.inter)
        else:
            self.queueDepth = None

    def createClient(self):
        """Sets up HTTP connector and starts queue timer
        """

        self.client = OpenTSDBClient(self.url, self.user, self.password)

        self.t.start(self.inter)

    def stop(self):
        """Stop this client.
        """
        self.t.stop()

    def transformEvent(self, ev):
        """Convert an event object into OpenTSDB format
        """
        d = {
            'timestamp': int(ev.time * 1000),
            'metric': ev.service,
            'value': ev.metric,
            'tags': {
                'host': ev.hostname,
                'description': ev.description,
                'state': ev.state,
            }
        }

        if ev.tags:
            d['tags'] = ",".join(ev.tags)

        if ev.attributes:
            for k, v in ev.attributes.items():
                d['tags'][k] = v
        return d

    def sendEvents(self, events):
        return self.client.put([self.transformEvent(e) for e in events])

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
                if result.get('errors'):
                    log.msg('OpenTSDB error: %s' % repr(result))
                if result.get('error'):
                    log.msg('OpenTSDB error: %s' % result['error']['message'])
                    if self.config.get('debug'):
                        for ln in result['error']['trace'].split('\n'):
                            log.msg(ln)

            except Exception as e:
                log.msg('Could not connect to OpenTSDB ' + str(e))
                self.events.extend(events)
