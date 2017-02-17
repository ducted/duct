"""
.. module:: objects
   :synopsis: Base classes for sources, outputs, and event objects

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import hashlib
import time
import socket
import traceback

from twisted.internet import task, defer
from twisted.python import log

from duct.utils import fork
from duct.protocol import ssh


class Event(object):
    """Duct Event object

    All sources pass these to the queue, which form a proxy object
    to create protobuf Event objects

    :param state: Some sort of string < 255 chars describing the state
    :param service: The service name for this event
    :param description: A description for the event, ie. "My house is on fire!"
    :param metric: int or float metric for this event
    :param ttl: TTL (time-to-live) for this event
    :param tags: List of tag strings
    :param hostname: Hostname for the event (defaults to system fqdn)
    :param aggregation: Aggregation function
    :param attributes: A dictionary of key/value attributes for this event
    :param evtime: Event timestamp override
    """
    def __init__(
            self,
            state,
            service,
            description,
            metric,
            ttl,
            tags=None,
            hostname=None,
            aggregation=None,
            evtime=None,
            attributes=None,
            evtype='metric'):
        self.state = state
        self.service = service
        self.description = description
        self.metric = metric
        self.ttl = ttl
        self.tags = tags if tags is not None else []
        self.attributes = attributes
        self.aggregation = aggregation
        self.evtype = evtype

        if evtime:
            self.time = evtime
        else:
            self.time = time.time()
        if hostname:
            self.hostname = hostname
        else:
            self.hostname = socket.gethostbyaddr(socket.gethostname())[0]

    def eid(self):
        """Return a unique identifier for this event
        """
        return self.hostname + '.' + self.service

    def __repr__(self):
        ser = ['%s=%s' % (key, repr(val)) for key, val in dict(self).items()]

        return "<Event %s>" % (', '.join(ser))

    def __iter__(self):
        obj = {
            'hostname': self.hostname,
            'state': self.state,
            'service': self.service,
            'metric': self.metric,
            'ttl': self.ttl,
            'tags': self.tags,
            'time': self.time,
            'type': self.evtype,
            'description': self.description,
        }

        if self.attributes:
            obj['attributes'] = self.attributes

        for key, val in obj.items():
            yield key, val

    def copyWithMetric(self, metric):
        """Create a copy of this event with a different metric value
        """
        return Event(self.state, self.service, self.description, metric,
                     self.ttl, self.tags, self.hostname, self.aggregation)

class Output(object):
    """Output parent class

    Outputs can inherit this object which provides a construct
    for a working output

    :param config: Dictionary config for this queue (usually read from the
             yaml configuration)
    :param duct: A DuctService object for interacting with the queue manager
    """
    def __init__(self, config, duct):
        self.config = config
        self.duct = duct
        self.events = []
        self.maxsize = 0

    def createClient(self):
        """Deferred which sets up the output
        """
        pass

    def eventsReceived(self, events):
        """Receives a list of events and queues them

        Arguments:
        events -- list of `duct.objects.Event`
        """
        # Make sure queue isn't oversized
        if self.maxsize > 0:
            if (self.maxsize < 1) or (len(self.events) < self.maxsize):
                self.events.extend(events)
        else:
            self.events.extend(events)

    def stop(self):
        """Called when the service shuts down
        """
        pass

class Source(object):
    """Source parent class

    Sources can inherit this object which provides a number of
    utility methods.

    :param config: Dictionary config for this queue (usually read from the
             yaml configuration)
    :param queueBack: A callback method to recieve a list of Event objects
    :param duct: A DuctService object for interacting with the queue manager
    """

    sync = False
    ssh = False

    def __init__(self, config, queueBack, duct):
        self.config = config
        self.duct = duct

        self.timer = task.LoopingCall(self.tick)
        self.timerDeferred = None
        self.attributes = None

        self.service = config['service']
        self.inter = float(config.get('interval', duct.inter))
        self.ttl = float(config.get('ttl', duct.ttl))

        if 'tags' in config:
            self.tags = [tag.strip() for tag in config['tags'].split(',')]
        else:
            self.tags = []

        attributes = config.get("attributes")
        if isinstance(attributes, dict):
            self.attributes = attributes

        self.hostname = config.get('hostname')
        if self.hostname is None:
            self.hostname = socket.gethostbyaddr(socket.gethostname())[0]

        self.use_ssh = config.get('use_ssh', False)

        if self.use_ssh:
            self._init_ssh()

        self.queueBack = self._queueBack(queueBack)

        self.running = False

    def _init_ssh(self):
        """ Configure SSH client options
        """

        self.ssh_host = self.config.get('ssh_host', self.hostname)

        self.known_hosts = self.config.get(
            'ssh_knownhosts_file',
            self.duct.config.get('ssh_knownhosts_file', None)
        )

        self.ssh_keyfile = self.config.get(
            'ssh_keyfile', self.duct.config.get('ssh_keyfile', None))

        self.ssh_key = self.config.get(
            'ssh_key', self.duct.config.get('ssh_key', None))

        # Not sure why you'd bother but maybe you've got a weird policy
        self.ssh_keypass = self.config.get(
            'ssh_keypass', self.duct.config.get('ssh_keypass', None))

        self.ssh_user = self.config.get(
            'ssh_username', self.duct.config.get('ssh_username', None))

        self.ssh_password = self.config.get(
            'ssh_password', self.duct.config.get('ssh_password', None))

        self.ssh_port = self.config.get(
            'ssh_port', self.duct.config.get('ssh_port', 22))

        # Verify config to see if we're good to go

        if not (self.ssh_key or self.ssh_keyfile or self.ssh_password):
            raise Exception("To use SSH you must specify *one* of ssh_key,"
                            " ssh_keyfile or ssh_password for this source"
                            " check or globally")

        if not self.ssh_user:
            raise Exception("ssh_username must be set")

        self.ssh_keydb = []

        cHash = hashlib.sha1(
            ':'.join((
                self.ssh_host, self.ssh_user, str(self.ssh_port),
                str(self.ssh_password), str(self.ssh_key),
                str(self.ssh_keyfile)
            )).encode()).hexdigest()

        if cHash in self.duct.hostConnectorCache:
            self.ssh_client = self.duct.hostConnectorCache.get(cHash)
            self.ssh_connector = False
        else:
            self.ssh_connector = True
            self.ssh_client = ssh.SSHClient(self.ssh_host, self.ssh_user,
                                            self.ssh_port,
                                            password=self.ssh_password,
                                            knownhosts=self.known_hosts)

            if self.ssh_keyfile:
                self.ssh_client.addKeyFile(self.ssh_keyfile, self.ssh_keypass)

            if self.ssh_key:
                self.ssh_client.addKeyString(self.ssh_key, self.ssh_keypass)

            self.duct.hostConnectorCache[cHash] = self.ssh_client

    def _queueBack(self, caller):
        return lambda events: caller(self, events)

    def start(self):
        """Called when source is started
        """
        pass

    @defer.inlineCallbacks
    def startTimer(self):
        """Starts the timer for this source"""
        yield defer.maybeDeferred(self.start)

        self.timerDeferred = self.timer.start(self.inter)

        if self.use_ssh and self.ssh_connector:
            yield defer.maybeDeferred(self.ssh_client.connect)


    def stop(self):
        """Called when source is stopped
        """
        pass

    def stopTimer(self):
        """Stops the timer for this source"""
        self.timerDeferred = None
        if self.timer.running:
            self.timer.stop()
        return defer.maybeDeferred(self.stop)

    def fork(self, *a, **kw):
        """Wrapper function to execute another process

           Passes off to either ssh or local system based on whether
           use_ssh is set
        """
        if self.use_ssh:
            return self.ssh_client.fork(*a, **kw)
        else:
            return fork(*a, **kw)

    @defer.inlineCallbacks
    def _get(self):
        if self.use_ssh and not self.ssh:
            event = yield defer.maybeDeferred(self.sshGet)

        else:
            event = yield defer.maybeDeferred(self.get)

        if self.config.get('debug', False):
            log.msg("[%s] Tick: %s" % (self.config['service'], event))

        defer.returnValue(event)

    @defer.inlineCallbacks
    def tick(self):
        """Called for every timer tick. Calls self.get which can be a deferred
        and passes that result back to the queueBack method

        Returns a deferred"""

        if self.sync:
            if self.running:
                defer.returnValue(None)

        self.running = True

        try:
            event = yield self._get()
            if event:
                self.queueBack(event)

        except Exception as ex:
            if self.duct.config.get('debug'):
                tb_lines = traceback.format_exc().splitlines()
                header = "[%s] Unhandled error: %%s" % (self.service)
                log.msg(header % tb_lines[0])
                if len(tb_lines) > 1:
                    for l in tb_lines[1:]:
                        log.msg(l)

            else:
                log.msg("[%s] Unhandled error: %s" % (self.service, ex))

        self.running = False

    def createEvent(self, state, description, metric, prefix=None,
                    hostname=None, aggregation=None, evtime=None, attributes=None):
        """Creates an Event object from the Source configuration"""
        if prefix:
            service_name = self.service + "." + prefix
        else:
            service_name = self.service

        return Event(state, service_name, description, metric, self.ttl,
                     hostname=hostname or self.hostname,
                     aggregation=aggregation,
                     evtime=evtime, tags=self.tags, attributes=attributes)

    def createLog(self, evtype, data, evtime=None, hostname=None):
        """Creates an Event object from the Source configuration"""

        return Event(None, evtype, data, 0, self.ttl,
                     hostname=hostname or self.hostname, evtime=evtime,
                     tags=self.tags, evtype='log')

    def get(self):
        """Get method for source called every `self.inter`
           Should return a list of `Event` objects or `None`
        """
        raise NotImplementedError()

    def sshGet(self):
        """Get method for source if use_ssh is enabled
        """
        raise NotImplementedError(
            "This source does not implement SSH remote checks")
