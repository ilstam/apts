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

import socket

from .packets import RRQPacket, WRQPacket, DataPacket, ACKPacket, ErrorPacket


class TftpSession:
    """
    A new session must be created in the beggining of the communication
    with a new address. It should take care of all the incoming traffic from
    that specific address, starting with the first received packet.

    A session is associated with one file transfer only, and therefore each
    session uses a different transfer socket with a unique TID (transfer
    identifier). Of course, a TftpServer can have many sessions running
    simultaneously.

    When the file transfer is over, the session is destroyed.
    """
    def __init__(self, local_ip, remote_address):
        """
        Keyword arguments:
        local_ip       -- the ip to listen to
        remote_address -- the address of the remote host on a ('ip', port) format
        """
        self.remote_address = remote_address

        # We must create a new socket with a random TID for the transfer.
        # Port 0 means that the OS will pick an available port for us.
        self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.transfer_socket.bind((local_ip, 0))

        # When we receive data, blockn indicates the block number of the next
        # DataPacket that we expect to acknowledge. When we send data, blockn
        # indicates the block number of the last sent DataPacket.
        self.blockn = 0

        # Save the last packet we sent, to make retransmission easy.
        self.last_sent = None

    def send_packet(self, packet):
        """
        Sends a TftpPacket to the remote host through the transfer socket.
        """
        self.transfer_socket.sendto(packet.to_wire(), self.remote_address)
        self.last_sent = packet

    def resend_last(self):
        """
        Retransmits the last sent packet, due to a socket timeout.
        """
        self.send_packet(self.last_sent)

    def respond_to_packet(self, packet):
        """
        Returns an appropriate TftpPacket in response, based on the type of
        the packet given.
        """
        handle_map = {
            RRQPacket: self.respond_to_RRQ, WRQPacket: self.respond_to_WRQ,
            DataPacket: self.respond_to_Data, ACKPacket: self.respond_to_ACK,
            ErrorPacket: self.respond_to_Error
        }
        return handle_map[type(packet)](packet)

    def respond_to_RRQ(self, packet):
        return packet

    def respond_to_WRQ(self, packet):
        return packet

    def respond_to_Data(self, packet):
        return packet

    def respond_to_ACK(self, packet):
        return packet

    def respond_to_Error(self, packet):
        return packet
