# Netascii is a modified form of ASCII, defined in RFC 764 (Telnet).
# It requires that any CR must be followed by either a LF or the NULL. So, in
# netascii a newline is represented by CR+LF, and a single CR is represented
# by CR+NULL.

LF = b'\x0d\x0a' # ASCII CR + ASCII LF
CR = b'\x0d\x00' # ASCII CR + ASCII NUL


def encode(bdata):
    """
    Converts a python string, with platfrom-specific newlines, into a
    netascii string. Returns a sequence of bytes.

    Keyword arguments:
    bdata -- the byte sequence of a python string
    """
    pass

def decode(bdata):
    """
    Converts a netascii-encoded string to a python string with
    platform-specific newlines. Returns a sequence of bytes.

    Keyword arguments:
    bdata -- the byte sequence of a netascii-encoded string
    """
    pass
