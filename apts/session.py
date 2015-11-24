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

import os
import socket

from . import config
from .errors import PacketParseError
from .file_rw import TftpFileReader, TftpFileWriter
from .packets import (RRQPacket, WRQPacket, DataPacket, ACKPacket, ErrorPacket,
                      PacketFactory)


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
    factory = PacketFactory()

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

        # Each time we retransmit a package, we increase the timeout time.
        # When and if the values of the following tuple is exhausted, the
        # transfer is considered failed and the session is terminated.
        self.timeout_values = (1, 3, 8)

        # Indicates the number of retransmissions of the last sent packet.
        self.retransmissions = 0

        # A TftpFileReader instance will be initialized if, and at the time,
        # we receive a RRQ packet.
        self.file_reader = None
        # As above, will be initialized with a WRQ packet.
        self.file_writer = None

    def listen(self):
        while True:
            timeout = self.timeout_values[self.retransmissions]
            self.transfer_socket.settimeout(timeout)

            try:
                data, _ = transfer_socket_socket.recvfrom(config.bufsize)
                self.handle_received_data(data)
                self.retransmissions = 0
            except socket.timeout:
                self.retransmissions += 1
                if self.retransmissions < len(self.timeout_values):
                    self.resend_last()
                else:
                    break # termination of session

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

    def handle_received_data(self, data):
        """
        """
        try:
            packet = self.factory.create(data)
            response_packet = self.respond_to_packet(packet)
        except PacketParseError:
            response_packet = ErrorPacket(ErrorPacket.ERR_ILLEGAL_OPERATION)

        if response_packet is not None:
            self.send_packet(response_packet)

    def respond_to_packet(self, packet):
        """
        Returns an appropriate TftpPacket in response, based on the type of
        the packet given. If the return value is None, it means that we should
        just ignore the received packet and send nothing in response.
        """
        handle_map = {
            RRQPacket: self.respond_to_RRQ, WRQPacket: self.respond_to_WRQ,
            DataPacket: self.respond_to_Data, ACKPacket: self.respond_to_ACK,
            ErrorPacket: self.respond_to_Error
        }
        return handle_map[type(packet)](packet)

    def respond_to_RRQ(self, packet):
        fname, mode = packet.filename.decode(), packet.mode.decode()
        if not os.isfile(fname):
            return ErrorPacket(ErrorPacket.ERR_FILE_NOT_FOUND)

        self.file_reader = TftpFileReader(fname, mode)

        data = self.file_reader.get_next_block()
        self.blockn += 1
        return DataPacket(self.blockn, data)

    def respond_to_WRQ(self, packet):
        fname, mode = packet.filename.decode(), packet.mode.decode()
        if os.isfile(fname):
            return ErrorPacket(ErrorPacket.ERR_FILE_EXISTS)

        self.file_writer = TftpFileWriter(fname, mode)
        return ACKPacket(0)

    def respond_to_Data(self, packet):
        if packet.blockn == self.blockn:
            try:
                self.file_writer.write_next_block(packet.data)
                self.blockn += 1
            except IOError:
                # No space left on device
                return ErrorPacket(ErrorPacket.ERR_DISK_FULL)

        return ACKPacket(packet.blockn)

    def respond_to_ACK(self, packet):
        if packet.blockn == self.blockn:
            self.blockn += 1
            data = self.file_reader.get_next_block()
            return DataPacket(self.blockn, data)

        if packet.blockn < self.blockn:
            return self.last_sent

        return None

    def respond_to_Error(self, packet):
        # As a server we should not receive any error packets from a client.
        return None
