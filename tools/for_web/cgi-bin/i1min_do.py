#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import os
import subprocess
import json

szCassIP1="127.0.0.1"
szCassDB="tqdb1"

importTicket=""

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]
if 'importTicket' in mapQS: importTicket = mapQS['importTicket']


cmdfile = '/tmp/%s.cmd' % importTicket
if os.path.isfile(cmdfile):
    sys.stdout.write("Content-Type: text/plain\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.flush()
    subprocess.call(cmdfile, shell=True, cwd='/tmp')
else:
    sys.stdout.write("Content-Type: text/html\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write("<html><body>\r\n")
    sys.stdout.write("Can't find the ticket: '%s'\r\n"%importTicket)
    sys.stdout.write("</body></html>\r\n")

sys.stdout.write("\r\n")
sys.stdout.flush()

