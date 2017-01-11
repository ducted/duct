"""
.. module:: network
   :platform: Unix
   :synopsis: A source module for network checks

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import time
import uuid

from email.mime.text import MIMEText

from twisted.internet import defer
from twisted.mail.smtp import sendmail
from twisted.mail import imap4
from twisted.python import log

from zope.interface import implementer

from duct.interfaces import IDuctSource
from duct.objects import Source
from duct.protocol import icmp
from duct.utils import HTTPRequest, Timeout


class IMAP4Client(imap4.IMAP4Client):
    """
    A client with callbacks for greeting messages from an IMAP server.
    """
    greetDeferred = None

    def serverGreeting(self, caps):
        self.serverCapabilities = caps
        if self.greetDeferred is not None:
            d, self.greetDeferred = self.greetDeferred, None
            d.callback(self)


class IMAP4ClientFactory(protocol.ClientFactory):
    usedUp = False
    protocol = SimpleIMAP4Client

    def __init__(self, username, onConn):
        self.username = username
        self.onConn = onConn

    def buildProtocol(self, addr):
        assert not self.usedUp
        self.usedUp = True

        p = self.protocol()
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


@implementer(IDuctSource)
class SMTP(Source):
    """SMTP check

    **Configuration arguments:**
    
    :param server: SMTP server (default: `hostname`)
    :type server: str.
    :param port: SMTP port (default: 25)
    :type port: int.
    :param use_tls: Ensure TLS
    :type use_tls: bool.
    :param ehlo: EHLO name (default: `hostname`)
    :type ehlo: str.
    :param from: FROM address (default: 'Tensor <tensor@`hostname`>')
    :type from: str.
    :param to: TO address (default: 'Tensor <tensor@`server`>')
    :type to: str.
    :param username: Username (optional)
    :type username: str.
    :param password: Password (optional)
    :type password: str.
    **Metrics:**

    :(service name).latency: Time to complete request
    """

    @defer.inlineCallbacks
    def sendMail(self):
        server = self.config.get('server', self.hostname)
        m_from = self.config.get('from', 'Tensor <tensor@%s>' % self.hostname)
        m_to = self.config.get('to', 'Tensor <tensor@%s>' % server)
        port = self.config.get('port', 25)
        password = self.config.get('password', None)
        username = self.config.get('username', None)
        ehlo = self.config.get('ehlo', self.hostname)
        tls = self.config.get('use_tls', False)
        if username and password:
            auth = True
        else:
            auth = False


        id = uuid.uuid4().hex.decode()
        message = MIMEText("Duct email test: %s" % id)
        message['Subject'] = "Duct check %s" % id
        message['From'] = m_from
        message['To'] = m_to

        e_from = m_from.split('<')[1].split('>')[0]
        e_to = m_to.split('<')[1].split('>')[0]

        start_time = time.time()
        try:
            d = yield sendmail(server, e_from, e_to, message, port=port,
                               username=username, password=password,
                               senderDomainName=ehlo,
                               requireAuthentication=auth,
                               requireTransportSecurity=tls)
            info = "Email check result: %s" % d[1][0][2]
            state = 'ok'
        except Exception as e:
            state = 'critical'
            info = repr(e)
            log.msg('Error sending mail %s' % info)

        elapsed = time.time() - start_time

        defer.returnValue((elapsed, info, state, id))

    @defer.inlineCallbacks
    def get(self):
        elapsed, info, state, id = yield self.sendMail()
        defer.returnValue([
           self.createEvent(state, info, elapsed)
        ])


class RoundTrip(SMTP):
    """Mail round-trip check
    Sends an email and checks to see if it was delivered somewhere

    **Configuration arguments:**
    
    :param smtp_server: SMTP server
    :type smtp_server: str.
    :param smtp_port: SMTP port (default: 25)
    :type smtp_port: int.
    :param use_tls: Ensure TLS
    :type use_tls: bool.
    :param ehlo: EHLO name (default: `hostname`)
    :type ehlo: str.
    :param from: FROM address (default: 'Tensor <tensor@`hostname`>')
    :type from: str.
    :param to: TO address (default: 'Tensor <tensor@`server`>')
    :type to: str.
    :param username: Username (optional)
    :type username: str.
    :param password: Password (optional)
    :type password: str.

    :param mail_type: pop3 or imap
    :type mail_type: str.
    :param mail_server: POP3/IMAP server
    :type mail_server: str.
    :param mail_port: POP3/IMAP port
    :type mail_port: str.
    :param mail_username: POP3/IMAP username
    :type mail_username: str.
    :param mail_password: POP3/IMAP password
    :type mail_password: str.
    :param mail_ssl: Use SSL/TLS for POP3/IMAP
    :type mail_ssl: bool.

    **Metrics:**

    :(service name).latency: Time to complete request
    """

    def __init__(self, *a, **kw):
        SMTP.__init__(self, *a, **kw)
        if 'smtp_server' in self.config:
            self.config['server'] = self.config['smtp_server']

        if 'smtp_port' in self.config:
            self.config['server'] = self.config['smtp_port']
        
    def checkImap(self, id):
        

    @defer.inlineCallbacks
    def get(self):
        elapsed, info, state, id = yield self.sendMail()

        yield self.checkImap(id)
