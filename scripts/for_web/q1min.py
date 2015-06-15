#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import urllib

szBinDir='/home/tqdb/codes/tqdb/scripts/'
szSymbol = "SIN"; #"TXO;201506;9200P";
timeoffset=0	
iLocalTimeOff=480 #TW
iGZip=1
iRemoveQfile=1
mapQS={}
def loopReadFromStdin():
	global mapQS
	tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
	begDT = '2000-1-1'
	endDT = '2037-1-1'
	if ('BEG' in mapQS):
		begDT=mapQS['BEG']
	if ('END' in mapQS):
		endDT=mapQS['END']
	subprocess.call("./q1minall.sh '%s' '%s' '%s' '%s' '%d'" % (szSymbol,begDT,endDT,tmpFile,iGZip), shell=True, cwd=szBinDir)

	if (iGZip==1):
		tmpFile = tmpFile+".gz"
		filesize=os.path.getsize(tmpFile)
		sys.stdout.write("Content-Length: %d\r\n" % filesize)
		sys.stdout.write("Content-Encoding: gzip\r\n")
	else:
		pass
	sys.stdout.write("Content-Type: text/plain\r\n")
	sys.stdout.write("\r\n")
	fp = file(tmpFile, 'rb')
	sys.stdout.write(fp.read())
	sys.stdout.flush()
	
	if (iRemoveQfile==1):
		os.remove(tmpFile)

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
if 'symbol' in mapQS:
	szSymbol = mapQS['symbol']
if 'timeoffset' in mapQS:
	timeoffset = int(mapQS['timeoffset'])
loopReadFromStdin();
