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

from .errors import (DataSizeError, InvalidErrorcodeError, InvalidOpcodeError,
                     OpcodeExtractError, PayloadParseError, UnsupportedModeError)


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
        self.filename = filename
        self.mode = mode.lower()

        if self.mode not in (b'netascii', b'octet'):
            raise UnsupportedModeError(self.mode.decode())

    @classmethod
    def from_wire(cls, payload):
        tokens = payload.split(TftpPacket.seperator)
        if len(tokens) < 2:
            raise PayloadParseError("not enough fields in the payload")

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
        if len(data) > 512:
            raise DataSizeError()

        self.blockn = blockn
        self.data = data
        self.is_last = len(data) < 512

    @classmethod
    def from_wire(cls, payload):
        try:
            blockn = struct.unpack('!H', payload[:2])[0]
        except struct.error:
            raise PayloadParseError("couldn't extract block number")

        return cls(blockn, data=payload[2:])

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
            raise PayloadParseError("couldn't extract block number")

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

    ERR_NOT_DEFINED = 0
    ERR_FILE_NOT_FOUND = 1
    ERR_ACCESS_VIOLATION = 2
    ERR_DISK_FULL = 3
    ERR_ILLEGAL_OPERATION = 4
    ERR_UNKNOWN_TID = 5
    ERR_FILE_EXISTS = 6
    ERR_NO_SUCH_USER = 7

    errors = {
        ERR_NOT_DEFINED: "Not defined, see error message (if any)",
        ERR_FILE_NOT_FOUND: "File not found",
        ERR_ACCESS_VIOLATION: "Access violation",
        ERR_DISK_FULL: "Disk full or allocation exceeded",
        ERR_ILLEGAL_OPERATION: "Illegal TFTP operation",
        ERR_UNKNOWN_TID: "Unknown transfer ID",
        ERR_FILE_EXISTS: "File already exists",
        ERR_NO_SUCH_USER: "No such user",
    }

    def __init__(self, error_code, error_msg=None):
        """
        Keyword arguments:
        error_code -- integer, TFTP error code
        error_msg  -- raw bytes, error message
        """
        self.error_code = error_code
        if not self.error_code in self.errors.keys():
            raise InvalidErrorcodeError(self.error_code)

        if error_msg is None:
            self.error_msg = self.errors[error_code]
        else:
            self.error_msg = error_msg

    @classmethod
    def from_wire(cls, payload):
        try:
            error_code = struct.unpack('!H', payload[:2])[0]
        except struct.error:
            raise PayloadParseError("couldn't extract error code")

        error_msg = payload[2:].split(TftpPacket.seperator)[0]
        return cls(error_code, error_msg)

    def to_wire(self):
        return b''.join((struct.pack('!HH', self.opcode, self.error_code),
                         self.error_msg, self.seperator))


class PacketFactory:
    """
    This class generates TftpPacket objects by using its create() method.
    It parses raw data (byte representations of TftpPackets) and creates new
    instances depending on the extracted opcode.
    """
    packet_pool = {
        RRQPacket.opcode: RRQPacket,
        WRQPacket.opcode: WRQPacket,
        DataPacket.opcode: DataPacket,
        ACKPacket.opcode: ACKPacket,
        ErrorPacket.opcode: ErrorPacket,
    }

    def create(self, data):
        """
        Creates an appropriate TftpPacket instance, based on the opcode of
        the given data.

        Keyword arguments:
        data -- raw bytes representation of a TftpPacket

        Returns a TftpPacket object.
        May raise a PacketParseError.
        """
        opcode, payload = self.split_packet(data)

        try:
            return self.packet_pool[opcode].from_wire(payload)
        except KeyError:
            raise InvalidOpcodeError

    @staticmethod
    def split_packet(data):
        """
        Splits a bytes representation of a TftpPacket into opcode and payload.

        Keyword arguments:
        data -- raw bytes representation of a TftpPacket

        Returns an opcode, payload tuple.
        """
        try:
            opcode = struct.unpack("!H", data[:2])[0]
        except struct.error:
            raise OpcodeExtractError()

        return opcode, data[2:]
