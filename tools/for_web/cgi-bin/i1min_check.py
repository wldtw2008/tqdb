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

    sym = form.getvalue('sym')
    if sym:
        param['Sym'] = sym
    tzConv = form.getvalue('tzConv')
    tzSelect = form.getvalue('tzSelect')

    if (tzConv == 'on' and tzSelect is not None and tzSelect != ''):
        param['tzFromTo'] = [tzSelect, 'local']
        try:
            with open('/etc/timezone', 'r') as f:
                param['tzFromTo'][1] = f.readline().strip()
        except:
            pass
    else:
        param['tzFromTo'] = None 

    if 'file' in form:
        fileitem = form['file']
        iYYYYMMDDType = 0 #0=yyyymmdd 1=yyyy-mm-dd 2=yyyy/mm/dd 3=mm/dd/yyyy
        iHHMMSSType = 0 #0=hhmmss 1=hh:mm:ss 2=hh:mm
        while True:
            line = fileitem.file.readline()
            if not line: break
            onedata = line.strip('\n').strip('\r').split(',')
            if len(onedata)>=6:
                #first tag should be date (length more then 8 and first byte should be a number)
                if len(onedata[0])<8: continue
                if onedata[0][0] < '0' or onedata[0][0] > '9': continue

                if len(param['Lines'])==0: #first line detacted date & time format
                    if len(onedata[0].split('-'))==3: iYYYYMMDDType=1
                    if len(onedata[0].split('/'))==3:
                         iYYYYMMDDType=2
                         try:
                             if int(onedata[0].split('/')[2])>1900: iYYYYMMDDType=3
                         except:
                             pass

                    if len(onedata[1].split(':'))==3: iHHMMSSType=1
                    if len(onedata[1].split(':'))==2: iHHMMSSType=2

                if iYYYYMMDDType==1:
                    _date=onedata[0].split('-')
                    onedata[0]="%08d"%(int(_date[0])*10000+int(_date[1])*100+int(_date[2]))
                elif iYYYYMMDDType==2:
                    _date=onedata[0].split('/')
                    onedata[0]="%08d"%(int(_date[0])*10000+int(_date[1])*100+int(_date[2]))
                elif iYYYYMMDDType==3:
                    _date=onedata[0].split('/')
                    onedata[0]="%08d"%(int(_date[2])*10000+int(_date[0])*100+int(_date[1]))

                if iHHMMSSType==1:
                    _time=onedata[1].split(':')
                    onedata[1]="%06d"%(int(_time[0])*10000+int(_time[1])*100+int(_time[2]))
                elif iHHMMSSType==2:
                    _time=onedata[1].split(':')
                    onedata[1]="%06d"%(int(_time[0])*10000+int(_time[1])*100)

                #try:#chech year
                #    year=int(onedata[0][0:4])
                #    if year<1900 or year>2030: continue
                #except:
                #    continue

                if len(onedata) == 6: onedata.append('0') #for vol
                param['Lines'].append(onedata)

    if param['tzFromTo'] is not None:
        with open('/tmp/%s.tzFrom'%importTicket, 'w') as csv:
            for onedata in param['Lines']:
                csv.write('%s\n' % ','.join(onedata))

        runCmd = "/home/tqdb/codes/tqdb/tools/csvtzconv.py '%s' '%s' '/tmp/%s.tzFrom' > /tmp/%s.tzTo" % (param['tzFromTo'][0], param['tzFromTo'][1], importTicket, importTicket)
        param['tzConvertCmd'] = runCmd
        subprocess.call(runCmd, shell=True)
        param['Lines'] = []
        with open('/tmp/%s.tzTo'%importTicket, 'r') as csv:
            for line in csv.readlines():
                param['Lines'].append(line.strip('\n').strip('\r').split(','))

