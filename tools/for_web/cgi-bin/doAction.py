#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2,cgi,cgitb,subprocess
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster

def _main(keyspace, cmd, params):
    retObj = {'Result': 'Error! Wrong cmd!', 'Detail':None}
    if cmd in ('TQALERT_MUTE', 'TQALERT_UNMUTE'):
        retObj['Detail'] = {'Succeed':[], 'Failed':[]}
        params = params.replace('/', '_') #for security issue
        allSyms = params.split(',')
        for sym in allSyms:
            sym = sym.strip()
            filename = '/tmp/TQAlert/TQAlert.skip.%s' % sym
            try:
                if cmd == 'TQALERT_MUTE': #MUTE!!
                    with open(filename, 'w') as f:
                        f.write('1\n')
                    subprocess.call(['chmod', '0777', filename])
                else: #UN-MUTE
                    os.remove(filename)
                retObj['Detail']['Succeed'].append(sym)
            except:
                retObj['Detail']['Failed'].append(sym)
                pass
        retObj['Result'] = 'OK';
    if cmd in ('TQALERT_TESTCMD'):
        filename = '/tmp/TQAlert/TQAlert.testcmd.%s' % params
        with open(filename, 'w') as f:
            f.write('1\n')
        subprocess.call(['chmod', '0777', filename])
        retObj['Result'] = 'OK';
        
    return retObj

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])

#debug
mapQS['cmd'] = 'TQALERT_MUTE';
mapQS['params']='WTX,WTE '

allNeedParam = {'cmd':'', 'params':''}
for key in allNeedParam.keys():
    if key in mapQS:
        allNeedParam[key] = mapQS[key]
if (True):
    form = cgi.FieldStorage()
    for key in allNeedParam.keys():
        valFromFS = form.getvalue(key)
        if valFromFS is not None: allNeedParam[key] = valFromFS

retObj = _main('tqdb1', allNeedParam['cmd'], allNeedParam['params'])

sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()

