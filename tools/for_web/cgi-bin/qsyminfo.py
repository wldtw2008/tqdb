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

szSymbol="ALL"

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]
if 'symbol' in mapQS: szSymbol = mapQS['symbol']
sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
szCMD="./qsym %s %s %s.symbol 0 %s 1 > %s" % (szCassIP1, '9042', szCassDB, szSymbol, tmpFile)
subprocess.call(szCMD, shell=True, cwd='/home/tqdb/codes/tqdb/tools/') 
fp = file(tmpFile, 'rb')
jsonstr=fp.read()
os.remove(tmpFile)
allObjs = json.loads(jsonstr.replace("'",'"'))
sys.stdout.write(json.dumps(allObjs))
sys.stdout.flush()
