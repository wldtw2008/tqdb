#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster

def _main(keyspace, table, symbol, EPOCHFloat, cmd, dataObj):
    cluster = Cluster()
    session = cluster.connect(keyspace)
    queryStr = ""
    qResult = None
    #return {'Result': str(dataObj)}
    if table in ['minbar','secbar']:
        queryStr = "select * from %s.%s where symbol='%s' and datetime=%d" %(keyspace, table, symbol, EPOCHFloat*1000)
    elif table == 'tick':
        queryStr = "select * from %s.%s where symbol='%s' and datetime=%d" %(keyspace, table, symbol, EPOCHFloat*1000)
    try:
        qResult = session.execute(queryStr)
    except:
        return {'Result': 'Error! Failed to excute [%s]!'%queryStr}
    if qResult is None or len(qResult.current_rows)!=1:
        return {'Result': 'Error! No Such Data'}
    if table == 'tick' and qResult[0].type != 1:
        return {'Result': 'Error! No Such Tick Data'}
 
    cqlCmd = ""
    if cmd == "DELETE":
        cqlCmd = "delete from %s.%s where symbol='%s' and datetime=%d"%(keyspace, table, symbol, EPOCHFloat*1000)
    elif cmd == "UPDATE":
        updatePart = ""
        if table in ['minbar','secbar']:
            allKeyVal = []
            for key in dataObj.keys():
                allKeyVal.append("%s=%s"%(key,str(dataObj[key])))
            updatePart = ",".join(allKeyVal)
        elif table == 'tick':
            keyvalList = []
            for key in qResult[0].keyval.keys():
                if key in dataObj:
                    keyvalList.append("'%s':%s" % (key, str(dataObj[key])))
                else:
                    keyvalList.append("'%s':%s" % (key, str(qResult[0].keyval[key])))

            updatePart = "keyval={%s}" % ",".join(keyvalList)
        cqlCmd = "update %s.%s set %s where symbol='%s' and datetime=%d"%(keyspace, table, updatePart, symbol, EPOCHFloat*1000)
    try:
        eResult = session.execute(cqlCmd)
    except:
        return {'Result': 'Error! Failed to excute [%s]!'%cqlCmd}
    return {'Result': 'OK'}

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
if 'symbol' not in mapQS:
        mapQS['symbol'] = 'XX??'
if 'type' not in mapQS:
        mapQS['type'] = 'minbar'
if 'epochFloat' not in mapQS:
        mapQS['epochFloat'] = '0'
if 'cmd' not in mapQS:
        mapQS['cmd'] = 'UPDATE'
if 'jsonObj' not in mapQS:
        mapQS['jsonObj'] = '{"open":0,"high":0,"low":0,"close":0,"vol":"0"}'

retObj = _main('tqdb1', mapQS['type'], mapQS['symbol'], float(mapQS['epochFloat']), mapQS['cmd'], json.loads(mapQS['jsonObj']))


sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()

