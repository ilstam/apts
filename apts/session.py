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
import logging
import threading

from . import config
from .errors import PacketParseError
from .file_rw import TftpFileReader, TftpFileWriter
from .packets import (RRQPacket, WRQPacket, DataPacket, ACKPacket, ErrorPacket,
                      PacketFactory)


class TftpSessionThread(threading.Thread):
    """
    Each file transfer should happen on a TftpSessionThread that runs on a
    separate thread. The session should take care of all the incoming traffic
    for this specific "imaginary" connection, starting with the first received
    packet.

    A session is associated with one file transfer only, and therefore each
    session uses a different transfer socket with a unique TID (transfer
    identifier). Of course, a TftpServer can have many sessions running
    simultaneously.

    When the file transfer is over, the session is destroyed.
    """
    factory = PacketFactory()

    def __init__(self, interface, remote_address, tftp_root, allow_write,
                 initial_data):
        """
        Keyword arguments:
        interface      -- the interface to bind to
        remote_address -- the address of the remote host in a (ip, port) format
        tftp_root      -- canonical path of the tftp root directory
        allow_write    -- if False, reject all WRQs
        intial_data    -- the initial raw data received by the server at the
                          beggining of the transfer with the remote host.
                          should be a read or write request.
        """
        super().__init__()

        self.remote_address = remote_address
        self.initial_data = initial_data
        self.tftp_root = tftp_root
        self.allow_write = allow_write

        # We must create a new socket with a random TID for the transfer.
        # Port value 0 means that the OS will pick an available port for us.
        self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.transfer_socket.bind((interface, 0))
        self.tid = self.transfer_socket.getsockname()[1]

        # When we receive data, blockn indicates the block number of the next
        # DataPacket that we expect to acknowledge. When we send data, blockn
        # indicates the block number of the last sent DataPacket.
        self.blockn = 0

        # Save the last packet we sent, to make retransmission easy.
        self.last_sent = None
        self.last_received = None

        # Each time we retransmit a package, we can have different timeout
        # values. When and if the values of the following tuple is exhausted,
        # the transfer is considered failed and the session is terminated.
        self.timeout_values = (3, 5, 8)

        # Indicates the number of retransmissions of the last sent packet.
        self.retransmissions = 0

        # A TftpFileReader instance will be initialized if, and at the time,
        # we receive a RRQ packet.
        self.file_reader = None
        # As above, will be initialized with a WRQ packet.
        self.file_writer = None

        self.respond_map = {
            RRQPacket: self.respond_to_RRQ, WRQPacket: self.respond_to_WRQ,
            DataPacket: self.respond_to_Data, ACKPacket: self.respond_to_ACK,
            ErrorPacket: self.respond_to_Error
        }

        logging.info('Initialized new connection from {} with TID={}'\
                     .format(remote_address[0], self.tid))

    def run(self):
        """
        This method represents the thread's activity as it overrides the
        threading.Thread's run() method and it can be seen as the main of the
        session.

        It waits for new data, takes care of retransmissions and handles
        received data appropriately.

        When this method is over the session is terminated.
        """
        while True:
            timeout = self.timeout_values[self.retransmissions]
            self.transfer_socket.settimeout(timeout)

            try:
                data = self.read_new_data()
            except socket.timeout:
                self.retransmissions += 1
                if not self.must_retransmit():
                    break

                self.resend_last()
            else:
                self.send_packet(self.respond_to_data(data))
                self.retransmissions = 0

                if isinstance(self.last_sent, (ErrorPacket, type(None))):
                    break

        logging.info('Connection with TID={} closed'.format(self.tid))

    def read_new_data(self):
        """
        Returns new raw data for processing.

        First time called, it returns the initial data that have been passed
        to the session. After then, it reads data from the transfer_socket.

        May raise socket.timeout error.
        """
        if self.initial_data is None:
            return self.transfer_socket.recvfrom(config.bufsize)[0]

        data = self.initial_data
        self.initial_data = None
        return data

    def send_packet(self, packet):
        """
        Sends a TftpPacket to the remote host through the transfer socket.
        """
        self.last_sent = packet
        if packet is None:
            return

        self.transfer_socket.sendto(packet.to_wire(), self.remote_address)
        logging.info("[Sent TID={}] ".format(self.tid) + str(packet))

    def resend_last(self):
        """
        Retransmits the last sent packet, due to a socket timeout.
        """
        self.send_packet(self.last_sent)

    def must_retransmit(self):
        """
        Checks whether the last sent packet needs retransmission after a
        socket timeout.

        Returns True if we need to retransmit the last packet, else False.
        """
        if self.retransmissions >= len(self.timeout_values):
            return False
        # Do not retransmit ACK packets for the last block of data.
        if isinstance(self.last_received, DataPacket):
            return not self.last_received.is_last
        return True

    def respond_to_data(self, data):
        """
        Creates an appropriate TftpPacket as a response to the received raw
        data, based on the type of packet of the received data.

        Returns a TftpPacket or None. None as a return value means that we
        should just ignore the received data and send nothing in response.
        """
        try:
            packet = self.factory.create(data)
        except PacketParseError:
            msg = "[UNKOWN] Failed to parse received packet"
            logging.info("[Recv TID={}] ".format(self.tid) + msg)
            return ErrorPacket(ErrorPacket.ERR_ILLEGAL_OPERATION)

        logging.info("[Recv TID={}] ".format(self.tid) + str(packet))
        self.last_received = packet
        return self.respond_map[type(packet)](packet)

    def respond_to_RRQ(self, packet):
        fname, mode = packet.filename.decode(), packet.mode.decode()
        path = os.path.realpath(os.path.join(self.tftp_root, fname.strip('/')))

        # Ensure that file exists, is readable and resides in the tftp root.
        if not os.path.isfile(path) or not path.startswith(self.tftp_root):
            return ErrorPacket(ErrorPacket.ERR_FILE_NOT_FOUND)
        if not os.access(path, os.R_OK):
            return ErrorPacket(ErrorPacket.ERR_ACCESS_VIOLATION)

        self.file_reader = TftpFileReader(path, mode)
        data = self.file_reader.get_next_block()
        self.blockn = 1

        return DataPacket(self.blockn, data)

    def respond_to_WRQ(self, packet):
        fname, mode = packet.filename.decode(), packet.mode.decode()
        path = os.path.realpath(os.path.join(self.tftp_root, fname.strip('/')))

        if not all([self.allow_write,
                    path.startswith(self.tftp_root),
                    os.access(os.path.split(path)[0], os.W_OK)]):
            return ErrorPacket(ErrorPacket.ERR_ACCESS_VIOLATION)

        self.file_writer = TftpFileWriter(path, mode)
        self.blockn = 1

        return ACKPacket(0)

    def respond_to_Data(self, packet):
        if packet.blockn > self.blockn:
            return ErrorPacket(ErrorPacket.ERR_UNKNOWN_TID)

        if packet.blockn == self.blockn:
            try:
                self.file_writer.write_next_block(packet.data)
            except IOError:
                return ErrorPacket(ErrorPacket.ERR_DISK_FULL)
            else:
                self.blockn += 1

        return ACKPacket(packet.blockn)

    def respond_to_ACK(self, packet):
        if packet.blockn == self.blockn:
            if isinstance(self.last_sent, DataPacket) and self.last_sent.is_last:
                return None

            self.blockn += 1
            data = self.file_reader.get_next_block()
            return DataPacket(self.blockn, data)

        if packet.blockn < self.blockn:
            return self.last_sent

        return ErrorPacket(ErrorPacket.ERR_UNKNOWN_TID)

    def respond_to_Error(self, packet):
        # As a server we should not receive any error packets from a client.
        return ErrorPacket(ErrorPacket.ERR_UNKNOWN_TID)
