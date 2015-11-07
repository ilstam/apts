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
    opcode = None
    seperator = '\x00'

    @classmethod
    def from_wire(cls, payload):
        """
        Creates a TftpPacket object by parsing the payload.

        Keyword arguments:
        payload -- a packet that comes directly from the wire,
                   without its first 2 bytes which are the opcode
        """
        raise NotImplementedError("Abstract method")

    def to_wire(self):
        """
        Returns the wire representation of the packet (in bytes).
        """
        raise NotImplementedError("Abstract method")

    def respond_to(self, session):
        """
        Handles a received TftpPacket.

        Keyword arguments:
        session -- an object holding the state of the current connection

        Returns a new TftpPacket as a response to the received one.
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
        self.filename = filename
        self.mode = mode.lower()
        assert self.mode in ('netascii', 'octet'), "Unsupported mode"

    @classmethod
    def from_wire(cls, payload):
        tokens = payload.split(TftpPacket.seperator)
        if len(tokens) < 2:
            # handle this error
            raise Exception

        return cls(filename=tokens[0], mode=tokens[1])


class RRQPacket(RQPacket):
    opcode = 1


class WRQPacket(RQPacket):
    opcode = 2


class DATAPacket(TftpPacket):
    """
    DATAPacket representation:

     2 bytes    2 bytes       n bytes
     ---------------------------------
    |  03   |   Block #  |    Data    |
     ---------------------------------
    """
    opcode = 3

    def __init__(self, block, data):
        self.block = block
        self.data = data

    @classmethod
    def from_wire(cls, payload):
        try:
            block = struct.unpack('!H', payload[:2])
            data = payload[2:]
        except struct.error:
            # handle this error
            return

        return cls(block, data)


class ACKPacket(TftpPacket):
    """
    ACKPacket representation:

     2 bytes    2 bytes
     -------------------
    |  04   |   Block #  |
     --------------------
    """
    opcode = 4

    def __init__(self, block):
        self.block = block

    @classmethod
    def from_wire(cls, payload):
        try:
            block = struct.unpack('!H', payload)[0]
        except struct.error:
            # handle this error
            return

        return cls(block)


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
        self.error_code = error_code
        self.error_msg = self.errors[error_code] if error_msg is None else error_msg

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
