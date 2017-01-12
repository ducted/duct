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
        self.t.stop()
        self.logfile.close()

    def sendEvents(self, events):
        for e in events:
            if self.logfile:
                self.logfile.write(repr(e) + '\n')
            else:
                log.msg(repr(e))
