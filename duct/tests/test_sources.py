import json
import socket
import os

from twisted.trial import unittest
from twisted.internet import defer, endpoints, reactor
from twisted.web import server, static

from duct.sources.linux import basic, process, sensors
from duct.sources import riak, nginx, network, apache, munin, haproxy
from duct.sources.database import elasticsearch, postgresql, memcache
from duct.service import DuctService
from duct.tests import globs


class TestSources(unittest.TestCase):
    def setUp(self):
        self.duct = DuctService({})

    def skip_if_no_hostname(self):
        try:
            socket.gethostbyaddr(socket.gethostname())
        except socket.herror:
            raise unittest.SkipTest('Unable to get local hostname.')

    def _qb(self, source, events):
        pass

class FakeDBAPI(object):
    def __init__(self, queryHandler=None):
        self.queryHandler = queryHandler or self._handle_query
        self.closed = False

    def _handle_query(self, request):
        return []

    def runQuery(self, query, *a, **kw):
        """ Run a query """
        return defer.maybeDeferred(self.queryHandler, query)

    def close(self):
        """ Closes fake connection """
        def _close():
            self.closed = True
        return defer.maybeDeferred(_close)

class FakeMuninServer(object):
    configs = {
        'apache_accesses': globs.MUNIN_APACHE_ACCESSES,
        'apache_processes': globs.MUNIN_APACHE_PROCS
    }

    results = {
        'apache_accesses': 'accesses80.value $',
        'apache_processes': 'busy80.value 1\nidle80.value 49\nfree80.value 100'
    }

    def sendCommand(self, command, clist=False):
        d = defer.Deferred()

        result = ""
        if command.startswith('cap '):
            result = "cap multigraph dirtyconfig"

        if command == 'list':
            result = globs.MUNIN_LIST + '\n'

        if command.startswith('config '):
            toconfigure = command.split()[-1]
            result = self.configs.get(toconfigure, "")

        if command.startswith('fetch '):
            tofetch = command.split()[-1]
            result = self.results.get(tofetch, "")

        if clist:
            d.callback(result.strip('\n').split('\n'))
        else:
            d.callback(result)

        return d

    def disconnect(self):
        d = defer.Deferred()
        d.callback(None)
        return d

class FakeTransport(object):
    def loseConnection(self, *a):
        return None

class FakeMemcache(object):
    transport = FakeTransport()
    def stats(self):
        return globs.MEMCACHE_STATS

