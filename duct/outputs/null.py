"""
.. module:: null
   :synopsis: Null event output. Does nothing

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
from duct.objects import Output


class Null(Output):
    """Null output throws your events away
    """
    def eventsReceived(self, events):
        return
