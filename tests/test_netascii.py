import os
import unittest

from apts import netascii

LF = netascii.LF
CR = netascii.CR
OSLF = os.linesep # os-specific newline


class TestNetascii(unittest.TestCase):
    def test_lf_and_cr_values(self):
        """
        Netascii line feed should always be ascii CR+LF, and carriage return
        should always be ascii CR+NUL.
        """
        self.assertEqual(LF, b'\x0d\x0a')
        self.assertEqual(CR, b'\x0d\x00')

    def test_encode(self):
        self.assertEqual(netascii.encode('data'.encode()), 'data'.encode())
        self.assertEqual(netascii.encode('da\rta'.encode()), b'da' + CR + b'ta')
        self.assertEqual(netascii.encode('da{0}ta'.format(OSLF).encode()),
                                        b'da' + LF + b'ta')
        self.assertEqual(netascii.encode('da\r{0}ta'.format(OSLF).encode()),
                                        b'da' + CR + LF + b'ta')
        self.assertEqual(netascii.encode('da{0}\rta'.format(OSLF).encode()),
                                        b'da' + LF + CR + b'ta')

    def test_decode(self):
        self.assertEqual(netascii.decode('data'.encode()), 'data'.encode())
        self.assertEqual(netascii.decode(b'da' + CR + b'ta'), 'da\rta'.encode())
        self.assertEqual(netascii.decode(b'da' + LF + b'ta'),
                                        'da{0}ta'.format(OSLF).encode())
        self.assertEqual(netascii.decode(b'da' + CR + LF + b'ta'),
                                         'da\r{0}ta'.format(OSLF).encode())
        self.assertEqual(netascii.decode(b'da' + LF + CR + b'ta'),
                                         'da{0}\rta'.format(OSLF).encode())
