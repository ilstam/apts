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


class TftpFileIO:
    block_size = 512

    def __init__(self, mode):
        self.mode = mode


class TftpFileReader(TftpFileIO):
    def __init__(self, filename, mode):
        super(TftpFileReader, self).__init__(mode)
        self._file = open(filename, mode='rb')
        self._bytes = 0

    def read_next_bytes(self):
        b = self._file.read(self.block_size)
        if len(b) < self.block_size:
            self._file.close()
        self._bytes += b

    def get_next_block_netascii(self):
        netascii_bytes = netascii.encode(self._bytes)
        while len(netascii_bytes) < 512 and not self._file.closed:
            self.read_next_bytes()
            netascii_bytes = netascii.encode(self._bytes)

        return netascii_bytes

    def get_next_block_octet(self):
        self.read_next_bytes()
        return self._bytes

    def get_next_block(self):
        if self.mode == 'netascii':
            return self.get_next_block_netascii()
        if self.mode == 'octet':
            return self.get_next_block_octet()


class TftpFileWriter(TftpFileIO):
    def __init__(self, filename, mode):
        super(TftpFileReader, self).__init__(mode)
        self._file = open(filename, mode='wb')

    def write_next_block(self, data):
        if self.mode == 'netascii':
            self._file.write(netascii.decode(data))
        if self.mode == 'octet':
            self._file.write(data)

        if len(data) < self.block_size:
            self._file.close()
