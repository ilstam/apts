# Netascii is a modified form of ASCII, defined in RFC 764 (Telnet).
# It requires that any CR must be followed by either a LF or the NULL. So, in
# netascii a newline is represented by CR+LF, and a single CR is represented
# by CR+NULL.

import os
import re

LF = b'\x0d\x0a' # ASCII CR + LF
CR = b'\x0d\x00' # ASCII CR + NUL


def encode(bdata):
    """
    Converts a python string, with platfrom-specific newlines, into a
    netascii string. Returns a sequence of bytes.

    Keyword arguments:
    bdata -- the byte sequence of a python string
    """
    def f(matched):
        return CR if matched.group(0) == b'\r' else LF

    regex = '({0}|\r)'.format(os.linesep).encode()
    return re.sub(regex, f, bdata)

def decode(bdata):
    """
    Converts a netascii-encoded string to a python string with
    platform-specific newlines. Returns a sequence of bytes.

    Keyword arguments:
    bdata -- the byte sequence of a netascii-encoded string
    """
    def f(matched):
        return b'\r' if matched.group(0) == CR else os.linesep.encode()

    regex = b'(%s|%s)' % (LF, CR)
    return re.sub(regex, f, bdata)
