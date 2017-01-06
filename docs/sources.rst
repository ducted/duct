Sources
*******

Introduction
============

Sources are Python objects which subclass :class:`duct.objects.Source`. They
are constructed with a dictionary parsed from the YAML configuration block
which defines them, and as such can read any attributes from that either
optional or mandatory.

Since sources are constructed at startup time they can retain any required
state, for example the last metric value to report rates of change or for
any other purpose. However since a Duct process might be running many checks
a source should not use an excessive amount of memory.

The `source` configuration option is passed a string representing an object
in much the same way as you would import it in a python module. The final
class name is split from this string. For example specifying::

    source: duct.sources.network.Ping

is equivalent to::

    from duct.sources.network import Ping

Writing your own sources
========================

A source class must subclass :class:`duct.objects.Source` and also
implement the interface :class:`duct.interfaces.IDuctSource`

The source must have a `get` method which returns a :class:`duct.objects.Event`
object. The Source parent class provides a helper method `createEvent` which
performs the metric level checking (evaluating the simple logical statement in
the configuration), sets the correct service name and handles prefixing service
names.

A "Hello world" source::

    from zope.interface import implementer

    from duct.interfaces import IDuctSource
    from duct.objects import Source

    @implementer(IDuctSource)
    class HelloWorld(Source):
        
        def get(self):
            return self.createEvent('ok', 'Hello world!', 0)

To hold some state, you can re-implement the `__init__` method, as long as the
arguments remain the same.

Extending the above example to create a simple flip-flop metric event::

    from zope.interface import implementer

    from duct.interfaces import IDuctSource
    from duct.objects import Source

    @implementer(IDuctSource)
    class HelloWorld(Source):
        def __init__(self, *a):
            Source.__init__(self, *a)
            self.bit = False

        def get(self):
            self.bit = not self.bit
            return self.createEvent('ok', 'Hello world!', self.bit and 0.0 or 1.0)

You could then place this in a Python module like `hello.py` and as long as it's
in the Python path for Duct it can be used as a source with `hello.HelloWorld`

A list of events can also be returned but be careful of overwhelming the output
buffer, and if you need to produce lots of metrics it may be worthwhile to
return nothing from `get` and call `self.queueBack` as needed.

Using custom sources
====================

When a source is specified, eg ::

    source: duct.sources.network.Ping

Duct will import and instantiate the `Ping` class from `duct.sources.network`.
Consequently a source can be any installed Python module.

For the sake of convenience, however, Duct also appends `/var/lib/duct` to the
Python path. This means you can easily create, test and distribute sources in that
directory.

For example, create the above `hello.py` file and place it in `/var/lib/duct` then
use the configuration ::

    source: hello.HelloWorld

You can also always submit Github pull request with sources to have them added to
Duct for others to benefit from!

Handling asynchronous tasks
===========================

Since Duct is written using the Twisted asynchronous framework, sources can
(and in most cases *must*) make full use of it to implement network checks, or
execute other processes.

The simplest example of a source which executes an external process is the
ProcessCount check::

    from zope.interface import implementer

    from twisted.internet import defer

    from duct.interfaces import IDuctSource
    from duct.objects import Source
    from duct.utils import fork

    @implementer(IDuctSource)
    class ProcessCount(Source):
        @defer.inlineCallbacks
        def get(self):
            out, err, code = yield fork('/bin/ps', args=('-e',))

            count = len(out.strip('\n').split('\n'))

            defer.returnValue(
                self.createEvent('ok', 'Process count %s' % (count), count)
            )

For more information please read the Twisted documentation at https://twistedmatrix.com/trac/wiki/Documentation

The :py:meth:`duct.utils.fork` method returns a deferred which can timeout
after a specified time.

Thinking outside the box
========================

Historically monitoring systems are poorly architected, and terribly
inflexible. To demonstrate how Duct offers a different concept
to the boring status quo it's interesting to note that there is nothing
preventing you from starting a listening service directly within a source which
processes and relays events to Riemann implementing some protocol.

Here is an example of a source which listens for TCP connections to port
8000, accepting any number on a line and passing that to the event queue::

    from twisted.internet.protocol import Factory
    from twisted.protocols.basic import LineReceiver
    from twisted.internet import reactor

    from zope.interface import implementer

    from duct.interfaces import IDuctSource
    from duct.objects import Source

    class Numbers(LineReceiver):
        def __init__(self, source):
            self.source = source

        def lineReceived(self, line):
            """
            Send any numbers received back to the Duct queue
            """
            print repr(line)
            try:
                num = float(line)
                self.source.queueBack(
                    self.source.createEvent('ok', 'Number: %s' % num, num)
                )
            except:
                pass

    class NumbersFactory(Factory):
        def __init__(self, source):
            self.source = source

        def buildProtocol(self, addr):
            return Numbers(self.source)

    @implementer(IDuctSource)
    class NumberProxy(Source):
        def startTimer(self):
            # Override starting the source timer, we don't need it
            f = NumbersFactory(self)
            reactor.listenTCP(8000, f)

        def get(self):
            # Implement the get method, but we can ignore it
            pass
