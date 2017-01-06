"""Duct - A monitoring agent

.. moduleauthor:: Colin Alston <colin@imcol.in>

"""

from duct import service

def makeService(config):
    # Create DuctService
    return service.DuctService(config)
