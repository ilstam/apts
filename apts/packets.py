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

import struct


class TftpPacket:
    """
    Represents a TFTP packet.
    All TFTP packets should inherit from this class and it may not be
    instantiated directly.
    """
    opcode = -1
    seperator = b'\x00'

    @classmethod
    def from_wire(cls, payload):
        """
        Creates a TftpPacket object by parsing the payload.

        Keyword arguments:
        payload -- a packet in raw bytes, without its first 2 bytes (opcode)
        """
        raise NotImplementedError("Abstract method")

    def to_wire(self):
        """
        Returns the bytes representation of the packet.
        """
        raise NotImplementedError("Abstract method")


class RQPacket(TftpPacket):
    """
    RQPacket representation:

     2 bytes     string    1 byte     string   1 byte
     ------------------------------------------------
    | 01/02  |  Filename  |   0  |    Mode    |   0  |
     ------------------------------------------------
    """

    def __init__(self, filename, mode):
        """
        Keyword arguments:
        filename -- raw bytes, represents the requested file name
        mode     -- raw bytes, transfer mode, can be b'netascii' or b'octet'
        """
        assert isinstance(filename, bytes), "Filename must be in bytes"
        assert isinstance(mode, bytes), "Mode must be in bytes"
        self.filename = filename
        self.mode = mode.lower()
        assert self.mode in (b'netascii', b'octet'), "Unsupported mode"

    @classmethod
    def from_wire(cls, payload):
        tokens = payload.split(TftpPacket.seperator)
        if len(tokens) < 2:
            # handle this error
            raise Exception

        return cls(filename=tokens[0], mode=tokens[1])

    def to_wire(self):
        return b''.join((struct.pack("!H", self.opcode), self.filename,
                         self.seperator, self.mode, self.seperator))


class RRQPacket(RQPacket):
    opcode = 1


class WRQPacket(RQPacket):
    opcode = 2


class DataPacket(TftpPacket):
    """
    DataPacket representation:

     2 bytes    2 bytes       n bytes
     ---------------------------------
    |  03   |   Block #  |    Data    |
     ---------------------------------
    """
    opcode = 3

    def __init__(self, blockn, data):
        """
        Keyword arguments:
        blockn -- integer, sequence number
        data   -- raw bytes, file data, 512 bytes or less

        The is_last instance variable indicates whether the packet is the last
        in the sequence of all the sent or received packets.
        """
        assert isinstance(data, bytes), "Data must be in bytes"
        assert len(data) <= 512, "512 bytes of data is the max for a packet"
        self.blockn = blockn
        self.data = data
        self.is_last = len(data) < 512

    @classmethod
    def from_wire(cls, payload):
        try:
            blockn = struct.unpack('!H', payload[:2])
        except struct.error:
            # handle this error
            return

        data = payload[2:]
        if len(data) > 512:
            # handle this error
            return

        return cls(blockn, data)

    def to_wire(self):
        return b''.join((struct.pack('!HH', self.opcode, self.blockn), self.data))


class ACKPacket(TftpPacket):
    """
    ACKPacket representation:

     2 bytes    2 bytes
     -------------------
    |  04   |   Block #  |
     --------------------
    """
    opcode = 4

    def __init__(self, blockn):
        """
        Keyword arguments:
        blockn -- integer, sequence number
        """
        self.blockn = blockn

    @classmethod
    def from_wire(cls, payload):
        try:
            blockn = struct.unpack('!H', payload)[0]
        except struct.error:
            # handle this error
            return

        return cls(blockn)

    def to_wire(self):
        return struct.pack('!HH', self.opcode, self.blockn)


class ErrorPacket(TftpPacket):
    """
    ErrorPacket representation:

     2 bytes  2 bytes        string    1 byte
     ----------------------------------------
    |  05   |  ErrorCode |   ErrMsg   |   0  |
     ----------------------------------------
    """
    opcode = 5

    errors = {
        0 : "Not defined, see error message (if any)",
        1 : "File not found",
        2 : "Access violation",
        3 : "Disk full or allocation exceeded",
        4 : "Illegal TFTP operation",
        5 : "Unknown transfer ID",
        6 : "File already exists",
        7 : "No such user",
    }

    def __init__(self, error_code, error_msg=None):
        """
        Keyword arguments:
        error_code -- integer, TFTP error code
        error_msg  -- raw bytes, error message
        """
        self.error_code = error_code
        if error_msg is None:
            self.error_msg = self.errors[error_code]
        else:
            assert isinstance(error_msg, bytes), "Error message must be in bytes"
            self.error_msg = error_msg

    @classmethod
    def from_wire(cls, payload):
        try:
            error_code = struct.unpack('!H', payload[:2])[0]
        except struct.error:
            # handle this error
            return

        error_msg = payload[2:].split(TftpPacket.seperator)[0]

        if not error_code in ErrorPacket.errors.keys():
            # handle this error
            return

        return cls(error_code, error_msg)

    def to_wire(self):
        return b''.join((struct.pack('!HH', self.opcode, self.error_code),
                         self.error_msg, self.seperator))
