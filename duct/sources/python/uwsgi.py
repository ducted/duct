"""
.. module:: uwsgi
   :platform: Any
   :synopsis: Reads UWSGI stats

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import json

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from zope.interface import implementer

from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientCreator, Protocol

from duct.interfaces import IDuctSource
from duct.objects import Source

class JSONProtocol(Protocol):
    """
    JSON line protocol
    """
    delimiter = '\n'
    def __init__(self):
        self.ready = False
        self.buf = StringIO()
        self.d = defer.Deferred()

    def dataReceived(self, data):
        self.buf.write(data)

    def connectionLost(self, *_a):
        self.buf.seek(0)
        self.d.callback(json.load(self.buf))

    def disconnect(self):
        """Disconnect transport
        """
        return self.transport.loseConnection()


@implementer(IDuctSource)
class Emperor(Source):
    """Connects to UWSGI Emperor stats and creates useful metrics

    **Configuration arguments:**

    :param host: Hostname (default localhost)
    :type host: str.
    :param port: Port
    :type port: int.

    """

    @defer.inlineCallbacks
    def get(self):
        host = self.config.get('host', 'localhost')
        port = int(self.config.get('port', 6001))

        proto = yield ClientCreator(
            reactor, JSONProtocol).connectTCP(host, port)

        stats = yield proto.d

        nodes = stats.get('vassals', [])

        events = []

        active = 0
        accepting = 0
        respawns = 0

        for node in nodes:
            if node['accepting'] > 0:
                active += 1
                accepting += node['accepting']
            if node['respawns'] > 0:
                respawns += 1

            events.extend([
                self.createEvent('ok', 'accepting', node['accepting'],
                                 prefix=node['id'] + '.accepting'),
                self.createEvent('ok', 'respawns', node['respawns'],
                                 prefix=node['id'] + '.respawns'),
            ])


        events.extend([
            self.createEvent('ok', 'active', active, prefix='total.active'),
            self.createEvent('ok', 'accepting', accepting,
                             prefix='total.accepting'),
            self.createEvent('ok', 'respawns', respawns,
                             prefix='total.respawns'),
        ])

        defer.returnValue(events)
