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
import urllib
szCassIP1="127.0.0.1"
szCassPort1="9042"
szCassDB="tqdb1"

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
#querystrings="sym=WTX&desc=Taifex&bpv=200&mko=84500&mkc=134500"
mapQS={}
for qs in querystrings.split("&"):
	if qs.find("=") <= 0: continue
	mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
sym=''
if 'sym' in mapQS: sym=mapQS['sym']
param = {'DESC':"", 'BPV':'0.0', 'MKO':'0', 'MKC':'0', 'SSEC':'0'}
if 'desc' in mapQS: param['DESC']=mapQS['desc']
if 'bpv' in mapQS: param['BPV']=mapQS['bpv']
if 'mko' in mapQS: param['MKO']=mapQS['mko']
if 'mkc' in mapQS: param['MKC']=mapQS['mkc']
if 'ssec' in mapQS: param['SSEC']=mapQS['ssec']

if sym != '':
	szCMD="python Sym2Cass.py %s %s '%s' '%s' '%s' > /dev/null" % (szCassIP1, szCassPort1, szCassDB, sym, json.dumps(param))
	subprocess.call(szCMD, shell=True, cwd='/home/tqdb/codes/tqdb/tools/')

sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
#sys.stdout.write('aaa')
sys.stdout.write("<html><body><script language='javascript'>location.href='/esymbol.html'</script></body></html>")
sys.stdout.write("\r\n")
sys.stdout.flush()
