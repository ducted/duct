"""
.. module:: utils
   :synopsis: Utility wrappers for HTTP calls and process forks

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import json
import time
import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from zope.interface import implementer

from twisted.internet import reactor, protocol, defer, error
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.web.client import Agent
from twisted.names import client
from twisted.python import log

from twisted.internet.endpoints import clientFromString


def wait(msecs):
    """Simple deferred delay function
    """
    d = defer.Deferred()
    reactor.callLater(msecs/1000.0, d.callback, None)
    return d

class SocketyAgent(Agent):
    """HTTP agent for connecting to UNIX sockets
    """
    def __init__(self, react, path, **kwargs):
        Agent.__init__(self, react, **kwargs)
        self.path = path

    def _getEndpoint(self, *_a):
        return clientFromString(reactor, self.path)

class Timeout(Exception):
    """
    Raised to notify that an operation exceeded its timeout.
    """

def reverseNameFromIPAddress(address):
    """Returns PTR record for IP
    """
    return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'

class Resolver(object):
    """Helper class for DNS resolution
    """

    def __init__(self):
        self.recs = {}
        self.resolver = client.getResolver()

    def reverse(self, ip):
        """Perform a reverse lookup on `ip`
        """
        def _ret(result, ip):
            host = ip
            if isinstance(result, tuple):
                answers, _, _ = result
                if isinstance(answers, list):
                    ttl = answers[0].payload.ttl
                    host = answers[0].payload.name.name
                    self.recs[ip] = (host, ttl, time.time())

            return host

        if ip in self.recs:
            host, ttl, ti = self.recs[ip]

            if (time.time() - ti) < ttl:
                return defer.maybeDeferred(lambda x: x, host)

        return self.resolver.lookupPointer(
            name=reverseNameFromIPAddress(address=ip)
        ).addCallback(_ret, ip).addErrback(_ret, ip)

class BodyReceiver(protocol.Protocol):
    """ Simple buffering consumer for body objects """
    def __init__(self, finished):
        self.finished = finished
        self.data = StringIO()

    def dataReceived(self, data):
        self.data.write(data.decode())

    def connectionLost(self, *_r):
        self.data.seek(0)
        self.finished.callback(self.data)

@implementer(IBodyProducer)
class StringProducer(object):
    """String producer for writing to HTTP requests
    """
    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        """Start writing content to consumer
        """
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        """Producing paused
        """
        pass

    def stopProducing(self):
        """Producing stopped
        """
        pass

class ProcessProtocol(protocol.ProcessProtocol):
    """ProcessProtocol which supports timeouts"""
    def __init__(self, deferred, timeout):
        self.timeout = timeout
        self.timer = None

        self.deferred = deferred
        self.outBuf = StringIO()
        self.errBuf = StringIO()

    def outReceived(self, data):
        self.outBuf.write(data.decode())

    def errReceived(self, data):
        self.errBuf.write(data.decode())

    def processEnded(self, reason):
        if self.timer and (not self.timer.called):
            self.timer.cancel()

        out = self.outBuf.getvalue()
        err = self.errBuf.getvalue()

        code = reason.value.exitCode

        if reason.value.signal:
            self.deferred.errback(reason)
        else:
            self.deferred.callback((out, err, code))

    def connectionMade(self):
        @defer.inlineCallbacks
        def killIfAlive():
            """Terminate after timeout if still alive
            """
            try:
                yield self.transport.signalProcess('KILL')
                log.msg('Killed source proccess: Timeout %s exceeded'
                        % self.timeout)
            except error.ProcessExitedAlready:
                pass

        self.timer = reactor.callLater(self.timeout, killIfAlive)

def fork(executable, args=(), env={}, path=None, timeout=3600):
    """fork
    Provides a deferred wrapper function with a timeout function

    :param executable: Executable
    :type executable: str.
    :param args: Tupple of arguments
    :type args: tupple.
    :param env: Environment dictionary
    :type env: dict.
    :param timeout: Kill the child process if timeout is exceeded
    :type timeout: int.
    """
    de = defer.Deferred()
    proc = ProcessProtocol(de, timeout)
    reactor.spawnProcess(proc, executable, (executable,)+tuple(args), env,
                         path)
    return de

try:
    from twisted.internet.ssl import ClientContextFactory

    class WebClientContextFactory(ClientContextFactory):
        """SSL Context factory
        """
        def getContext(self, *_a):
            return ClientContextFactory.getContext(self)
    SSL = True
except:
    SSL = False

try:
    from twisted.web import client as twclient
    # pylint: disable=W0212
    twclient._HTTP11ClientFactory.noisy = False
    twclient.HTTPClientFactory.noisy = False
except:
    pass

class HTTPRequest(object):
    """Helper class for creating HTTP requests.
       Accepts a `timeout` to cancel requests which take too long
    """
    def __init__(self, timeout=120):
        self.timeout = timeout
        self.timedout = None

    def abort_request(self, request):
        """Called to abort request on timeout"""
        self.timedout = True
        if not request.called:
            try:
                request.cancel()
            except error.AlreadyCancelled:
                return

    @defer.inlineCallbacks
    def response(self, request):
        """Response received
        """
        if request.length:
            de = defer.Deferred()
            request.deliverBody(BodyReceiver(de))
            body = yield de
            body = body.read()
        else:
            body = ""

        if (request.code < 200) or (request.code > 299):
            raise Exception((request.code, body))

        defer.returnValue(body)

    def request(self, url, method='GET', headers={}, data=None, socket=None,
                follow_redirect=False):
        """Perform an HTTP request
        """
        self.timedout = False

        if socket:
            agent = SocketyAgent(reactor, socket)
        else:
            if url[:5] == 'https':
                if SSL:
                    agent = Agent(reactor, WebClientContextFactory())
                else:
                    raise Exception('HTTPS requested but not supported')
            else:
                agent = Agent(reactor)

        request = agent.request(method.encode(), url.encode(),
                                Headers(headers),
                                StringProducer(data) if data else None)

        if self.timeout:
            timer = reactor.callLater(self.timeout, self.abort_request,
                                      request)

            def timeoutProxy(request):
                """Wrapper function to time-out requests
                """
                if timer.active():
                    timer.cancel()

                if follow_redirect and (request.code in (301, 302,)):
                    location = request.headers.getRawHeaders('location')
                    url = request.request.absoluteURI
                    if location:
                        if not location[0].startswith("http"):
                            # Well this isn't really allowed
                            if location[0].startswith("/"):
                                hp = '/'.join(url.split('/')[:3])
                                url = hp + location[0]
                            else:
                                url = url.rstrip('/') + '/' + location[0]
                        else:
                            url = location[0]

                        log.msg("Redirecting to %s" % url)

                        return self.request(url, method=method, headers=headers,
                                            data=data, socket=socket,
                                            follow_redirect=follow_redirect)
                    else:
                        raise Exception("Server responded with %s code but no"
                                        " location header" % request.code)

                return self.response(request)

            def requestAborted(failure):
                """Request was aborted due to timeout
                """
                if timer.active():
                    timer.cancel()

                failure.trap(defer.CancelledError,
                             error.ConnectingCancelledError)

                raise Timeout(
                    "Request took longer than %s seconds" % self.timeout)

            request.addCallback(timeoutProxy).addErrback(requestAborted)
        else:
            request.addCallback(self.response)

        return request


    def getBody(self, url, method='GET', headers={}, data=None, socket=None):
        """Make an HTTP request and return the body
        """

        if 'User-Agent' not in headers:
            headers['User-Agent'] = ['Ductd/1']

        return self.request(url, method, headers, data, socket)

    @defer.inlineCallbacks
    def getJson(self, url, method='GET', headers={}, data=None, socket=None):
        """Fetch a JSON result via HTTP
        """
        if 'Content-Type' not in headers:
            headers['Content-Type'] = ['application/json']

        body = yield self.getBody(url, method, headers, data, socket)

        try:
            if not body:
                defer.returnValue({})
            response = json.loads(body)
        except ValueError:
            raise ValueError("Response was not JSON: %s" % repr(body))

        defer.returnValue(response)

class PersistentCache(object):
    """A very basic dictionary cache abstraction. Not to be used
    for large amounts of data or high concurrency"""

    def __init__(self, location='/var/lib/duct/cache'):
        self.store = {}
        self.location = location
        self.mtime = 0
        self._read()

    def _changed(self):
        if os.path.exists(self.location):
            mtime = os.stat(self.location).st_mtime

            return self.mtime != mtime
        else:
            return False

    def _acquire_cache(self):
        try:
            cache_file = open(self.location, 'r')
        except IOError:
            return {}

        cache = json.loads(cache_file.read())
        cache_file.close()
        return cache

    def _write_cache(self, data):
        cache_file = open(self.location, 'w')
        cache_file.write(json.dumps(data))
        cache_file.close()

    def _persist(self):
        cache = self._acquire_cache()

        for key, val in self.store.items():
            cache[key] = val

        self._write_cache(cache)

    def _read(self):
        cache = self._acquire_cache()
        for key, val in cache.items():
            self.store[key] = val

    def _remove_key(self, key):
        cache = self._acquire_cache()
        if key in cache:
            if key in cache:
                cache.pop(key)
            if key in self.store:
                self.store.pop(key)
            self._write_cache(cache)

    def expire(self, age):
        """Expire any items in the cache older than `age` seconds"""
        now = time.time()
        cache = self._acquire_cache()

        expired = [key for key, val in cache.items() if (now - val[0]) > age]

        for key in expired:
            if key in cache:
                cache.pop(key)
            if key in self.store:
                self.store.pop(key)

        self._write_cache(cache)

    def set(self, key, val):
        """Set a key to value `val`"""
        self.store[key] = (time.time(), val)
        self._persist()

    def get(self, k):
        """Returns key contents, and modify time"""
        if self._changed():
            self._read()

        if k in self.store:
            return tuple(self.store[k])
        else:
            return None

    def contains(self, k):
        """Return True if key `k` exists"""
        if self._changed():
            self._read()
        return k in self.store.keys()

    def delete(self, k):
        """Remove key `k` from the cache"""
        self._remove_key(k)
