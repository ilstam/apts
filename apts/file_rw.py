# Copyright (C) 2015 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from . import netascii
from .errors import TftpIOError


class TftpFileIO:
    block_size = 512

    def __init__(self, mode):
        self.mode = mode


class TftpFileReader(TftpFileIO):
    """
    This class is responsible for reading data from the appropriate file,
    one block at a time, taking into consideration the TFTP transfer mode.

    From outside of the class we should only call the get_next_block() method
    that will return the next 512 bytes to be send to the remote host. The rest
    of the methods are helper functions and they should not be called directly.
    """
    def __init__(self, filename, mode):
        super(TftpFileReader, self).__init__(mode)
        self._file = open(filename, mode='rb')

        # Raw bytes buffer.
        # Holds the last bytes read directly from the file in binary mode.
        self._bytes = b''

        # Netascii bytes buffer.
        # Holds the netascii bytes that didn't make it to the last sent packet
        # because of the size differences of raw bytes and netascii bytes.
        self.netascii_bytes = b''

    def get_next_block(self):
        """
        Returns the next 512 unread bytes of the file.
        These 512 bytes might not correspond to the original 512 bytes read
        from the file due to netascii conversions. However, regardless of the
        self.mode it will always return 512 bytes or less.
        """
        if self.mode == 'netascii':
            return self.get_next_block_netascii()
        if self.mode == 'octet':
            return self.get_next_block_octet()

    def read_next_bytes(self):
        """
        This method reads 512 bytes from the file and save them to the
        self._bytes variable (it doesn't return anything). If it actually read
        less than 512 bytes, it closes the file.

        Shall not be called from outside of the class.
        """
        if self._file.closed:
            raise TftpIOError("read attemption of closed file")

        self._bytes = self._file.read(self.block_size)
        if len(self._bytes) < self.block_size:
            self._file.close()

    def get_next_block_netascii(self):
        self.netascii_bytes += netascii.encode(self._bytes)
        while len(self.netascii_bytes) < self.block_size:
            try:
                self.read_next_bytes()
                self.netascii_bytes += netascii.encode(self._bytes)
            except TftpIOError:
                if self.netascii_bytes:
                    break
                raise # reraise the TftpIOError

        to_send = self.netascii_bytes[:self.block_size]
        self.netascii_bytes = self.netascii_bytes[self.block_size:]
        self._bytes = b''
        return to_send

    def get_next_block_octet(self):
        self.read_next_bytes()
        to_send = self._bytes
        self._bytes = b''
        return to_send


class TftpFileWriter(TftpFileIO):
    """
    This class is responsible for writing each block of received data on
    the appropriate file, taking into consideration the TFTP transfer mode.
    """
    def __init__(self, filename, mode):
        super(TftpFileWriter, self).__init__(mode)
        self._file = open(filename, mode='wb')

    def write_next_block(self, data):
        """
        Writes the given data to the file.
        It firstly converts them to netascii when needed. If the
        given data are less than 512 bytes, it closes the file.
        """
        if self._file.closed:
            raise TftpIOError("write attemption of closed file")

        if self.mode == 'netascii':
            self._file.write(netascii.decode(data))
        if self.mode == 'octet':
            self._file.write(data)

        if len(data) < self.block_size:
            self._file.close()
