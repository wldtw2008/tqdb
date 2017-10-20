#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import urllib

szBinDir='/home/tqdb/codes/tqdb/tools/'
szSymbol = "SIN"; #"TXO;201506;9200P";
timeoffset=0	
iLocalTimeOff=480 #TW
iGZip=1
iRemoveQfile=1
begDT = '2016-5-23 11:45:00'
endDT = '2016-5-23 21:46:00'
fileType = 0 #0=gz 1=csv
mapQS={}
def loopReadFromStdin():
	global mapQS
	tmpFile="/tmp/q1sec.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
	subprocess.call("./q1secall.sh '%s' '%s' '%s' '%s' '%d'" % (szSymbol,begDT,endDT,tmpFile,iGZip), shell=True, cwd=szBinDir)

	if (iGZip==1):
		tmpFile = tmpFile+".gz"
		filesize=os.path.getsize(tmpFile)
		sys.stdout.write("Content-Length: %d\r\n" % filesize)
		sys.stdout.write("Content-Encoding: gzip\r\n")
	else:
		pass
        if (fileType==0):
                sys.stdout.write("Content-Type: text/plain\r\n")
        else:
                sys.stdout.write("Content-Type: text/csv\r\n")
                sys.stdout.write("Content-Disposition: attachment; filename=\"%s.1sec.csv\"\r\n"%szSymbol);
	sys.stdout.write("\r\n")
	fp = file(tmpFile, 'rb')
	sys.stdout.write(fp.read())
	sys.stdout.flush()
	
	if (iRemoveQfile==1):
		os.remove(tmpFile)

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
if 'symbol' in mapQS:
	szSymbol = mapQS['symbol']
if 'timeoffset' in mapQS:
	timeoffset = int(mapQS['timeoffset'])
if ('BEG' in mapQS):
        begDT=mapQS['BEG']
if ('END' in mapQS):
        endDT=mapQS['END']
if ('csv' in mapQS):
    if mapQS['csv']=='1':
        fileType = 1
        iGZip = 0

loopReadFromStdin();
