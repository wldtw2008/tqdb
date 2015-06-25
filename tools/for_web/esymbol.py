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

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]

sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
tmpFile="/tmp/q1min.%d.%d"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
szCMD="./qsym %s %s %s.symbol 0 ALL 1 > %s" % (szCassIP1, '9042', szCassDB, tmpFile)
subprocess.call(szCMD, shell=True, cwd='/home/tqdb/codes/tqdb/tools/') 
fp = file(tmpFile, 'rb')
jsonstr=fp.read()
os.remove(tmpFile)
allObjs = json.loads(jsonstr.replace("'",'"'))

sys.stdout.write("<html><body>\n")
sys.stdout.write("<script language='javascript'>\n")
sys.stdout.write("function doupdate(idx, sym){\n")
sys.stdout.write("desc=document.getElementById('desc'+idx).value\n")
sys.stdout.write("bpv=1*document.getElementById('bpv'+idx).value\n")
sys.stdout.write("//alert('ready to update: '+sym+', desc:'+desc+', bpv:'+bpv)\n")
sys.stdout.write("location.href='/cgi-bin/usymbol.py?sym='+encodeURI(sym)+'&desc='+desc+'&bpv='+bpv;\n")
sys.stdout.write("}\n")
sys.stdout.write("</script>\n")
sys.stdout.write("<table border=0><tr><td>Symbol</td><td>Desc.</td><td>BigPointVal</td><td>Action</td></tr>\n");
iIDX = 0;
for obj in allObjs:
	
	sym=obj['symbol']
	desc=""
	if ('DESC' in obj['keyval']):
		desc = obj['keyval']['DESC']
	bpv=""
	if ('BPV' in obj['keyval']):
		bpv=obj['keyval']['BPV']
	print("<tr><td>%s</td><td><input type='text' id='desc%d' value='%s'></td><td><input type='text' id='bpv%d' value='%s'></td><td><button type='button' value='%s' onclick=\"doupdate(%d, '%s')\">Update</button></td></tr>\n" % (sym, iIDX, desc, iIDX, bpv,sym, iIDX, sym))
	iIDX = iIDX+1
sys.stdout.write("</table></body></html>\n")
sys.stdout.flush()
