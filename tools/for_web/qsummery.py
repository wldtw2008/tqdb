#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import json
szCassIP1="127.0.0.1"
szCassDB="tqdb1"
szBinDir='/home/tqdb/codes/tqdb/tools/'

def runCql(szCql, objRet):
    p = subprocess.Popen(["/var/cassandra/bin/cqlsh", "-e", szCql], cwd="/var/cassandra/bin/",  
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    objRet['output'], objRet['err'] = p.communicate()
    objRet['retcode'] = p.returncode

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
#querystrings="sym=WTX&desc=Taifex&bpv=200&mko=84500&mkc=134500"
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]

sym='WTX'
if 'symbol' in mapQS: sym=mapQS['symbol']
qtype='ALL'
if 'qtype' in mapQS: qtype=mapQS['qtype']

if qtype == 'qLastPrc':
    cmd="%s '%s'" % (os.path.join(szBinDir, 'qLastPrc.py'), sym) 
    lastPrc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    sys.stdout.write("Content-Type: application/json\r\n")
    sys.stdout.write("\r\n%s"%lastPrc)
    #sys.stdout.write(cmd)
    sys.stdout.write("\r\n")
    sys.stdout.flush()
    exit(0)


summery={}
if sym != '':
	tmpFile="/tmp/qsummery.%d.%d.txt"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
        objRet = {}
	cql="select * from %s.tick where symbol='%s' order by datetime limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['tick.first'] = objRet['output']
        cql="select * from %s.tick where symbol='%s' order by datetime desc limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['tick.last'] = objRet['output']

        cql="select * from %s.secbar where symbol='%s' order by datetime limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['sec.first'] = objRet['output']
        cql="select * from %s.secbar where symbol='%s' order by datetime desc limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['sec.last'] = objRet['output']

        cql="select * from %s.minbar where symbol='%s' order by datetime limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['min.first'] = objRet['output']
        cql="select * from %s.minbar where symbol='%s' order by datetime desc limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['min.last'] = objRet['output']

        cql="select * from %s.symbol where symbol='%s';" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['summery'] = objRet['output']

sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
sys.stdout.write("<html>")
sys.stdout.write("<style type='text/css'>")
sys.stdout.write("<!--")
sys.stdout.write("body { background: #FFF; font-family: 'Lucida Console', Monaco, monospace;}")
sys.stdout.write("/-->")
sys.stdout.write("</style>")
sys.stdout.write("<body>")
#sys.stdout.write("<script language='javascript'>location.href='/esymbol.html'</script>")
sys.stdout.write("<table table border='1' style='border-collapse: collapse;' cellpadding='5'>")
sys.stdout.write("<tr style='background-color:#ccc'><td colspan='2'>Summery</td></tr>")
sys.stdout.write("<tr><td colspan='2'>%s</td></tr>"%summery['summery'].replace('\n','<br>'))

sys.stdout.write("<tr style='background-color:#ccc'><td colspan='2'>Tick</td></tr>")
sys.stdout.write("<tr><td>First 10 record</td><td>%s</td></tr><tr><td>Last 10 record</td><td>%s</td></tr>"%(summery['tick.first'].replace('\n','<br>'),summery['tick.last'].replace('\n','<br>')))

sys.stdout.write("<tr style='background-color:#ccc'><td colspan='2'>Sec</td></tr>")
sys.stdout.write("<tr><td>First 10 record</td><td>%s</td></tr><tr><td>Last 10 record</td><td>%s</td></tr>"%(summery['sec.first'].replace('\n','<br>'),summery['sec.last'].replace('\n','<br>')))

sys.stdout.write("<tr style='background-color:#ccc'><td colspan='2'>Min</td></tr>")
sys.stdout.write("<tr><td>First 10 record</td><td>%s</td></tr><tr><td>Last 10 record</td><td>%s</td></tr>"%(summery['min.first'].replace('\n','<br>'),summery['min.last'].replace('\n','<br>')))
sys.stdout.write("</table>")
sys.stdout.write("</body></html>")
sys.stdout.write("\r\n")
sys.stdout.flush()
