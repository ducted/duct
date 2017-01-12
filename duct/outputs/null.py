from twisted.python import log

from duct.objects import Output

class Null(Output):
    """Null output
    Throw your events away

    **Configuration arguments:**

    """
    def eventsReceived(self, events):
        return 
