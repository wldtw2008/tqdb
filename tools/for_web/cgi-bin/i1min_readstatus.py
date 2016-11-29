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


importLogFile = '/tmp/%s.log' % importTicket
sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
sys.stdout.write("<html><body>\r\n")
bFinish = False
try:
    with open(importLogFile, 'r') as f:
        for line in f:
            sys.stdout.write("%s<br>" % line)
            if line.find('Importing finish!') >=0:
                bFinish = True
except:
    pass
sys.stdout.write("<script language='javascript'>")
sys.stdout.write("window.scrollTo(0,document.body.scrollHeight);")
if not bFinish:
    sys.stdout.write("setTimeout('window.location.reload();', 1000);")
sys.stdout.write("</script>")
sys.stdout.write("</body></html>\r\n")

sys.stdout.write("\r\n")
sys.stdout.flush()

