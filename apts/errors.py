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


class TftpError(Exception):
    """
    Base exception class.
    All other exceptions should inherit from this class.
    """
    pass


class PacketParseError(TftpError):
    """
    Failed to parse a packet (raw data).
    """
    pass


class OpcodeExtractError(PacketParseError):
    """
    Failed to extract the opcode of a TftpPacket.
    """
    def __str__(self):
        return "failed to extract packet opcode"


class InvalidOpcodeError(PacketParseError):
    """
    A TftpPacket has an invalid TFTP opcode.
    """
    def __init__(self, opcode):
        self.opcode = opcode

    def __str__(self):
        return "invalid TFTP opcode: {0}".format(self.opcode)


class PayloadParseError(PacketParseError):
    """
    Failed to parse the payload.
    """
    pass


class UnsupportedModeError(PayloadParseError):
    """
    An unsupported TFTP mode requested.
    """
    def __init__(self, mode):
        self.mode = mode

    def __str__(self):
        return "unsupported TFTP mode: {0}".format(self.mode)


class DataSizeError(PayloadParseError):
    """
    A DataPacket carries more than 512 bytes of data.
    """
    def __str__(self):
        return "512 bytes of data is the max for a packet"


class InvalidErrorcodeError(PayloadParseError):
    """
    An ErrorPacket has an invalid TFTP error code.
    """
    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        return "unknown TFTP error code: {0}".format(self.error_code)


class TftpIOError(Exception):
    """
    Base exception class for Tftp I/O errors.
    """
    pass
