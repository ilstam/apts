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

    def test_from_netascii(self):
        pass

    def test_to_netascii(self):
        pass
