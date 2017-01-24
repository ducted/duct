"""
.. module:: interfaces
   :synopsis: Generic interfaces

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

from zope.interface import Interface


# pylint: disable=E0239
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
