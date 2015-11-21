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
    def __init__(self, filename, mode):
        super(TftpFileReader, self).__init__(mode)
        self._file = open(filename, mode='rb')
        self._bytes = b''

    def read_next_bytes(self):
        if self._file.closed:
            raise TftpIOError("read attemption of closed file")

        b = self._file.read(self.block_size)
        if len(b) < self.block_size:
            self._file.close()
        self._bytes += b

    def get_next_block_netascii(self):
        netascii_bytes = netascii.encode(self._bytes)
        while len(netascii_bytes) < self.block_size:
            try:
                self.read_next_bytes()
                netascii_bytes = netascii.encode(self._bytes)
            except TftpIOError:
                break

        to_send = netascii_bytes[:self.block_size]
        self._bytes = self._bytes[self.block_size:]
        return to_send

    def get_next_block_octet(self):
        self.read_next_bytes()
        to_send = self._bytes
        self._bytes = b''
        return to_send

    def get_next_block(self):
        if self._file.closed:
            raise TftpIOError("read attemption of closed file")

        if self.mode == 'netascii':
            return self.get_next_block_netascii()
        if self.mode == 'octet':
            return self.get_next_block_octet()


class TftpFileWriter(TftpFileIO):
    def __init__(self, filename, mode):
        super(TftpFileWriter, self).__init__(mode)
        self._file = open(filename, mode='wb')

    def write_next_block(self, data):
        if self._file.closed:
            raise TftpIOError("write attemption of closed file")

        if self.mode == 'netascii':
            self._file.write(netascii.decode(data))
        if self.mode == 'octet':
            self._file.write(data)

        if len(data) < self.block_size:
            self._file.close()
