"""
.. module:: mail
   :platform: Unix
   :synopsis: A source module for mailserver tests

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
# pylint: disable=C0413,E0611,E0401
import time
import uuid
import sys

if sys.version_info > (3, 0):
    raise Exception("Mail checks are not yet available on Python 3")

from email.mime.text import MIMEText

from zope.interface import implementer

from twisted.internet import defer
from twisted.mail.smtp import sendmail
from twisted.python import log

from duct.interfaces import IDuctSource
from duct.objects import Source

from duct.protocol import imap4


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
        """Send an email with a unique ID
        """
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


        mail_id = uuid.uuid4().hex.decode()
        message = MIMEText("Duct email test: %s" % mail_id)
        message['Subject'] = "Duct check %s" % mail_id
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

        defer.returnValue((elapsed, info, state, mail_id))

    @defer.inlineCallbacks
    def get(self):
        elapsed, info, state, _ = yield self.sendMail()
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

    :param mail_type: pop3 or imap (default: imap)
    :type mail_type: str.
    :param mail_server: POP3/IMAP server (default: `hostname`)
    :type mail_server: str.
    :param mail_port: POP3/IMAP port (default: standard port)
    :type mail_port: int.
    :param mail_username: POP3/IMAP username (required)
    :type mail_username: str.
    :param mail_password: POP3/IMAP password (required)
    :type mail_password: str.
    :param mail_ssl: Use SSL/TLS for POP3/IMAP (default: False)
    :type mail_ssl: bool.
    :param imap_mailbox: Mailbox to check for IMAP (default: INBOX)
    :type imap_mailbox: str.
    :param max_time: Max time to wait for delivery in seconds (default: 60)
    :type max_time: int.

    **Metrics:**

    :(service name).latency: Time to complete request
    """

    def __init__(self, *a, **kw):
        SMTP.__init__(self, *a, **kw)
        if 'smtp_server' in self.config:
            self.config['server'] = self.config['smtp_server']

        if 'smtp_port' in self.config:
            self.config['port'] = int(self.config['smtp_port'])

        self.max_time = int(self.config.get('max_time', 60))

        self.mail_type = self.config.get('mail_type', 'imap')

        self.mail_server = self.config.get('mail_server', self.hostname)
        self.mail_ssl = self.config.get('mail_ssl', False)

        self.username = self.config['mail_username']
        self.password = self.config['mail_password']

        self.imapClient = None

        self.sent = None

        if self.mail_type == 'imap':
            self.mailbox = self.config.get('imap_mailbox', 'INBOX')
            if self.mail_ssl:
                self.mail_port = self.config.get('mail_port', 993)
            else:
                self.mail_port = self.config.get('mail_port', 143)
        elif self.mail_type == 'pop3':
            if self.mail_ssl:
                self.mail_port = self.config.get('mail_port', 995)
            else:
                self.mail_port = self.config.get('mail_port', 110)
        else:
            raise Exception("Unsupported mailserver type '%s'" % self.mail_type)

    @defer.inlineCallbacks
    def connectImap(self):
        """Connect to IMAP server
        """
        if not self.imapClient:
            self.imapClient = imap4.IMAPClient(self.mail_server, self.mail_port,
                                               self.username, self.password,
                                               ssl=self.mail_ssl)

        if not self.imapClient.connected:

            yield self.imapClient.connect()

            mailboxes = yield self.imapClient.getMailboxes()

            if self.mailbox in mailboxes:
                yield self.imapClient.useMailbox(self.mailbox)
            else:
                log.msg("Can't find mailbox %s" % self.mailbox)

    def stop(self):
        yield self.imapClient.disconnect()

    @defer.inlineCallbacks
    def get(self):
        events = []
        if not self.sent:
            today = time.strftime('%d-%b-%Y')
            elapsed, info, state, uid = yield self.sendMail()
            events.append(self.createEvent(state,
                                           info, elapsed, prefix='smtp'))

            if state == 'ok':
                self.sent = (uid, today, elapsed, time.time())

        else:
            try:
                yield self.connectImap()
                events.append(self.createEvent('ok',
                                               'IMAP OK', 1, prefix='imap'))
            except:
                events.append(self.createEvent('critical',
                                               'Could not connect to IMAP', 0,
                                               prefix='imap'))
                defer.returnValue(events)

            uid, today, elapsed, t = self.sent

            mailnum = yield self.imapClient.findMail(
                subject="Duct check %s" % uid,
                since=today
            )

            if mailnum:
                mail = yield self.imapClient.getMail(mailnum[0])

                body = mail.get(mailnum[0])
                if body:
                    body = body.values()[0]
                    expected = 'Duct email test: %s' % uid
                    if expected in body:
                        round_trip = (time.time() - t) + elapsed
                        events.append(self.createEvent('ok',
                                                       'Mail delivery RTT',
                                                       round_trip,
                                                       prefix='delivery'))
                        self.sent = None

                yield self.imapClient.deleteMail(mailnum[0])
            yield self.imapClient.disconnect()

            if self.sent and ((time.time() - t) > self.max_time):
                # Stil waiting after max_time, so give up and raise error
                events.append(self.createEvent('critical',
                                               'Mail delivery failed',
                                               time.time() - t,
                                               prefix='delivery'))

                self.sent = None

        defer.returnValue(events)
