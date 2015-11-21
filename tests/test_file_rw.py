import unittest
from tempfile import NamedTemporaryFile

from apts import netascii
from apts.file_rw import TftpFileReader
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
        data = LOREM_IPSUM[300:]
        fr = TftpFileReader(write_temp_file(data), 'netascii')
        self.assertEqual(read_whole_file(fr), netascii.encode(data))

        # test with a file of precisely 512 bytes
        data = LOREM_IPSUM[512:]
        fr = TftpFileReader(write_temp_file(data), 'netascii')
        self.assertEqual(read_whole_file(fr), netascii.encode(data))

        # test with a file of more than 512 bytes
        data = LOREM_IPSUM
        fr = TftpFileReader(write_temp_file(data), 'netascii')
        self.assertEqual(read_whole_file(fr), netascii.encode(data))

    def test_reader_octet_mode(self):
        # test with a file of less than 512 bytes
        data = LOREM_IPSUM[300:]
        fr = TftpFileReader(write_temp_file(data), 'octet')
        self.assertEqual(read_whole_file(fr), data)

        # test with a file of precisely 512 bytes
        data = LOREM_IPSUM[512:]
        fr = TftpFileReader(write_temp_file(data), 'octet')
        self.assertEqual(read_whole_file(fr), data)

        # test with a file of more than 512 bytes
        data = LOREM_IPSUM
        fr = TftpFileReader(write_temp_file(data), 'octet')
        self.assertEqual(read_whole_file(fr), data)
