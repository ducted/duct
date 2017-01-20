"""
.. module:: interfaces
   :platform: Unix
   :synopsis: Generic interfaces

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

from zope.interface import Interface


class IDuctProtocol(Interface):
    """Interface for Duct client protocols"""

    def sendEvent(self, event):
        """Sends an event to this client"""
        pass

class IDuctSource(Interface):
    """Interface for Duct metric sources"""

    def get(self):
        """Return this source data"""
        pass
