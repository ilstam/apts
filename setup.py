#!/usr/bin/env python3

import apts
from distutils.core import setup


setup(
    name = apts.__name__,
    packages = [apts.__name__],
    scripts = ['bin/apts'],
    version = apts.__version__,
    description = apts.__description__,
    author = apts.__author__,
    author_email = apts.__author_email__,
    license = apts.__license__,
    platforms = apts.__platforms__,
    url = apts.__url__,
    download_url = apts.__download_url__,
    keywords = ['tftp', 'server', 'file transfer'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Topic :: Communications :: File Sharing',
    ],
)

