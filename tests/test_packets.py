import unittest

from apts import packets


class TestRQPacket(unittest.TestCase):
    pass


class TestRRQPacket(unittest.TestCase):
    def test_opcode(self):
        """
        RRQ packets opcode must be 1.
        """
        packet = packets.RRQPacket(b'filename', b'octet')
        self.assertEqual(packet.opcode, 1)


class TestWRQPacket(unittest.TestCase):
    def test_opcode(self):
        """
        WRQ packets opcode must be 2.
        """
        packet = packets.WRQPacket(b'filename', b'octet')
        self.assertEqual(packet.opcode, 2)


class TestDataPacket(unittest.TestCase):
    def test_opcode(self):
        """
        Data packets opcode must be 3.
        """
        packet = packets.DataPacket(0, b'data')
        self.assertEqual(packet.opcode, 3)


class TestACKPacket(unittest.TestCase):
    def test_opcode(self):
        """
        ACK packets opcode must be 4.
        """
        packet = packets.ACKPacket(0)
        self.assertEqual(packet.opcode, 4)


class TestErrorPacket(unittest.TestCase):
    def test_opcode(self):
        """
        Error packets opcode must be 5.
        """
        packet = packets.ErrorPacket(0)
        self.assertEqual(packet.opcode, 5)
