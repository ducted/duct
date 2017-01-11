import time
import json

from twisted.trial import unittest

from twisted.internet import defer, reactor, error
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from duct.protocol import riemann, elasticsearch, opentsdb

from duct.objects import Event

from duct.utils import fork

class Tests(unittest.TestCase):
    def setUp(self):
        self.endpoint = None
        self.last_request = None

    def tearDown(self):
        if self.endpoint:
            return defer.maybeDeferred(self.endpoint.stopListening)

    def _fake_request(self, result, *a, **kw):
        self.last_request = (a, kw)
        return result

    @defer.inlineCallbacks
    def test_elasticsearch_proto(self):
        proto = elasticsearch.ElasticSearch()

        def _wrap_request(*a, **kw):
            return defer.maybeDeferred(self._fake_request, {"errors":[]}, *a, **kw)

        proto._request = _wrap_request

        index = proto._get_index()

        t = time.strptime(index, "duct-%Y.%m.%d")
        self.assertEqual(time.gmtime().tm_year, t.tm_year)
        self.assertEqual(time.gmtime().tm_mday, t.tm_mday)
        self.assertEqual(time.gmtime().tm_mon, t.tm_mon)

        event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0,
                      attributes={"chicken": "little"})

        ans = yield proto.bulkIndex([dict(event)])

        self.assertEqual(ans['errors'], [])

        meta, metric = self.last_request[0][1].strip('\n').split('\n')
        requestMeta = json.loads(meta)
        requestData = json.loads(metric)

        self.assertEqual(self.last_request[0][0], '/_bulk')
        self.assertEqual(requestMeta['index']['_index'], index)
        self.assertEqual(requestData['service'], 'sky')

    def test_riemann_protobuf(self):
        proto = riemann.RiemannProtocol()

        event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0)

        # Well, I guess we'll just assume this is right
        message = proto.encodeMessage([event])

    def test_riemann_protobuf_with_attributes(self):
        proto = riemann.RiemannProtocol()

        event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0,
                      attributes={"chicken": "little"})

        e = proto.encodeEvent(event)
        attrs = e.attributes
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0].key, "chicken")
        self.assertEqual(attrs[0].value, "little")

    @defer.inlineCallbacks
    def test_tcp_riemann(self):

        event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0)

        end = TCP4ClientEndpoint(reactor, "localhost", 5555)
       
        p = yield connectProtocol(end, riemann.RiemannProtocol())

        yield p.sendEvents([event])

        p.transport.loseConnection()

    @defer.inlineCallbacks
    def test_udp_riemann(self):

        event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0)
        
        protocol = riemann.RiemannUDP('127.0.0.1', 5555)
        self.endpoint = reactor.listenUDP(0, protocol)

        yield protocol.sendEvents([event])

    @defer.inlineCallbacks
    def test_utils_fork(self):
        o, e, c = yield fork('echo', args=('hi',))

        self.assertEquals(o, "hi\n")
        self.assertEquals(c, 0)

    @defer.inlineCallbacks
    def test_utils_fork_timeout(self):
        died = False
        try:
            o, e, c = yield fork('sleep', args=('2',), timeout=0.1)
        except error.ProcessTerminated:
            died = True

        self.assertTrue(died)
