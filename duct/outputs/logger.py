"""
.. module:: logger
   :synopsis: Output which sends events to the standard logging output

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
from twisted.python import log

from duct.objects import Output


class Logger(Output):
    """Logger output

    **Configuration arguments:**

    :param logfile: Logfile (default: Write to standard log)
    :type logfile: str
    """
    def __init__(self, *a, **kw):
        Output.__init__(self, *a, **kw)
        if self.config.get('logfile'):
            self.logfile = open(self.config.get('logfile', 'at'))
        else:
            self.logfile = None

    def stop(self):
        if self.logfile:
            self.logfile.close()

    def eventsReceived(self, events):
        """Log received events
        """
        for ev in events:
            if self.logfile:
                self.logfile.write(repr(ev) + '\n')
            else:
                log.msg(repr(ev))
