#!/usr/bin/env python
import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import os
import stat
import subprocess
import json
import cgi, os
import cgitb
cgitb.enable()

szCassIP1="127.0.0.1"
szCassDB="tqdb1"

param = {'Sym':'', 'Lines': [], 'Log':''}
importTicket="i1min.%d.%d"%(int(time.time()), os.getpid())
def _procPostData():
    global param
    form = cgi.FieldStorage()
    #param['Log'] = str(form)
    if 'file' in form:
        fileitem = form['file']
        while True:
            line = fileitem.file.readline()
            if not line: break
            onedata = line.strip('\n').strip('\r').split(',')
            if len(onedata)>=6:
                if len(onedata) == 6: onedata.append('0') #for vol
                param['Lines'].append(onedata)

    sym = form.getvalue('sym')
    if sym:
        param['Sym'] = sym

def _prepareImport():
    global param
    cmdfile = '/tmp/%s.cmd' % importTicket
    csvfile = '/tmp/%s.csv' % importTicket
    with open(cmdfile, 'w') as cmd:
        cmd.write('. /etc/profile.d/profile_tqdb.sh\n')
        cmd.write('TQDB="tqdb1"\n')
        cmd.write('SYMBOL="%s"\n'% param['Sym'])
        cmd.write('NDAYAGO=0\n')
        cmd.write('CMD="cat /tmp/%s.csv | python $TQDB_DIR/tools/Min2Cass.py $CASS_IP $CASS_PORT $TQDB \'$SYMBOL\'"\n' % importTicket)
        cmd.write('echo "Ready to run: "$CMD > /tmp/%s.log\n' % importTicket)
        cmd.write('eval $CMD >> /tmp/%s.log\n' % importTicket)
        cmd.write('cat /tmp/%s.log\n' % importTicket)
    os.chmod(cmdfile, os.stat(cmdfile).st_mode | stat.S_IEXEC)
    with open(csvfile, 'w') as csv:
        for onedata in param['Lines']:
            csv.write(','.join(onedata)+'\n')
_procPostData()
_prepareImport()
sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
if param['Sym'] == '':
    sys.stdout.write('<html><body>No Sym!</body></html>')
else:
    #sys.stdout.write('<html><body>No Sym!</body></html>')
    sys.stdout.write('<html><body>')
    sys.stdout.write('Sym:%s, TotalLines:%d<br>\n'%(param['Sym'], len(param['Lines'])))
    sys.stdout.write('<table border=1>\n')
    sys.stdout.write('<tr><td>No</td><td>Date</td><td>Time</td><td>Open</td><td>High</td><td>Low</td><td>Close</td><td>Vol</td></tr>\n')
    cnt = 0
    for onedata in param['Lines']:
       cnt += 1
       if cnt>100 and cnt<len(param['Lines'])-100:
          if cnt == 101:
              sys.stdout.write('<tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>\n')
          continue
       sys.stdout.write('<tr><td>#%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'%
                        (cnt, onedata[0], onedata[1], onedata[2], onedata[3], onedata[4], onedata[5], onedata[6]))
    sys.stdout.write('</table>\n')
    sys.stdout.write('<input type="button" onclick="location.href=\'/cgi-bin/i1min_do.py?importTicket=%s\'" value=\'Confirm importing!\'></input>\n'%importTicket)
    sys.stdout.write('</body></html>')
sys.stdout.write("\r\n")
sys.stdout.flush()
