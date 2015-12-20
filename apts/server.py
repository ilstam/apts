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
import pwd
import grp
import sys
import socket
import logging

from . import config
from .session import TftpSessionThread
from .errors import TftpRootError


class TftpServer:
    def __init__(self, tftp_root=config.tftp_root, writable=config.writable):
        """
        Keyword arguments:
        tftp_root -- path to the tftp root directory
        writable  -- if True, the server is writable
                     else, a client can only read existing files
        """
        self.tftp_root = os.path.realpath(tftp_root)
        self.writable = writable

        if not self.check_tftp_root():
            logging.info("Terminating the server")
            sys.exit(config.EXIT_ROOTDIR_ERROR)

        logging.info("TFTP root directory set to: {}".format(self.tftp_root))

    def listen(self, ip=config.host, port=config.port):
        """
        Start a server listening on the supplied interface and port.
        """
        # AF_INET for IPv4 family address, SOCK_DGRAM for UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((ip, port))
        logging.info('Start listening on port {}'.format(port))

        # Drop no longer needed root privileges for security reasons.
        if not self.drop_root_privileges():
            logging.info('Aborting')
            sys.exit(config.EXIT_PRIVILEGES)

        while True:
            data, client_address = server_socket.recvfrom(config.bufsize)

            session_thread = TftpSessionThread(ip, client_address,
                    self.tftp_root, self.writable, data)
            session_thread.start()

    def check_tftp_root(self):
        """
        Performs sanity checks on the tftp root path.

        Returns True if the path passes the tests, else False.
        """
        try:
            if not os.path.exists(self.tftp_root):
                raise TftpRootError("The TFTP root does not exist")
            if not os.path.isdir(self.tftp_root):
                raise TftpRootError("The TFTP root must be a directory")
        except TftpRootError as e:
            logging.error("{}: {}".format(e, self.tftp_root))
            return False

        return True

    @staticmethod
    def drop_root_privileges(username='nobody'):
        """
        Drops root privileges of the process by changing to user 'username'
        and username's group.

        Returns True if privileges were dropped, else False.
        """
        try:
            user = pwd.getpwnam(username)
        except KeyError as e:
            logging.error(e)
            return False

        try:
            os.setgroups([]) # remove group privileges
            os.setgid(user.pw_gid)
            os.setuid(user.pw_uid)
        except OSError as e:
            logging.error('Could not set effective group or user id: {}'.format(e))
            return False

        logging.info('Dropped root privilages, running as {}:{}'.format(
                user.pw_name, grp.getgrgid(user.pw_gid).gr_name))
        return True


def main():
    server = TftpServer()
    server.listen()
