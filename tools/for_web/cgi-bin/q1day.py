#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import urllib
import json


szCassIP1="127.0.0.1"
szCassDB="tqdb1"

szBinDir='/home/tqdb/codes/tqdb/tools/'
szSymbol = "SIN"; #"TXO;201506;9200P";
iMkO=0
iMkC=0
timeoffset=0	
iLocalTimeOff=480 #TW
iGZip=1
iRemoveQfile=1
begDT = '2016-5-23 11:45:00'
endDT = '2016-5-23 21:46:00'
fileType = 0 #0=gz 1=csv
mapQS={}


def loopReadFromStdin():
	global mapQS,iMkO,iMkC,iRemoveQfile
	tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
	if ('MKO' in mapQS and 'MKC' in mapQS):
		iMkO = int(mapQS['MKO'])
		iMkC = int(mapQS['MKC'])
	if (iMkO==0 and iMkC ==0):#read from DB
		tmpFile="/tmp/qsym.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
		szCMD="./qsym %s %s %s.symbol 0 '%s' 1 > %s" % (szCassIP1, '9042', szCassDB, szSymbol, tmpFile)
		subprocess.call(szCMD, shell=True, cwd='/home/tqdb/codes/tqdb/tools/')
		fp = file(tmpFile, 'rb')
		jsonstr=fp.read()
		os.remove(tmpFile)
		#print jsonstr
		allObjs = json.loads(jsonstr.replace("'",'"'))

		if 'keyval' in allObjs[0] and \
		  'MKC' in allObjs[0]['keyval'] and 'MKO' in allObjs[0]['keyval'] :
			iMkO = int(allObjs[0]['keyval']['MKO'])
			iMkC = int(allObjs[0]['keyval']['MKC'])
			#print "---->%d,%d" % (iMkO,iMkC)
		#./q1dayall.sh WTX 2015-1-1 2015-6-15 /tmp/wtx.min 0 084500 134500

	szCMD = "./q1dayall.sh '%s' '%s' '%s' '%s' '%d' '%d' '%d'" \
	        % (szSymbol,begDT,endDT,tmpFile,iGZip,iMkO, iMkC)
	#print "--->%s"%szCMD
	subprocess.call(szCMD, shell=True, cwd=szBinDir)

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
                sys.stdout.write("Content-Disposition: attachment; filename=\"%s.1day.csv\"\r\n"%szSymbol);
	sys.stdout.write("\r\n")
	with open(tmpFile, 'rb') as fp:
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
