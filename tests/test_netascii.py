import unittest

from apts import netascii


class TestNetascii(unittest.TestCase):
    def test_lf_and_cr_values(self):
        """
        Netascii line feed should always be ascii CR+LF, and carriage return
        should always be ascii CR+NUL.
        """
        self.assertEqual(netascii.LF, b'\x0d\x0a')
        self.assertEqual(netascii.CR, b'\x0d\x00')

    def test_encode(self):
        self.assertEqual(netascii.encode('data'.encode()), 'data'.encode())
        self.assertEqual(netascii.encode('da\nta'.encode()),
                                        b'da' + b'\x0d\x0a' + b'ta')
        self.assertEqual(netascii.encode('da\rta'.encode()),
                                        b'da' + b'\x0d\x00' + b'ta')
        self.assertEqual(netascii.encode('da\r\nta'.encode()),
                                        b'da' + b'\x0d\x00\x0d\x0a' + b'ta')
        self.assertEqual(netascii.encode('da\n\rta'.encode()),
                                        b'da' + b'\x0d\x0a\x0d\x00' + b'ta')

    def test_decode(self):
        self.assertEqual(netascii.decode('data'.encode()), 'data'.encode())
        self.assertEqual(netascii.decode(b'da' + b'\x0d\x0a' + b'ta'),
                                        'da\nta'.encode())
        self.assertEqual(netascii.decode(b'da' + b'\x0d\x00' + b'ta'),
                                         'da\rta'.encode())
        self.assertEqual(netascii.decode(b'da' + b'\x0d\x00\x0d\x0a' + b'ta'),
                                         'da\r\nta'.encode())
        self.assertEqual(netascii.decode(b'da' + b'\x0d\x0a\x0d\x00' + b'ta'),
                                         'da\n\rta'.encode())
