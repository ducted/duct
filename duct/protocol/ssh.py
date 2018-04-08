"""
.. module:: ssh
   :synopsis: Provides a simplified SSH client interface

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
# Had to work around a bunch of conch fails
# pylint: disable=W0212
import os

from twisted.conch.ssh.keys import EncryptedKeyError, Key
from twisted.conch.ssh import connection, channel
from twisted.conch.client.knownhosts import KnownHostsFile
from twisted.conch.endpoints import (SSHCommandClientEndpoint,
                                     AuthenticationFailed)

from twisted.internet import defer, protocol, reactor, error

from twisted.python.compat import nativeString
from twisted.python.filepath import FilePath
from twisted.python import log
from twisted.python.failure import Failure

# Monkey patch noisy logs
class FakeLog(object):
    """Silence immutable logging
    """
    def msg(self, *a):
        """Dummy message function"""
        pass

    def callWithLogger(self, *a, **kw):
        """Retain logger"""
        return log.callWithLogger(*a, **kw)


connection.log = FakeLog()
channel.log = FakeLog()

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


class SSHCommandProtocol(protocol.Protocol):
    """Protocol class for SSH commands
    """
    def __init__(self):
        self.factory = None
        self.stdOut = StringIO()
        self.stdErr = StringIO()
        self.finished = None

    def connectionMade(self):
        self.finished = defer.Deferred()

    def dataReceived(self, data):
        self.stdOut.write(data.decode())

    def extReceived(self, _code, data):
        """Received extended data, usually stderr
        """
        self.stdErr.write(data.decode())

    def connectionLost(self, reason=protocol.connectionDone):
        self.stdOut.seek(0)
        self.stdErr.seek(0)
        if reason.type is error.ConnectionDone:
            # Success
            code = 0
        else:
            code = reason.value.exitCode
        self.factory.done.callback((self.stdOut, self.stdErr, code))


class SSHClient(object):
    """Create an SSH connection and tunnel commands over it

    :param hostname: Hostname to connect to
    :type hostname: str
    :param port: Port to connect to
    :type port: int
    :param username: Username to authenticate with
    :type username: str
    :param password: Optionally use password auth, otherwise provide a key
    :type password: str
    :param knownhosts: Known hosts file path
    :type knownhosts: str
    """
    def __init__(self, hostname, username, port, password=None,
                 knownhosts=None):

        self.hostname = hostname.encode()
        self.username = username.encode()
        self.port = int(port)
        self.password = None
        self.endpoint = None
        if password:
            self.password = password.encode()
        self.connection = None

        if not knownhosts:
            knownhosts = '/var/lib/duct/known_hosts'

        self.knownHosts = KnownHostsFile.fromPath(FilePath(knownhosts.encode()))
        self.knownHosts.verifyHostKey = self.verifyHostKey

        self.keys = []

    def verifyHostKey(self, _ui, hostname, ip, key):
        """Called to verify host keys
        Does very minimal validation to prevent monitoring blockages
        """
        hhk = defer.maybeDeferred(self.knownHosts.hasHostKey, hostname, key)
        def gotHasKey(result):
            """Successfully found key"""
            if result:
                if not self.knownHosts.hasHostKey(ip, key):
                    log.msg("Added new %s host key for IP address '%s'." %
                            (key.type(), nativeString(ip)))
                    self.knownHosts.addHostKey(ip, key)
                    self.knownHosts.save()
                return result
            else:
                log.msg("Added %s host key for IP address '%s'." %
                        (key.type(), nativeString(ip)))
                self.knownHosts.addHostKey(hostname, key)
                self.knownHosts.addHostKey(ip, key)
                self.knownHosts.save()
                return True
        return hhk.addCallback(gotHasKey)

    def addKeyFile(self, kfile, password=None):
        """Import a private key file
        """
        if not os.path.exists(kfile):
            raise Exception("Key file not found %s" % kfile)

        try:
            self.keys.append(Key.fromFile(kfile))
        except EncryptedKeyError:
            self.keys.append(Key.fromFile(kfile, passphrase=password))

    def addKeyString(self, kstring, password=None):
        """Import a private key from a string
        """
        try:
            self.keys.append(Key.fromString(kstring))
        except EncryptedKeyError:
            self.keys.append(Key.fromString(kstring, passphrase=password))

    def _get_endpoint(self):
        """ Creates a generic endpoint connection that doesn't finish
        """
        return SSHCommandClientEndpoint.newConnection(
            reactor, b'/bin/cat', self.username, self.hostname,
            port=self.port, keys=self.keys, password=self.password,
            knownHosts=self.knownHosts
        )

    def connect(self):
        """Open connection to SSH server
        """
        log.msg("Opening SSH connection to %s@%s:%s" % (
            self.username, self.hostname, self.port))

        self.endpoint = self._get_endpoint()
        factory = protocol.Factory()
        factory.protocol = protocol.Protocol

        def connected(protocol):
            """Connection established
            """
            log.msg("Established SSH connection to %s" % (
                self.hostname,))
            self.connection = protocol.transport.conn

            real_transport = protocol.transport.conn.transport
            # Epic fail whomever wrote Conch :(
            def conLost(reason):
                """Connection lost
                """
                self.connectionLost(real_transport, reason)
            real_transport.connectionLost = conLost

        de = self.endpoint.connect(factory)
        de.addCallback(connected)

        return de

    def connectionLost(self, transport, reason):
        """Lost connection to SSH server
        """
        if transport._userauth:
            transport._userauth.loseAgentConnection()

        if transport._state == b'RUNNING' or transport.connectionReady is None:
            self.connection = None
            log.msg("Connection to %s lost: Retrying" % self.hostname)
            reactor.callLater(1, self.connect)
            return
        if transport._state == b'SECURING' and (
                transport._hostKeyFailure is not None):
            reason = transport._hostKeyFailure
        elif transport._state == b'AUTHENTICATING':
            reason = Failure(
                AuthenticationFailed("Connection lost while authenticating"))

        transport.connectionReady.errback(reason)

    def fork(self, command, args=(), env={}, path=None, _timeout=3600):
        """Execute a remote command on the SSH server
        """
        if not self.connection:
            return defer.maybeDeferred(lambda: (None, "SSH not ready", 255))

        if path:
            env['PATH'] = path

        if env:
            env = ' '.join('%s=%s' % (key, val) for key, val in env.items()
                          ) + ' '
        else:
            env = ''

        if args:
            args = ' ' + ' '.join(args)
        else:
            args = ''

        existing = SSHCommandClientEndpoint.existingConnection(
            self.connection, (env + command + args).encode()
        )

        factory = protocol.Factory()
        factory.protocol = SSHCommandProtocol
        factory.done = defer.Deferred()

        def finished(result):
            """Command finished
            """
            stdout, stderr, code = result
            return (stdout.read(), stderr.read(), code)

        factory.done.addCallback(finished)

        def connected(connection):
            """Connection established
            """
            # Be nice if Conch exposed this better...
            connection.transport.extReceived = connection.extReceived
            return factory.done

        return existing.connect(factory).addCallback(connected)
