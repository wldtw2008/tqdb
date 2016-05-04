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
szSymbol = "^^NKTOPX" #"SIN"; #"TXO;201506;9200P";
timeoffset=0	
iLocalTimeOff=480 #TW
iGZip=1
iRemoveQfile=1
begDT = '2016-1-1'
endDT = '2016-2-1'

mapQS={}
def downloadFromTQDB(tmpFile):
	subprocess.call("./q1minall.sh '%s' '%s' '%s' '%s' '%d'" % (szSymbol,begDT,endDT,tmpFile,iGZip), shell=True, cwd=szBinDir)

def doCustomSymbol(tmpFile): 
	profile = 'profile.ml.%s' % (szSymbol[2:])
	subprocess.call("python ./q1min_multilag.py '%s' '%s' '%s' '%s' '%d'" % (profile,begDT,endDT,tmpFile,iGZip), 
			shell=True, cwd="%s/../../tqdbPlus/" % szBinDir)
	
def loopReadFromStdin(tmpFile):
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
tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))


if szSymbol.find('^^') == 0: # if symbol is begin of ^^, it is a customer symbol !
	doCustomSymbol(tmpFile)
else:
	downloadFromTQDB(tmpFile)

loopReadFromStdin(tmpFile)