def _prepareImport():
    global param
    cmdfile = '/tmp/%s.cmd' % importTicket
    csvfile = '/tmp/%s.csv' % importTicket
    with open(cmdfile, 'w') as cmd:
        cmd.write('. /etc/profile.d/profile_tqdb.sh\n')
        cmd.write('TQDB="tqdb1"\n')
        sym = param['Sym']
        sym = sym.replace('$', '\\$')
        cmd.write('SYMBOL="%s"\n'% sym)
        cmd.write('NDAYAGO=0\n')
        cmd.write('CMD="cat /tmp/%s.csv | python -u $TQDB_DIR/tools/Min2Cass.py $CASS_IP $CASS_PORT $TQDB \'$SYMBOL\'"\n' % importTicket)
        cmd.write('echo "Ready to run: "$CMD > /tmp/%s.log\n' % importTicket)
        cmd.write('eval $CMD >> /tmp/%s.log\n' % importTicket)
        cmd.write('echo "Importing finish!" >> /tmp/%s.log\n' % importTicket)
    os.chmod(cmdfile, os.stat(cmdfile).st_mode | stat.S_IEXEC)
    with open(csvfile, 'w') as csv:
        for onedata in param['Lines']:
            csv.write(','.join(onedata)+'\n')
_procPostData()
_prepareImport()

retObj = {'symbol':param['Sym'], 'totalCnt':len(param['Lines']), 'importTicket':importTicket, 'tzFrom':'', 'tzTo':'', 'first100Rows':[], 'last100Rows':[], 'tzConvertCmd':''}
if param['tzFromTo'] is not None:
    retObj['tzFrom'] = param['tzFromTo'][0]
    retObj['tzTo'] = param['tzFromTo'][1]
    retObj['tzConvertCmd'] = param['tzConvertCmd']
cnt = 0
for onedata in param['Lines']:
    cnt += 1
    if cnt<=100 or cnt>=retObj['totalCnt']-100:
        dtohlcv={'D':None, 'T':None, 'O':None, 'H':None, 'L':None, 'C':None, 'V':0, 'Idx':cnt}
        tags=['D', 'T', 'O', 'H', 'L', 'C', 'V']
        for i in range(0,len(tags)):
            try:
                dtohlcv[tags[i]] = onedata[i]
            except:
                pass
        dtohlcv['Idx'] = cnt
        if cnt<=100: retObj['first100Rows'].append(dtohlcv)
        if retObj['totalCnt']>100 and cnt>=retObj['totalCnt']-100: retObj['last100Rows'].append(dtohlcv)

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
    mapQS[qs.split("=")[0]] = qs.split("=")[1]


if 'html' in mapQS and mapQS['html']=='1':
    sys.stdout.write("Content-Type: text/html\r\n")
    sys.stdout.write("\r\n")
    if retObj['symbol'] == '':
        sys.stdout.write('<html><body>No Sym!</body></html>')
    else:
        sys.stdout.write('<html><body>')
        sys.stdout.write("<link rel='stylesheet' type='text/css' href='/style.css'>")
        sys.stdout.write('Sym:%s, TotalLines:%d, ImportTicket:%s<br>\n'%(retObj['symbol'], retObj['totalCnt'], retObj['importTicket']))
        if retObj['tzFrom'] != '':
            sys.stdout.write('<font color="#f00">Convert Timezone: %s ---> %s' % (retObj['tzFrom'], retObj['tzTo']))
        sys.stdout.write('<table>\n')
        sys.stdout.write('<tr class="grayThing smallfont"><td>No</td><td>Date</td><td>Time</td><td>Open</td><td>High</td><td>Low</td><td>Close</td><td>Vol</td></tr>\n')
        for dtohlcv in retObj['first100Rows']:
            sys.stdout.write('<tr onmouseover="this.className=\'yellowThing\';" onmouseout=\"this.className=\'whiteThing\';">')
            sys.stdout.write('<td>#%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' %
                            (dtohlcv['Idx'], dtohlcv['D'], dtohlcv['T'], dtohlcv['O'], dtohlcv['H'], dtohlcv['L'], dtohlcv['C'], dtohlcv['V']))
        if len(retObj['last100Rows'])>0:
            sys.stdout.write('<tr><td colspan="8">...</td>')
            for dtohlcv in retObj['last100Rows']:
                sys.stdout.write('<tr onmouseover="this.className=\'yellowThing\';" onmouseout=\"this.className=\'whiteThing\';">')
                sys.stdout.write('<td>#%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % 
                                (dtohlcv['Idx'], dtohlcv['D'], dtohlcv['T'], dtohlcv['O'], dtohlcv['H'], dtohlcv['L'], dtohlcv['C'], dtohlcv['V']))

        sys.stdout.write('</table>\n')
        sys.stdout.write('<input type="button" onclick="location.href=\'/cgi-bin/i1min_do.py?importTicket=%s\'" value=\'Confirm importing!\'></input>\n'%importTicket)
        sys.stdout.write('</body></html>')
    
else:
    sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()
