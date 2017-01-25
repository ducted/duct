"""
.. module:: server
   :synopsis: SFlow UDP server

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task, defer
from twisted.application import service, internet
from twisted.web.client import getPage

from duct.protocol.sflow import protocol
from duct.protocol.sflow.protocol import flows, counters


class DatagramReceiver(DatagramProtocol):
    """DatagramReceiver for sFlow packets
    """
    def datagramReceived(self, data, (host, port)):
        sflow = protocol.Sflow(data, host)

        for sample in sflow.samples:
            if isinstance(sample, protocol.FlowSample):
                self.process_flow_sample(sflow, sample)

            if isinstance(sample, protocol.CounterSample):
                self.process_counter_sample(sflow, sample)

    def process_flow_sample(self, sflow, flow):
        """Process an incomming flow sample
        """
        for k, v in flow.flows.items():
            if isinstance(v, flows.HeaderSample) and v.frame:
                reactor.callLater(0, self.receive_flow, flow, v.frame,
                                  sflow.host)

    def process_counter_sample(self, sflow, counter):
        """Process an incomming counter sample
        """
        for k, v in counter.counters.items():
            if isinstance(v, counters.InterfaceCounters):
                reactor.callLater(0, self.receive_counter, v, sflow.host)

            elif isinstance(v, counters.HostCounters):
                reactor.callLater(0, self.receive_host_counter, v)

    def receive_flow(self, flow, sample):
        """Called when a flow is received
        """
        pass

    def receive_counter(self, counter):
        """Called when a counter is received
        """
        pass

    def receive_host_counter(self, counter):
        """Called when a host counter is received
        """
        pass
