#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster

def _LocalDT2EOPCHFloat(localDT):
    return float(localDT.strftime('%s.%f'))

def _utcDTtoEOPCHFloat(utcDT):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utcDT = utcDT.replace(tzinfo=from_zone)

    # Convert time zone
    localDT = utcDT.astimezone(to_zone)

    return float(localDT.strftime('%s.%f'))

def _main(keyspace, table, symbol, begDTStr, endDTStr):
    retObj = {'range':[_LocalDT2EOPCHFloat(parser.parse(begDTStr)), _LocalDT2EOPCHFloat(parser.parse(endDTStr))], 'data':[], 'symbol':symbol, 'type':table, 'qcmd':''}

    begDTStr = datetime.fromtimestamp(retObj['range'][0])
    ednDTStr = datetime.fromtimestamp(retObj['range'][1])

    cluster = Cluster()
    session = cluster.connect(keyspace)
    queryStr = "select * from %s.%s where symbol='%s' and datetime>='%s' and datetime<'%s' order by datetime limit 20000;"%(keyspace, table, symbol, begDTStr, endDTStr)
    retObj['qcmd'] = queryStr
    #print queryStr
    result = session.execute(queryStr)
    if result is None or len(result.current_rows)<=0:
        return retObj

    if table in ['minbar','secbar']:
        for onerow in result:
            retObj['data'].append({'dt':_utcDTtoEOPCHFloat(onerow.datetime), 'o':onerow.open, 'h':onerow.high, 'l':onerow.low, 'c':onerow.close, 'v':onerow.vol})
    elif table == 'tick':
        for onerow in result:
            if onerow.type == 1:
                retObj['data'].append({'dt':_utcDTtoEOPCHFloat(onerow.datetime), 'c':onerow.keyval['C'], 'v':onerow.keyval['V']})
    return retObj 


querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        if qs.find("=") <= 0: continue
        mapQS[qs.split("=")[0]] = urllib.unquote(qs.split("=")[1])
if 'symbol' not in mapQS:
        mapQS['symbol'] = 'XX??'
if 'type' not in mapQS:
        mapQS['type'] = 'minbar'
if 'BEG' not in mapQS:
        mapQS['BEG'] = datetime.now().strftime('%Y-%m-%d')
if 'END' not in mapQS:
        mapQS['END'] = datetime.now().strftime('%Y-%m-%d')

retObj = _main('tqdb1', mapQS['type'], mapQS['symbol'], mapQS['BEG'], mapQS['END'])


sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(retObj))
sys.stdout.flush()

