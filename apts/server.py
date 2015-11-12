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

from . import config
from .session import TftpSession


class TftpServer:
    def listen(self, ip=config.host, port=config.port):
        """
        Start a server listening on the supplied ip and port.
        """
        # AF_INET for IPv4 family address, SOCK_DGRAM for UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((ip, port))

        while True:
            data, client_address = server_socket.recvfrom(config.bufsize)

            session = TftpSession(ip, client_address)


def main():
    server = TftpServer()
    server.listen()
