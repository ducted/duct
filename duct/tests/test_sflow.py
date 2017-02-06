from twisted.trial import unittest
from twisted.internet import defer

from duct.protocol.sflow import protocol

from duct.tests import globs


class Test(unittest.TestCase):
    def test_decode(self):
        proto = protocol.Sflow(globs.SFLOW_PACKET, '172.30.0.5')

        self.assertTrue(proto.version == 5)

        self.assertTrue(len(proto.samples) == 5)
