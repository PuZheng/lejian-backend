#!/usr/bin/env python
"""
SYNOPSIS
    python runserver.py [options]
OPTIONS
    -h
        show this help
    -p  <port>
        the port of server runs on
    -s  <host>
        the ip of the server runs on
"""

from getopt import getopt
import sys
opts, _ = getopt(sys.argv[1:], "s:p:h")

host = '0.0.0.0'
port = None
for o, v in opts:
    if o == "-s":
        host = v
    elif o == "-p":
        port = int(v)
    elif o == "-h":
        print __doc__
    else:
        print "unkown option: " + o
        print __doc__

from genuine_ap import utils
utils.assert_dir('static/spu_pics')

from basemain import app, register_views
register_views()

app.run(host=host, port=port)
