APTS
====

Apts stands for "Another Python TFTP Server".
It is a complete server implementation of the RFC 1350.

Dependencies
-------------
python3

How to install
---------------
From application's directory run as root:
    python3 setup.py install

Then you can start the server by simply typing:
    apts

Run without installing
-----------------------
You may even launch the application without installing it, by
running the launcher script.

How to configure
-----------------
The program will read any configuration from /etc/conf.d/apts,
if such a file exists. If not, it will use its default values.
An example configuration file can be found on conf/apts.

No command line arguments are accepted at the moment.

Further plans (TODO)
---------------------

* Implement a TFTP client as well.
* Implement RFC2347, RFC2348 and RFC2349 extensions.
* Add IPv6 support.
* Write systemd service files.
* Windows port.
