#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2,cgi,cgitb,subprocess
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster

def _main(keyspace, confKey, confVal, cmd):
    cluster = Cluster()
    session = cluster.connect(keyspace)
    qResult = None
    if cmd in ('UPDATE'):
        cqlCmd = "update %s.conf set confVal='%s' where confKey='%s'" % (keyspace, confVal.replace('"', '&quot;').replace('\'', '&apos;').replace('\\', '&bsol;'), confKey)
        try:
            eResult = session.execute(cqlCmd)
            filename = '/tmp/TQAlert/TQAlert.confchange'
            try:
                subprocess.call(['rm', '-f', filename])
                with open(filename, 'w') as f:
                    f.write('%s\n' % datetime.now().strftime('%s'))
                subprocess.call(['chmod', '0777', filename])
            except:
                pass
        except:
            return {'Result': 'Error! Failed to excute [%s]!'%cqlCmd}
        return {'Result': 'OK'}
    elif cmd in ('QUERY'):
        queryStr = "select confVal from %s.conf where confKey='%s'" %(keyspace, confKey)
        try:
            qResult = session.execute(queryStr)
        except:
            return {'Result': 'Error! Failed to excute [%s]!'%queryStr}
        if qResult is None or len(qResult.current_rows)<=0:
            return {'Result': 'Error! No Such Data'}
        return {'Result': 'OK', 'confVal':qResult[0][0].replace('&quot;', '"').replace('&apos;', '\'').replace('&bsol;', '\\')}

    return {'Result': 'Error! Wrong cmd!'}

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])

#debug
#mapQS['confKey'] = 'tqalert';
#mapQS['cmd']='QUERY'

allNeedParam = {'confKey':'', 'confVal':'', 'cmd':''}
for key in allNeedParam.keys():
    if key in mapQS:
        allNeedParam[key] = mapQS[key]
if (True):
    form = cgi.FieldStorage()
    for key in allNeedParam.keys():
        valFromFS = form.getvalue(key)
        if valFromFS is not None: allNeedParam[key] = valFromFS

retObj = _main('tqdb1', allNeedParam['confKey'], allNeedParam['confVal'], allNeedParam['cmd'])

sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()

