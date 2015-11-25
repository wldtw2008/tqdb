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
#querystrings="sym=WTX&desc=Taifex&bpv=200&mko=84500&mkc=134500"
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]

sym=''
if 'sym' in mapQS: sym=mapQS['sym']
param = {'DESC':"", 'BPV':'0.0', 'MKO':'0', 'MKC':'0'}
if 'desc' in mapQS: param['DESC']=mapQS['desc']
if 'bpv' in mapQS: param['BPV']=mapQS['bpv']
if 'mko' in mapQS: param['MKO']=mapQS['mko']
if 'mkc' in mapQS: param['MKC']=mapQS['mkc']

if sym != '':
	tmpFile="/tmp/isym.%d.%d.cql"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
	sql="insert into %s.symbol (symbol,keyval) VALUES ('%s', %s);" % (szCassDB, sym, str(param))
	#print "sql--->%s"%sql
	szCMD="echo \"%s\" > %s" % (sql, tmpFile)
	subprocess.call(szCMD, shell=True, cwd='/tmp')

	szCMD="./cqlsh < %s >/dev/null"%(tmpFile)
	subprocess.call(szCMD, shell=True, cwd='/var/cassandra/bin/')

sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
#sys.stdout.write('aaa')
sys.stdout.write("<html><body><script language='javascript'>location.href='/cgi-bin/esymbol.py'</script></body></html>")
sys.stdout.write("\r\n")
sys.stdout.flush()
