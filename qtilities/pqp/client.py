#!/usr/bin/env python
"""Python QML preview client. Sends source filenames specified in command line
to pqp via UDP."""

import socket
import sys
import os

from . import UDP_PORT


def main():
    sources = sys.argv[1:]

    if sources:
        # render paths absolute
        absolute_sources = []
        cwd = os.getcwd()
        for source in sources:
            absolute_sources.append(os.path.join(cwd, source))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto("\n".join(absolute_sources).encode(), ("localhost", UDP_PORT))
    else:
        raise SystemExit("Usage: pqpc FILE [FILE...]")
