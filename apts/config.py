import sys
import logging
import configparser

from .errors import ParseConfigError


# Symbolic name, meaning all available interfaces.
host = ''

# Well-known TFTP port number
port = 69

# Path of the directory from where we serve files and write files to.
tftp_root = '/srv/tftp/'

# If True, allow files to written. Else, the server runs on read-only
# mode and a TFTP client can only read existing files.
writable = True

# Maximum amount of data to be received at once.
# Note: For best match with hardware and network realities,
# the value of bufsize should be a relatively small power of 2.
bufsize = 2048


# exit codes

EXIT_NORMAL = 0
EXIT_CONF_ERROR = 1
EXIT_ROOTDIR_ERROR = 2
EXIT_PRIVILEGES = 3


# parse the configuration file

config_parser = configparser.ConfigParser()
config_parser.read('/etc/conf.d/apts')

try:
    try:
        port = int(config_parser['SERVER']['port'])
    except ValueError:
        raise ParseConfigError("Failed to parse port value")
    except KeyError:
        pass

    try:
        tftp_root = config_parser['SERVER']['tftp_root']
    except KeyError:
        pass

    try:
        writable = config_parser['SERVER']['writable']

        if writable == 'True':
            writable = True
        elif writable == 'False':
            writable = False
        else:
            raise ParseConfigError("Failed to parse writable value")
    except KeyError:
        pass

except ParseConfigError as e:
    logging.error("Configuration error: " + str(e))
    logging.info("Aborting")
    sys.exit(EXIT_CONF_ERROR)
