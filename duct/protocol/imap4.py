"""
.. module:: imap4
   :platform: Unix
   :synopsis: IMAP4 protocol helper classes

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

# pylint: disable=C0413

import sys

if sys.version_info > (3, 0):
    raise Exception("This protocol is not yet supported on Python 3")

from twisted.internet import defer, reactor, ssl, endpoints, protocol
from twisted.mail import imap4
from twisted.python import log


class IMAPClientProtocol(imap4.IMAP4Client):
    """IMAP4 client connector protocol
    """
    greetDeferred = None
    debug = False

    def dataReceived(self, data):
        if self.debug:
            log.msg(data)
        imap4.IMAP4Client.dataReceived(self, data)

    def serverGreeting(self, caps):
        self.serverCapabilities = caps
        if self.greetDeferred is not None:
            de, self.greetDeferred = self.greetDeferred, None
            de.callback(self)


class IMAP4ClientFactory(protocol.ClientFactory):
    """IMAP4 client factory
    """
    usedUp = False
    protocol = IMAPClientProtocol
    debug = False

    def __init__(self, username, onConn):
        self.username = username
        self.onConn = onConn

    def buildProtocol(self, addr):
        assert not self.usedUp
        self.usedUp = True

        proto = self.protocol()
        proto.debug = self.debug
        proto.factory = self
        proto.greetDeferred = self.onConn

        proto.registerAuthenticator(imap4.PLAINAuthenticator(self.username))
        proto.registerAuthenticator(imap4.LOGINAuthenticator(self.username))
        proto.registerAuthenticator(
            imap4.CramMD5ClientAuthenticator(self.username)
        )

        return proto

    def clientConnectionFailed(self, connector, reason):
        de, self.onConn = self.onConn, None
        de.errback(reason)


class IMAPClient(object):
    """IMAP4 Client

    :param host: Server hostname
    :type host: str.
    :param port: Port
    :type port: int.
    :param user: Username
    :type user: str.
    :param password: Password
    :type password: str.
    :param ssl: Use SSL (default: False)
    :type ssl: bool.
    """

    def __init__(self, host, port, user, password, ssl=False, debug=False):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.ssl = ssl
        self.debug = debug

        self.mailboxes = {}

        self.selected = None

        self.connected = None
        self.connecting = False

    @defer.inlineCallbacks
    def connect(self):
        """Connect and authenticate with the IMAP server
        """
        if self.connecting:
            defer.returnValue(None)

        self.connecting = True

        endpoint = endpoints.HostnameEndpoint(reactor, self.host, self.port)

        if self.ssl:
            contextFactory = ssl.optionsForClientTLS(
                hostname=self.host.decode('utf-8')
            )
            endpoint = endpoints.wrapClientTLS(contextFactory, endpoint)

        de = defer.Deferred()
        factory = IMAP4ClientFactory(self.user, de)
        factory.debug = self.debug

        yield endpoint.connect(factory)
        self.proto = yield de

        yield self.proto.authenticate(self.password)

        self.connected = True
        self.connecting = False

    @defer.inlineCallbacks
    def getMailboxes(self):
        """Lists mailboxes for this account
        """
        if not self.connected:
            raise Exception("Not connected")

        mailbox = yield self.proto.list("", "*")

        for attrs, path, name in mailbox:
            self.mailboxes[name] = (path, attrs)

        defer.returnValue(self.mailboxes)

    @defer.inlineCallbacks
    def useMailbox(self, mailbox):
        """Select an IMAP mailbox
        """
        if not self.connected:
            raise Exception("Not connected")

        if self.selected != mailbox:
            yield self.proto.select(mailbox)

    @defer.inlineCallbacks
    def findMail(self, **kw):
        """Search for a mail
        """
        if not self.connected:
            raise Exception("Not connected")

        query = imap4.Query(**kw)
        mails = yield self.proto.search(query.encode())

        defer.returnValue(mails)

    @defer.inlineCallbacks
    def getMail(self, mailid):
        """Retrieve mail body
        """
        if not self.connected:
            raise Exception("Not connected")

        mail = yield self.proto.fetchBody(str(mailid))
        defer.returnValue(mail)

    @defer.inlineCallbacks
    def deleteMail(self, mailid):
        """Delete mail
        """
        if not self.connected:
            raise Exception("Not connected")

        yield self.proto.setFlags(str(mailid), ["\\Deleted"])
        yield self.proto.expunge()

    def disconnect(self):
        """Disconnect from IMAP server
        """
        if not self.connected:
            raise Exception("Not connected")

        self.connected = False
        return self.proto.logout()
