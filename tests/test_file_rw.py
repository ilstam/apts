import os
import unittest
from tempfile import NamedTemporaryFile

from apts import netascii
from apts.file_rw import TftpFileReader, TftpFileWriter
from apts.errors import TftpIOError


LOREM_IPSUM = """
Line1 Lorem ipsum lorem ipsum lorem ipsum ΛΟΡΕΜ ΙΨΟΥΜ λορεμ ιψουμ
lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem
ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum
lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem
ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum
lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem
λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ
ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ
λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ ιψούμ λορέμ ιψουμ λορέμ
ιψούμ λορέμ ιψουμ λορέμ ιψούμ
""".encode()


def read_whole_file(file_reader):
    _buffer = b''
    while True:
        try:
            _buffer += file_reader.get_next_block()
        except TftpIOError:
            break

    return _buffer

def write_temp_file(data):
    """
    Write the data to a temporary file and return the name of the file.
    """
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(data)
    temp_file.close()
    return temp_file.name


class TestTftpFileReader(unittest.TestCase):
    def test_reader_netascii_mode(self):
        # test with a file of less than 512 bytes
        self._test_reader_netascii_mode(LOREM_IPSUM[300:])
        # test with a file of precisely 512 bytes
        self._test_reader_netascii_mode(LOREM_IPSUM[512:])
        # test with a file of more than 512 bytes
        self._test_reader_netascii_mode(LOREM_IPSUM)

    def test_reader_octet_mode(self):
        self._test_reader_octet_mode(LOREM_IPSUM[300:])
        self._test_reader_octet_mode(LOREM_IPSUM[512:])
        self._test_reader_octet_mode(LOREM_IPSUM)

    def test_read_from_closed_file(self):
        self._test_read_from_closed_file('netascii')
        self._test_read_from_closed_file('octet')

    def _test_read_from_closed_file(self, mode):
        """
        When trying to read from a closed file, a TftpIOError should be raised.
        """
        fname = write_temp_file(LOREM_IPSUM)
        fr = TftpFileReader(fname, mode)
        read_whole_file(fr)

        self.assertTrue(fr._file.closed)
        with self.assertRaises(TftpIOError):
            fr.get_next_block()

        os.remove(fname)

    def _test_reader_netascii_mode(self, data):
        fname = write_temp_file(data)
        fr = TftpFileReader(fname, 'netascii')
        self.assertEqual(read_whole_file(fr), netascii.encode(data))
        self.assertTrue(fr._file.closed)
        os.remove(fname)

    def _test_reader_octet_mode(self, data):
        fname = write_temp_file(data)
        fr = TftpFileReader(fname, 'octet')
        self.assertEqual(read_whole_file(fr), data)
        self.assertTrue(fr._file.closed)
        os.remove(fname)


class TestTftpFileWriter(unittest.TestCase):
    def test_writer_netascii_mode(self):
        pass

    def test_writer_octet_mode(self):
        pass
