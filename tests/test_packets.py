import struct
import unittest

from apts.packets import (RQPacket, RRQPacket, WRQPacket, DataPacket,
                          ACKPacket, ErrorPacket, PacketFactory)
from apts.errors import (DataSizeError, OpcodeExtractError, PayloadParseError,
                         InvalidOpcodeError, InvalidErrorcodeError, UnsupportedModeError)


class TestRQPacket(unittest.TestCase):
    def test_from_wire_good_input(self):
        filename, mode = ('file'.encode(), 'netascii'.encode())
        raw_data = b''.join((filename, b'\x00', mode, b'\x00'))
        packet = RQPacket.from_wire(raw_data)

        self.assertEqual(filename, packet.filename)
        self.assertEqual(mode, packet.mode)

    def test_from_wire_bad_input(self):
        raw_data = 'blahblahblahblah'.encode()

        with self.assertRaises(PayloadParseError):
            RQPacket.from_wire(raw_data)

        filename, mode = ('file'.encode(), 'nomode'.encode())
        raw_data = b''.join((filename, b'\x00', mode, b'\x00'))
        with self.assertRaises(UnsupportedModeError):
            RQPacket.from_wire(raw_data)


class TestRRQPacket(unittest.TestCase):
    def test_opcode(self):
        """
        RRQ packets opcode must be 1.
        """
        packet = RRQPacket(b'filename', b'octet')
        self.assertEqual(packet.opcode, 1)

    def test_to_wire(self):
        opcode, filename, mode = (RRQPacket.opcode, 'file'.encode(), 'octet'.encode())
        raw_data =  b''.join((struct.pack("!H", opcode), filename, b'\x00',
                             mode, b'\x00'))

        packet = RRQPacket(filename, mode)
        self.assertEqual(packet.to_wire(), raw_data)


class TestWRQPacket(unittest.TestCase):
    def test_opcode(self):
        """
        WRQ packets opcode must be 2.
        """
        packet = WRQPacket(b'filename', b'octet')
        self.assertEqual(packet.opcode, 2)

    def test_to_wire(self):
        opcode, filename, mode = (WRQPacket.opcode, 'file'.encode(), 'octet'.encode())
        raw_data =  b''.join((struct.pack("!H", opcode), filename, b'\x00',
                             mode, b'\x00'))

        packet = WRQPacket(filename, mode)
        self.assertEqual(packet.to_wire(), raw_data)


class TestDataPacket(unittest.TestCase):
    def test_opcode(self):
        """
        Data packets opcode must be 3.
        """
        packet = DataPacket(0, b'data')
        self.assertEqual(packet.opcode, 3)

    def test_from_wire_good_input(self):
        blockn, data = (7, 'non-ascii data ελληνικά'.encode())
        raw_data = b''.join((struct.pack('!H', blockn), data))
        packet = DataPacket.from_wire(raw_data)

        self.assertEqual(blockn, packet.blockn)
        self.assertEqual(data, packet.data)

    def test_from_wire_bad_input(self):
        raw_data = 'b'.encode()

        with self.assertRaises(PayloadParseError):
            DataPacket.from_wire(raw_data)

    def test_to_wire(self):
        opcode, blockn, data = (DataPacket.opcode, 7, 'data ελληνικά'.encode())
        raw_data = b''.join((struct.pack('!HH', opcode, blockn), data))

        packet = DataPacket(blockn, data)
        self.assertEqual(packet.to_wire(), raw_data)

    def test_data_length(self):
        data = ('d' * 4).encode()
        packet = DataPacket(1, data)
        self.assertTrue(packet.is_last)

        data = ('d' * 512).encode()
        packet = DataPacket(1, data)
        self.assertFalse(packet.is_last)

        with self.assertRaises(DataSizeError):
            data = ('d' * 552).encode()
            packet = DataPacket(1, data)


class TestACKPacket(unittest.TestCase):
    def test_opcode(self):
        """
        ACK packets opcode must be 4.
        """
        packet = ACKPacket(0)
        self.assertEqual(packet.opcode, 4)

    def test_from_wire(self):
        blockn = 12
        raw_data = struct.pack('!H', blockn)
        packet = DataPacket.from_wire(raw_data)

        self.assertEqual(blockn, packet.blockn)

    def test_from_wire_bad_input(self):
        raw_data = 'b'.encode()

        with self.assertRaises(PayloadParseError):
            ACKPacket.from_wire(raw_data)

    def test_to_wire(self):
        opcode, blockn = (ACKPacket.opcode, 12)
        raw_data = struct.pack('!HH', opcode, blockn)

        packet = ACKPacket(blockn)
        self.assertEqual(packet.to_wire(), raw_data)


class TestErrorPacket(unittest.TestCase):
    def test_opcode(self):
        """
        Error packets opcode must be 5.
        """
        packet = ErrorPacket(0)
        self.assertEqual(packet.opcode, 5)

    def test_from_wire_good_input(self):
        code, message = (1, 'message ελληνικά'.encode())
        raw_data = b''.join((struct.pack('!H', code), message))
        packet = ErrorPacket.from_wire(raw_data)

        self.assertEqual(code, packet.error_code)
        self.assertEqual(message, packet.error_msg)

    def test_from_wire_bad_input(self):
        raw_data = 'b'.encode()

        with self.assertRaises(PayloadParseError):
            DataPacket.from_wire(raw_data)

        code, message = (9, 'message ελληνικά'.encode())
        raw_data = b''.join((struct.pack('!H', code), message))
        with self.assertRaises(InvalidErrorcodeError):
            ErrorPacket.from_wire(raw_data)

    def test_to_wire(self):
        opcode, code, message = (ErrorPacket.opcode, 1, 'message ελληνικά'.encode())
        raw_data = b''.join((struct.pack('!HH', opcode, code), message, b'\x00'))

        packet = ErrorPacket(code, message)
        self.assertEqual(packet.to_wire(), raw_data)

    def test_message_not_provided(self):
        """
        Test that even when we do not provide an error message, the produced
        packet will have one (the default).
        """
        packet = ErrorPacket(5)
        self.assertTrue(packet.error_msg)


class TestPacketFactory(unittest.TestCase):
    def test_create_good_input(self):
        factory = PacketFactory()

        p = WRQPacket('file'.encode(), 'netascii'.encode())
        self.assertTrue(isinstance(factory.create(p.to_wire()), WRQPacket))
        p = DataPacket(4, 'data'.encode())
        self.assertTrue(isinstance(factory.create(p.to_wire()), DataPacket))
        p = ACKPacket(12)
        self.assertTrue(isinstance(factory.create(p.to_wire()), ACKPacket))
        p = ErrorPacket(1)
        self.assertTrue(isinstance(factory.create(p.to_wire()), ErrorPacket))

    def test_create_bad_input(self):
        factory = PacketFactory()

        with self.assertRaises(InvalidOpcodeError):
            factory.create('blahblahblah'.encode())

        with self.assertRaises(OpcodeExtractError):
            factory.create('b'.encode())
