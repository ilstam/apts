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


class TftpPacket:
    """
    Represents a TFTP packet.
    All TFTP packets should inherit from this class and it may not be
    instantiated directly.
    """
    opcode = None

    @classmethod
    def from_wire(cls, payload):
        """
        Creates a TftpPacket object by parsing the payload.

        Keyword arguments:
        payload -- a packet that comes directly from the wire,
                   without its first 2 bytes which are the opcode
        """
        raise NotImplementedError("Abstract method")

    def send(self, session):
        """
        Sends a TftpPacket to the wire, through the socket defined in the
        session.

        Keyword arguments:
        session -- an object holding the state of the current connection
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
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode


class RRQPacket(RQPacket):
    opcode = 1


class WRQPacket(RQPacket):
    opcode = 2


class DATAPacket(TftpPacket):
    opcode = 3

    def __init__(self, block, data):
        self.block = block
        self.data = data


class ACKPacket(TftpPacket):
    opcode = 4

    def __init__(self, block):
        self.block = block


class ErrorPacket(TftpPacket):
    opcode = 5

    def __init__(self, block, error_msg):
        self.block = block
        self.error_msg = error_msg
