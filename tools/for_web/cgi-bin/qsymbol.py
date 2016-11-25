#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import os
import subprocess

szCassIP1="127.0.0.1"
szCassDB="tqdb1"

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]

sys.stdout.write("Content-Type: text/plain\r\n")
sys.stdout.write("\r\n")
tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
szCMD="./qsym %s %s %s.symbol 0 ALL 1 > %s" % (szCassIP1, '9042', szCassDB, tmpFile)
subprocess.call(szCMD, shell=True, cwd='/home/tqdb/codes/tqdb/tools/') 
fp = file(tmpFile, 'rb')
sys.stdout.write(fp.read())
sys.stdout.flush()
os.remove(tmpFile)
