#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2,cgi,cgitb,subprocess
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster


szSymbol = "006207.TW"
def _executeQurey(cassSession, queryStr):
    retData = []
    try:
        qResult = cassSession.execute(queryStr)
    except:
        return {'Result': 'Error! Failed to excute [%s]!'%queryStr, 'data': retData}
    retRows = qResult.current_rows
    if qResult is None or len(retRows)<=0:
        return {'Result': 'Error! No Such Data', 'data': retData}
    
    for retOneRow in retRows:
        tmpDict = {}
        for i in range(0, len(qResult.column_names)):
            if retOneRow[i] is not None:
                tmpDict[qResult.column_names[i]] = str(retOneRow[i])
            else:
                tmpDict[qResult.column_names[i]] = None
        retData.append(tmpDict)
    return {'Result': 'OK', 'data': retData}

def _main(keyspace, sym):
    cluster = Cluster()
    session = cluster.connect(keyspace)
    allData = {} 

    queryStr = "select * from %s.tick where symbol='%s' order by datetime limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['TickBeg'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.tick where symbol='%s' order by datetime desc limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['TickEnd'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.secbar where symbol='%s' order by datetime limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['SecBeg'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.secbar where symbol='%s' order by datetime desc limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['SecEnd'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.minbar where symbol='%s' order by datetime limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['MinBeg'] =  retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.minbar where symbol='%s' order by datetime desc limit 10;" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['MinEnd'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']

    queryStr = "select * from %s.symbol where symbol='%s';" % (keyspace, sym)
    retData = _executeQurey(session, queryStr)
    allData['SymbolInfo'] = retData['data'] if retData['Result'] == 'OK' else ['Exception!']
    return allData

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
if 'symbol' in mapQS:
        szSymbol = mapQS['symbol']

retObj = _main('tqdb1', szSymbol)

sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()

