"""
.. module:: imap4
   :platform: Unix
   :synopsis: IMAP4 protocol helper classes

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

from twisted.internet import defer, reactor, ssl, endpoints, protocol
from twisted.mail import imap4
from twisted.python import log


class IMAPClientProtocol(imap4.IMAP4Client):
    greetDeferred = None
    debug = False

    def dataReceived(self, data):
        if self.debug:
            log.msg(data)
        imap4.IMAP4Client.dataReceived(self, data)

    def serverGreeting(self, caps):
        self.serverCapabilities = caps
        if self.greetDeferred is not None:
            d, self.greetDeferred = self.greetDeferred, None
            d.callback(self)


class IMAP4ClientFactory(protocol.ClientFactory):
    usedUp = False
    protocol = IMAPClientProtocol
    debug = False

    def __init__(self, username, onConn):
        self.username = username
        self.onConn = onConn

    def buildProtocol(self, addr):
        assert not self.usedUp
        self.usedUp = True

        p = self.protocol()
        p.debug = self.debug
        p.factory = self
        p.greetDeferred = self.onConn

        p.registerAuthenticator(imap4.PLAINAuthenticator(self.username))
        p.registerAuthenticator(imap4.LOGINAuthenticator(self.username))
        p.registerAuthenticator(
                imap4.CramMD5ClientAuthenticator(self.username))

        return p

    def clientConnectionFailed(self, connector, reason):
        d, self.onConn = self.onConn, None
        d.errback(reason)


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

        d = defer.Deferred()
        factory = IMAP4ClientFactory(self.user, d)
        factory.debug = self.debug

        yield endpoint.connect(factory)
        self.proto = yield d

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
        if not self.connected:
            raise Exception("Not connected")

        if self.selected != mailbox:
            yield self.proto.select(mailbox)
    
    @defer.inlineCallbacks
    def findMail(self, **kw):
        if not self.connected:
            raise Exception("Not connected")

        q = imap4.Query(**kw)
        mails = yield self.proto.search(q.encode())

        defer.returnValue(mails)
    
    @defer.inlineCallbacks
    def getMail(self, mailid):
        if not self.connected:
            raise Exception("Not connected")

        mail = yield self.proto.fetchBody(str(mailid))
        defer.returnValue(mail)

    @defer.inlineCallbacks
    def deleteMail(self, mailid):
        if not self.connected:
            raise Exception("Not connected")

        yield self.proto.setFlags(str(mailid), ["\\Deleted"])
        yield self.proto.expunge()

    def disconnect(self):
        if not self.connected:
            raise Exception("Not connected")

        self.connected = False
        return self.proto.logout()