class TestOther(TestSources):
    @defer.inlineCallbacks
    def test_postgresql(self):
        def queryHandler(request):
            return [
                ('template1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                ('template0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                ('postgres', 1, 1256230, 1, 1058, 33931091, 405747556, 6290701,
                 0, 0, 0),
                ('testdb', 0, 1304478, 0, 1495, 53416317, 686856059, 9578732,
                 3094, 460, 151)
            ]

        events = []
        def _qb(source, event):
            events.append(event)
        s = postgresql.PostgreSQL({'service': 'postgres'},
                                  _qb, self.duct)

        s._get_connection = lambda: FakeDBAPI(queryHandler)

        event = yield s.get()

        self.assertEquals(events[1].service, 'postgres.postgres.commits')
        self.assertEquals(events[1].metric, 1256230)

    @defer.inlineCallbacks
    def test_elastic(self):
        s = elasticsearch.ElasticSearch({'service': 'es'},
                                          self._qb, self.duct)

        def _request(path):
            if path == '/_cluster/stats':
                return globs.ES_CLUSTER_STATS

            if path == '/_nodes/stats':
                return globs.ES_NODES_STATS

        def _request_wrapper(path, **kw):
            return defer.maybeDeferred(_request, path)

        s.client._request = _request_wrapper

        events = yield s.get()

        self.assertEquals(events[0].service, 'es.cluster.status')
        self.assertEquals(events[0].metric, 1)

    @defer.inlineCallbacks
    def test_munin(self):
        s = munin.MuninNode({'service': 'munin'}, self._qb, self.duct)

        def _connect_munin():
            return defer.maybeDeferred(lambda: FakeMuninServer())

        s._connect_munin = _connect_munin

        events = yield s.get()

        self.assertEquals(events[0].metric, 1)
        self.assertEquals(events[1].metric, 49.0)

    @defer.inlineCallbacks
    def test_memcache(self):
        def _get_connector():
            return defer.maybeDeferred(lambda: FakeMemcache())
        s = memcache.Memcache({'service': 'memcache'}, self._qb, self.duct)
        s._get_connector = _get_connector

        events = yield s.get()

        self.assertEquals(events[3].service, 'memcache.total.items')
        self.assertEquals(events[3].metric, 44)

    @defer.inlineCallbacks
    def test_haproxy(self):
        def _get_stats():
            return defer.maybeDeferred(lambda: globs.HAPROXY_CSV)

        s = haproxy.HAProxy({'service': 'haproxy'}, self._qb, self.duct)
        s._get_stats = _get_stats

        events = yield s.get()

    def test_sensors(self):
        s = sensors.Sensors({'service': 'sensors'}, self._qb, self.duct)
        events = s.get()

        s._find_sensors = lambda: {
            'acpitz': {},
            'coretemp': {'physical_id_0': 58.0, 'core_0': 58.0, 'core_1': 54.0},
            'dell_smm': {'other': 34.0, 'processor_fan': 0, 'ambient': 48.0, 'cpu': 54.0, 'sodimm': 38.0}
        }

        events = s.get()

        e = [e for e in events if e.service ==
                'sensors.coretemp.physical_id_0']

        self.assertEquals(e[0].metric, 58.0)

class TestLinuxSources(TestSources):
    def test_basic_cpu(self):
        self.skip_if_no_hostname()
        s = basic.CPU({'service': 'cpu'}, self._qb, self.duct)

        try:
            s.get()
            s.get()
        except:
            raise unittest.SkipTest('Might not exist in docker')

    def test_basic_cpu_multi_core(self):
        s = basic.CPU({
            'service': 'cpu',
            'hostname': 'localhost',
        }, self._qb, self.duct)

        stats = [
            "cpu  2255 34 2290 25563 6290 127 456 0 0 0",
            "cpu0 181705 1227 44920 4777152 5864 0 8054 0 0 0",
            "cpu1 186678 1194 43662 1196906 1169 0 860 0 0 0"
        ]

        s._read_proc_stat = lambda: stats
        # This is the first time we're getting this stat, so we get no events.
        self.assertEqual(s.get(), None)

        stats = ["cpu  4510 68 4580 51126 12580 254 912 0 0 0"]
        stats = [
            "cpu  2255 34 2290 25563 6290 127 456 0 0 0",
            "cpu0 181728 1227 44936 4781296 5865 0 8055 0 0 0",
            "cpu1 186712 1194 43670 1201159 1173 0 860 0 0 0"
        ]

        s._read_proc_stat = lambda: stats
        events = s.get()
        cpu_event = events[-1]
        iowait_event = events[4]
        self.assertEqual(cpu_event.service, 'cpu.core1')
        self.assertEqual(round(cpu_event.metric, 4), 0.0098)
        self.assertEqual(iowait_event.service, 'cpu.core0.iowait')
        self.assertEqual(round(iowait_event.metric, 4), 0.0002)

    def test_basic_cpu_calculation(self):
        s = basic.CPU({
            'service': 'cpu',
            'hostname': 'localhost',
        }, self._qb, self.duct)

        stats = ["cpu  2255 34 2290 25563 6290 127 456 0 0 0"]
        s._read_proc_stat = lambda: stats
        # This is the first time we're getting this stat, so we get no events.
        self.assertEqual(s.get(), None)

        stats = ["cpu  4510 68 4580 51126 12580 254 912 0 0 0"]
        s._read_proc_stat = lambda: stats
        events = s.get()
        cpu_event = events[-1]
        iowait_event = events[4]
        self.assertEqual(cpu_event.service, 'cpu')
        self.assertEqual(round(cpu_event.metric, 4), 0.1395)
        self.assertEqual(iowait_event.service, 'cpu.iowait')
        self.assertEqual(round(iowait_event.metric, 4), 0.1699)

    @defer.inlineCallbacks
    def test_basic_cpu_ssh(self):
        s = basic.CPU({
            'service': 'cpu',
            'use_ssh': True,
            'ssh_knownhosts_file': None,
            'ssh_password': 'None',
            'ssh_username': 'test',
            'hostname': 'localhost',
        }, self._qb, self.duct)

        stats = "cpu  2255 34 2290 25563 6290 127 456 0 0 0\n"
        s.fork = lambda *x: defer.maybeDeferred(lambda *x: (stats, '', 0))
        # This is the first time we're getting this stat, so we get no events.
        m = yield s.sshGet()
        self.assertEqual(m, None)

        stats = "cpu  4510 68 4580 51126 12580 254 912 0 0 0\n"
        s.fork = lambda *x: defer.maybeDeferred(lambda *x: (stats, '', 0))
        events = yield s.sshGet()
        cpu_event = events[-1]
        iowait_event = events[4]
        self.assertEqual(cpu_event.service, 'cpu')
        self.assertEqual(round(cpu_event.metric, 4), 0.1395)
        self.assertEqual(iowait_event.service, 'cpu.iowait')
        self.assertEqual(round(iowait_event.metric, 4), 0.1699)

    def test_basic_cpu_calculation_no_guest_stats(self):
        s = basic.CPU({'service': 'cpu', 'hostname': 'localhost'},
                      self._qb, self.duct)

        stats = ["cpu  2255 34 2290 25563 6290 127 456 0"]
        s._read_proc_stat = lambda: stats
        # This is the first time we're getting this stat, so we get no events.
        self.assertEqual(s.get(), None)

        stats = ["cpu  4510 68 4580 51126 12580 254 912 0"]
        s._read_proc_stat = lambda: stats
        events = s.get()
        cpu_event = events[-1]
        iowait_event = events[4]
        self.assertEqual(cpu_event.service, 'cpu')
        self.assertEqual(round(cpu_event.metric, 4), 0.1395)
        self.assertEqual(iowait_event.service, 'cpu.iowait')
        self.assertEqual(round(iowait_event.metric, 4), 0.1699)

    def test_disk_io(self):
        s = basic.DiskIO({'service': 'disk', 'hostname': 'localhost'},
                         self._qb, self.duct)

        stats = [
            '   1       0 ram0 0 0 0 0 0 0 0 0 0 0 0',
            '   7       0 loop0 0 0 0 0 0 0 0 0 0 0 0',
            ' 202       2 xvda2 2 0 4 64 0 0 0 0 0 64 64',
            ' 202      32 xvdc 576 10 3739 748 144 0 4497 18080 0 8616 18828',
            ' 202      33 xvdc1 423 0 2435 264 144 0 4497 18080 0 8132 18344',
        ]

        s._getstats = lambda: stats
        events = s.get()

        self.assertEqual(events[0].metric, 32)
        self.assertEqual(events[1].metric, 2)

    def test_basic_memory(self):
        self.skip_if_no_hostname()
        s = basic.Memory({'service': 'mem'}, self._qb, self.duct)

        s.get()

    def test_basic_memory_avail(self):
        s = basic.Memory(
            {'interval': 1.0, 'service': 'mem'}, self._qb, self.duct)

        out = """MemTotal:        8048992 kB
MemFree:         2774664 kB
MemAvailable:    5631108 kB
Buffers:          145408 kB
Cached:          3183724 kB
SwapCached:            0 kB\n"""
        event = s._parse_stats(out.split('\n'))

        used, total = event.description.split()[-1].split('/')
        used = int(used)
        total = int(total)
        avail = total - used

        self.assertEquals(avail, 5631108)

        out = """MemTotal:        8048992 kB
MemFree:         2774664 kB
Buffers:          145408 kB
Cached:          3183724 kB
SwapCached:            0 kB\n"""
        event = s._parse_stats(out.split('\n'))

        used, total = event.description.split()[-1].split('/')
        used = int(used)
        total = int(total)
        avail = total - used

        self.assertEquals(avail, 6103796)


    def test_basic_load(self):
        self.skip_if_no_hostname()
        s = basic.LoadAverage({'service': 'mem'}, self._qb, self.duct)

        s.get()

    @defer.inlineCallbacks
    def test_process_count(self):
        self.skip_if_no_hostname()
        s = process.ProcessCount({'service': 'proc'}, self._qb, self.duct)

        yield s.get()

    @defer.inlineCallbacks
    def test_basic_disk_space(self):
        self.skip_if_no_hostname()
        s = basic.DiskFree({'service': 'df'}, self._qb, self.duct)

        yield s.get()

    @defer.inlineCallbacks
    def test_process_stats(self):
        self.skip_if_no_hostname()
        s = process.ProcessStats({'service': 'ps'}, self._qb, self.duct)

        yield s.get()

    @defer.inlineCallbacks
    def test_http_request(self):
        self.skip_if_no_hostname()
        s = network.HTTP({'service': 'http', 'url': 'http://httpbin.org'},
                         self._qb, self.duct)

        event = yield s._get()
        self.assertEquals(event.state, 'ok')

    @defer.inlineCallbacks
    def test_http_request_timeout(self):
        self.skip_if_no_hostname()
        s = network.HTTP({
            'service': 'http',
            'timeout': 1,
            'url': 'http://1.1.1.1/'
        }, self._qb, self.duct)

        event = yield s._get()
        self.assertEquals(event.state, 'critical')
        self.assertEquals('timeout' in event.description, True)

    @defer.inlineCallbacks
    def test_http_request_fail(self):
        self.skip_if_no_hostname()
        s = network.HTTP({
            'service': 'http',
            'url': 'http://noresolve/'
        }, self._qb, self.duct)

        event = yield s._get()
        self.assertEquals(event.state, 'critical')

    def test_network_stats(self):
        self.skip_if_no_hostname()
        s = basic.Network({'service': 'net'}, self._qb, self.duct)

        s._readStats = lambda: [
            '  eth0: 254519754 1437339    0    0    0     0          0      '+
            '   0 202067280 1154168    0    0    0     0       0          0',
            '    lo: 63830682  900933    0    0    0     0          0       '+
            '  0 63830682  900933    0    0    0     0       0          0'
        ]

        ev = s.get()
        self.assertEquals(ev[0].metric, 254519754)
        self.assertEquals(ev[1].metric, 1437339)
        self.assertEquals(ev[2].metric, 0)
        self.assertEquals(ev[3].metric, 202067280)
        self.assertEquals(ev[4].metric, 1154168)
        self.assertEquals(ev[5].metric, 0)

    @defer.inlineCallbacks
    def test_apache_stats(self):
        src = apache.Apache({
            'service': 'apache',
            'hostname': 'localhost',
            'url': 'http://localhost/server-status?auto'
        }, self._qb, self.duct)

        def apstats():
            return globs.APACHE_STATS

        src._get_stats = lambda: defer.maybeDeferred(apstats)

        events = yield src.get()

        results = {
            'apache.uptime': 4564,
            'apache.accesses': 46,
            'apache.cpu_load': 0.036,
            'apache.bytes_req': 868.125,
            'apache.bytes_rate': 8.75,
            'apache.total_kbytes': 39,
            'apache.conns.active': 9,
            'apache.request_rate': 0.5,
            'apache.workers.idle': 48,
            'apache.workers.busy': 2,
            'apache.conns.writing': 2,
            'apache.conns.closing': 4,
            'apache.conns.keep_alive': 3,
        }

        for ev in events:
            self.assertEquals(ev.metric, results.get(ev.service))

    def test_nginx_parse(self):
        src = nginx.Nginx({
            'service': 'nginx',
            'hostname': 'localhost',
            'stats_url': 'http://localhost/nginx_stats'
        }, self._qb, self.duct)

        ngstats = """Active connections: 3
server accepts handled requests
 20649 20649 686969
Reading: 0 Writing: 1 Waiting: 2\n"""

        metrics = src._parse_nginx_stats(ngstats)

        self.assertEquals(metrics['handled'][0], 20649)

    def test_nginx_log_nohistory(self):
        try:
            os.unlink('foo.log.lf')
            os.unlink('foo.log')
        except:
            pass

        events = []

        def qb(src, ev):
            events.append(ev)

        f = open('foo.log', 'wt')
        f.write('192.168.0.1 - - [16/Jan/2015:16:31:29 +0200] "GET /foo HTTP/1.1" 200 210 "-" "My Browser"\n')
        f.write('192.168.0.1 - - [16/Jan/2015:16:51:29 +0200] "GET /foo HTTP/1.1" 200 410 "-" "My Browser"\n')
        f.flush()

        src = nginx.NginxLogMetrics({
            'service': 'nginx',
            'hostname': 'localhost',
            'log_format': 'combined',
            'file': 'foo.log'
        }, qb, self.duct)

        src.log.tmp = 'foo.log2.lf'

        src.get()

        self.assertEquals(len(events), 0)

        f.write('192.168.0.1 - - [16/Jan/2015:17:31:29 +0200] "GET /foo HTTP/1.1" 200 210 "-" "My Browser"\n')
        f.write('192.168.0.1 - - [16/Jan/2015:17:51:29 +0200] "GET /foo HTTP/1.1" 200 410 "-" "My Browser"\n')
        f.flush()

        src.get()

        self.assertEquals(len(events)>0, True)

    def test_nginx_log(self):
        try:
            os.unlink('foo.log.lf')
            os.unlink('foo.log')
        except:
            pass

        events = []

        def qb(src, ev):
            events.append(ev)

        f = open('foo.log', 'wt')
        f.write('192.168.0.1 - - [16/Jan/2015:16:31:29 +0200] "GET /foo HTTP/1.1" 200 210 "-" "My Browser"\n')
        f.write('192.168.0.1 - - [16/Jan/2015:16:51:29 +0200] "GET /foo HTTP/1.1" 200 410 "-" "My Browser"\n')
        f.flush()

        src = nginx.NginxLogMetrics({
            'service': 'nginx',
            'hostname': 'localhost',
            'log_format': 'combined',
            'history': True,
            'file': 'foo.log'
        }, qb, self.duct)

        src.log.tmp = 'foo.log.lf'

        src.get()

        ev1 = events[0]
        ev2 = events[1]

        for i in ev1:
            if i.service=='nginx.client.192.168.0.1.bytes':
                self.assertEquals(i.metric, 210)

        for i in ev2:
            if i.service=='nginx.client.192.168.0.1.bytes':
                self.assertEquals(i.metric, 410)

        events = []

        f.write('192.168.0.1 - - [16/Jan/2015:17:10:31 +0200] "GET /foo HTTP/1.1" 200 410 "-" "My Browser"\n')
        f.write('192.168.0.1 - - [16/Jan/2015:17:10:34 +0200] "GET /bar HTTP/1.1" 200 410 "-" "My Browser"\n')
        f.close()

        src.get()

        for i in events[0]:
            if i.service=='nginx.client.192.168.0.1.requests':
                self.assertEquals(i.metric, 2)
            if i.service=='nginx.user-agent.My Browser.bytes':
                self.assertEquals(i.metric, 820)

            if i.service=='nginx.request./foo.bytes':
                self.assertEquals(i.metric, 410)

class TestRiakSources(TestSources):
    def start_fake_riak_server(self, stats):
        def cb(listener):
            self.addCleanup(listener.stopListening)
            return listener

        data = static.Data(json.dumps(stats).encode(), 'application/json')

        data.isLeaf = True
        site = server.Site(data)
        endpoint = endpoints.TCP4ServerEndpoint(reactor, 0)
        return endpoint.listen(site).addCallback(cb)

    def make_riak_stats_source(self, config_overrides={}):
        config = {
            'service': 'riak',
            'hostname': 'localhost',
        }
        config.update(config_overrides)
        return riak.RiakStats(config, self._qb, self.duct)

    @defer.inlineCallbacks
    def test_riak_stats_zeros(self):
        listener = yield self.start_fake_riak_server({
            'node_gets': 0,
            'node_puts': 0,
        })
        addr = listener.getHost()
        url = 'http://localhost:%s/' % (addr.port,)
        s = self.make_riak_stats_source({'url': url})

        [gets, puts] = yield s.get()
        self.assertEqual(gets.service, "riak.gets_per_second")
        self.assertEqual(gets.metric, 0.0)
        self.assertEqual(puts.service, "riak.puts_per_second")
        self.assertEqual(puts.metric, 0.0)

    @defer.inlineCallbacks
    def test_riak_stats(self):
        listener = yield self.start_fake_riak_server({
            'node_gets': 150,
            'node_puts': 45,
        })
        addr = listener.getHost()
        url = 'http://localhost:%s/' % (addr.port,)
        s = self.make_riak_stats_source({'url': url})

        [gets, puts] = yield s.get()
        self.assertEqual(gets.service, "riak.gets_per_second")
        self.assertEqual(gets.metric, 2.5)
        self.assertEqual(puts.service, "riak.puts_per_second")
        self.assertEqual(puts.metric, 0.75)

