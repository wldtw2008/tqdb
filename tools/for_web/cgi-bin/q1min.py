#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import urllib, urllib2, json

szBinDir='/home/tqdb/codes/tqdb/tools/'
szSymbol = "WTF.506" #"^^NKTOPX" #"SIN"; #"TXO;201506;9200P";
timeoffset=0	
iLocalTimeOff=480 #TW
iGZip=1
iRemoveQfile=1
begDT = '2030-5-23 11:45:00'
endDT = '2030-5-23 21:46:00'
fileType = 0 #0=gz 1=csv
mapQS={}
def getFirstValidDateTime(symbol, begDTstr, endDTstr):
    trgType = 'MinBar'
    begRefDT, endRefDT = (-1, -1)
    url = 'http://127.0.0.1/cgi-bin/qSymRefPrc.py?symbol=%s&qType=LastValidPrc&qDatetime=%s' % (urllib2.quote(symbol), urllib2.quote(begDTstr))
    resp = urllib2.urlopen(url)
    obj = json.loads(resp.read())
    #print obj
    if obj != None and trgType in obj and obj[trgType][0] != None:
        begRefDT = obj[trgType][0]['datetime']
    url = 'http://127.0.0.1/cgi-bin/qSymRefPrc.py?symbol=%s&qType=LastValidPrc&qDatetime=%s' % (urllib2.quote(symbol), urllib2.quote(endDTstr))
    resp = urllib2.urlopen(url)
    obj = json.loads(resp.read())
    #print obj
    if obj != None and trgType in obj and obj[trgType][0] != None:
        endRefDT = obj[trgType][0]['datetime']
    if begRefDT != -1 and begRefDT == endRefDT:
        begRefDTobj = datetime.datetime.strptime(begRefDT, "%Y-%m-%d %H:%M:%S")
        begRefDTEopch = (begRefDTobj - datetime.datetime(1970,1,1)).total_seconds()
        dtFirstValid = datetime.datetime.fromtimestamp(begRefDTEopch)
        begDTstr = dtFirstValid.strftime("%Y-%m-%d %H:%M:%S")
    return begDTstr

def downloadFromTQDB(tmpFile):
	subprocess.call("./q1minall.sh '%s' '%s' '%s' '%s' '%d'" % (szSymbol,begDT,endDT,tmpFile,iGZip), shell=True, cwd=szBinDir)

def doCustomSymbol(tmpFile): 
	profile = 'profile.ml.%s' % (szSymbol[2:])
	subprocess.call("python ./q1min_multileg.py '%s' '%s' '%s' '%s' '%d'" % (profile,begDT,endDT,tmpFile,iGZip), 
			shell=True, cwd="%s/../../tqdbPlus/" % szBinDir)
	
def loopReadFromStdin(tmpFile):
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
                sys.stdout.write("Content-Disposition: attachment; filename=\"%s.1min.csv\"\r\n"%szSymbol);
	sys.stdout.write("\r\n")
        if (fileType==0):
		pass
	else:
		sys.stdout.write("YYYYMMDD,HHMMSS,Open,High,Low,Close,Vol\r\n")
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

# if symbol is begin of ^^, it is a customer symbol !
isCustomerSymbol = True if szSymbol.find('^^') == 0 else False
if not isCustomerSymbol:
    #typo !!
    if ('MOSTHAVEBEG' in mapQS and mapQS['MOSTHAVEBEG'] != '0'):
        begDT = getFirstValidDateTime(szSymbol, begDT, endDT)
    if ('MUSTHAVEBEG' in mapQS and mapQS['MUSTHAVEBEG'] != '0'):
        begDT = getFirstValidDateTime(szSymbol, begDT, endDT)

tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
if isCustomerSymbol:
	doCustomSymbol(tmpFile)
else:
	downloadFromTQDB(tmpFile)

loopReadFromStdin(tmpFile)
