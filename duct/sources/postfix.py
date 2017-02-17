"""
.. module:: postfix
   :platform: Unix
   :synopsis: A source module for postfix stats

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

import os

from zope.interface import implementer

from twisted.internet import defer
from twisted.python import log

from duct.interfaces import IDuctSource
from duct.objects import Source
from duct.aggregators import Counter


@implementer(IDuctSource)
class Postfix(Source):
    """Postfix checks

    **Configuration arguments:**

    :param spool: Postfix spool directory (default: /var/spool/postfix)
    :type spool: str.

    **Metrics:**

    :(service_name):
    :(service_name):
    :(service_name):
    :(service_name):
    :(service_name):
    :(service_name):
    :(service_name):
    """
    ssh = True

    def __init__(self, *a, **kw):
        Source.__init__(self, *a, **kw)

        self.spool = self.config.get('spool', '/var/spool/postfix')
        self.paths = ['active', 'deferred', 'maildrop', 'incoming', 'corrupt',
                      'hold', 'bounce']

    @defer.inlineCallbacks
    def get(self):
        events = []
        for queue in self.paths:
            abspath = os.path.join(self.spool, queue)

            out, err, code = yield self.fork(
                '/bin/sh',
                args=('-c',
                      '"/bin/find %s -type f | /usr/bin/wc -l"' % abspath,)
            )

            if code == 0:
                val = int(out.strip('\n'))

                events.extend([
                    self.createEvent('ok', 'postfix queue length', val,
                                     attributes={
                                         'queue': queue,
                                     })
                ])

            else:
                log.msg('Error running %s' % repr(err))
        defer.returnValue(events)
