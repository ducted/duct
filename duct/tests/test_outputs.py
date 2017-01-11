import json

from twisted.trial import unittest
from twisted.internet import defer

from duct.outputs import elasticsearch, opentsdb
from duct.objects import Event
from duct.service import DuctService

class ManualLooper(object):
    def __init__(self, task):
        self.task = task
        self.running = None

    def start(self, time):
        self.running = True

    def stop(self):
        self.running = False

    def tick(self):
        if not(self.running):
            raise Exception("Timer isn't running")

        return defer.maybeDeferred(self.task)

class Tests(unittest.TestCase):
    def setUp(self):
        self.service = DuctService({})
        self.event = Event('ok', 'sky', 'Sky has not fallen', 1.0, 60.0,
                           attributes={"chicken": "little"})

    def _fake_request(self, result, *a, **kw):
        self.last_request = (a, kw)
        return result

    def _bootstrap_output(self, outputClass, options={}):
        out = outputClass(options, self.service)
        out.t = ManualLooper(out.tick)
        out.createClient()

        return out

    @defer.inlineCallbacks
    def test_elasticsearch_output(self):
        def _wrap_request(*a, **kw):
            return defer.maybeDeferred(self._fake_request, {"errors":[]}, *a, **kw)

        out = self._bootstrap_output(elasticsearch.ElasticSearch)

        out.client._request = _wrap_request

        out.eventsReceived([self.event])

        yield out.t.tick()

        meta, metric = self.last_request[0][1].strip('\n').split('\n')
        requestData = json.loads(metric)

        self.assertEqual(requestData['service'], 'sky')

    @defer.inlineCallbacks
    def test_opentsdb_output(self):
        def _wrap_request(*a, **kw):
            return defer.maybeDeferred(self._fake_request, {"errors":[]}, *a, **kw)

        out = self._bootstrap_output(opentsdb.OpenTSDB)

        out.client._request = _wrap_request
        
        out.eventsReceived([self.event])

        yield out.t.tick()
        
        requestData = json.loads(self.last_request[0][1])[0]

        self.assertEqual(requestData['metric'], 'sky')
