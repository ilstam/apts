APTS
====

Apts stands for "Another Python TFTP Server".
It is a complete server implementation of the RFC 1350.

Dependencies
-------------
python3

Installation
-------------
From application's directory run as root:
    python3 setup.py install

It's not necessary to install the program system-wide, see below.

Configuration
--------------
The program will read any configuration from /etc/conf.d/apts, if such a
file exists. If not, it will use its default values. An example configuration
file can be found on conf/apts.

No command line arguments are accepted at the moment.

Setup the TFTP root
--------------------
Before starting the server, you need to create the TFTP root directory with
the appropriate ownership. The default root directory is /srv/tftp/ but you may
change it as described above.

First create the directory:
    mkdir /srv/tftp/

Then change its owner and group:
    chown -R nobody:nogroup /srv/tftp/

In case there's no nogroup group on your system, you can use the nobody group
if exists or any other similar group.

Run the server
---------------
Once you properly installed the application, you can start the server as root
by simply typing `apts`.

You also have the option to run the server without even installing it, by
executing the launcher script as root.

Further plans (TODO)
---------------------
* Implement a TFTP client as well.
* Implement RFC2347, RFC2348 and RFC2349 extensions.
* Add IPv6 support.
* Write systemd service files.
* Windows port.

***IMPORTANT NOTICE***
=======================
The software hasn't already been thoroughly tested.
PLEASE DO NOT USE IN PRODUCTION (YET), or do so at your own risk.
The software is provided "as is", without warranty of any kind.
