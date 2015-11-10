import os
import unittest

from apts.netascii import LF, CR, encode as net_enc, decode as net_dec

COS_LF  = os.linesep # line seperator of the current OS
WIN_LF  = '\r\n'     # line seperator of MS Windows
UNIX_LF = '\n'       # line seperator of Unix-like systems (Linux, *BSD, OS X)


class TestNetascii(unittest.TestCase):
    def test_lf_and_cr_values(self):
        """
        Netascii line feed should always be ascii CR+LF, and carriage return
        should always be ascii CR+NUL.
        """
        self.assertEqual(LF, b'\x0d\x0a')
        self.assertEqual(CR, b'\x0d\x00')

    def test_encode_on_different_OSes(self):
        """
        Test the netascii encode function with line seperators of different OSes.
        """
        self._test_encode(COS_LF)
        self._test_encode(UNIX_LF)
        self._test_encode(WIN_LF)

    def test_decode_on_different_OSes(self):
        """
        Test the netascii decode function with line seperators of different OSes.
        """
        self._test_decode(COS_LF)
        self._test_decode(UNIX_LF)
        self._test_decode(WIN_LF)

    def _test_encode(self, linesep):
        self.assertEqual(net_enc('data'.encode(), linesep), 'data'.encode())
        self.assertEqual(net_enc('da\rta'.encode(), linesep), b'da' + CR + b'ta')
        self.assertEqual(net_enc('da{0}ta'.format(linesep).encode(), linesep),
                                        b'da' + LF + b'ta')
        self.assertEqual(net_enc('da\r{0}ta'.format(linesep).encode(), linesep),
                                        b'da' + CR + LF + b'ta')
        self.assertEqual(net_enc('da{0}\rta'.format(linesep).encode(), linesep),
                                        b'da' + LF + CR + b'ta')

    def _test_decode(self, linesep):
        self.assertEqual(net_dec('data'.encode(), linesep), 'data'.encode())
        self.assertEqual(net_dec(b'da' + CR + b'ta', linesep), 'da\rta'.encode())
        self.assertEqual(net_dec(b'da' + LF + b'ta', linesep),
                                        'da{0}ta'.format(linesep).encode())
        self.assertEqual(net_dec(b'da' + CR + LF + b'ta', linesep),
                                         'da\r{0}ta'.format(linesep).encode())
        self.assertEqual(net_dec(b'da' + LF + CR + b'ta', linesep),
                                         'da{0}\rta'.format(linesep).encode())
