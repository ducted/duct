"""
.. module:: protocol
   :synopsis: SFlow protocol

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""

from duct.protocol.sflow.protocol import protocol

Sflow = protocol.Sflow
FlowSample = protocol.FlowSample
CounterSample = protocol.CounterSample
