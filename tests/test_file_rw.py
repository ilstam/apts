import os
import math
import random
import string
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
        self._test_writer_netascii_mode(netascii.encode(LOREM_IPSUM[300:]))
        self._test_writer_netascii_mode(netascii.encode(LOREM_IPSUM[512:]))
        self._test_writer_netascii_mode(netascii.encode(LOREM_IPSUM))

    def test_writer_octet_mode(self):
        self._test_writer_octet_mode(LOREM_IPSUM[300:])
        self._test_writer_octet_mode(LOREM_IPSUM[512:])
        self._test_writer_octet_mode(LOREM_IPSUM)

    def test_write_to_closed_file(self):
        self._test_write_to_closed_file('netascii')
        self._test_write_to_closed_file('octet')

    def _test_write_to_closed_file(self, mode):
        """
        When trying to write to a closed file, a TftpIOError should be raised.
        """
        fname = get_random_filename()
        fw = TftpFileWriter(fname, mode)
        if mode == 'netascii':
            write_whole_file(fw, netascii.decode(LOREM_IPSUM))
        elif mode == 'octet':
            write_whole_file(fw, LOREM_IPSUM)
        self.assertTrue(fw._file.closed)

        with self.assertRaises(TftpIOError):
            fw.write_next_block('data'.encode())

    def _test_writer_netascii_mode(self, data):
        fname = get_random_filename()
        fw = TftpFileWriter(fname, 'netascii')
        write_whole_file(fw, data)
        self.assertTrue(fw._file.closed)

        with open(fname, mode='rb') as f:
            _buffer = f.read()

        self.assertEqual(_buffer, netascii.decode(data))

    def _test_writer_octet_mode(self, data):
        fname = get_random_filename()
        fw = TftpFileWriter(fname, 'octet')
        write_whole_file(fw, data)
        self.assertTrue(fw._file.closed)

        with open(fname, mode='rb') as f:
            _buffer = f.read()

        self.assertEqual(_buffer, data)


def read_whole_file(file_reader):
    _buffer = b''
    while True:
        try:
            _buffer += file_reader.get_next_block()
        except TftpIOError:
            break

    return _buffer

def write_whole_file(file_reader, data):
    iterations = math.ceil((len(data) + 1) / file_reader.block_size)
    for _ in range(iterations):
        file_reader.write_next_block(data[:file_reader.block_size])
        data = data[file_reader.block_size:]

def write_temp_file(data):
    """
    Write the data to a temporary file and return the name of the file.
    """
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(data)
    temp_file.close()
    return temp_file.name

def get_random_string(n=10):
    """
    Returns a string consisting of n random ascii letters and digits.
    """
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(n))

def get_random_filename(folder='/tmp/'):
    """
    Returns the path of a file inside folder. The filename is random and it
    doesn't already exists in the OS directory tree.
    """
    fname = os.path.join(folder, get_random_string())
    while os.path.exists(fname):
        fname = os.path.join(folder, get_random_string())
    return fname
