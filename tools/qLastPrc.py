#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys
from datetime import datetime
from dateutil import tz
from cassandra.cluster import Cluster

lastInfo = {'minbar':(None, None, None), 'tick':(None, None, None), 'last':(None, None, None)}
def _utcDTtoLocalHuman(utcDT):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utcDT = utcDT.replace(tzinfo=from_zone)

    # Convert time zone
    localDT = utcDT.astimezone(to_zone)

    return localDT.strftime("%Y%m%d %H%M%S.%f")
def _utcDTtoEOPCH(utcDT):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utcDT = utcDT.replace(tzinfo=from_zone)

    # Convert time zone
    localDT = utcDT.astimezone(to_zone)
    return int(float(localDT.strftime("%s.%f"))*1000)

 
def _main(keyspace, symbol):
    global lastInfo
    cluster = Cluster()
    session = cluster.connect(keyspace)
    result = session.execute("select * from %s.minbar where symbol='%s' order by datetime desc limit 1;"%(keyspace,symbol))
    if result != None and len(result.current_rows)>0:
        utcDT = result[0].datetime
        last = result[0].close
        lastInfo['minbar'] = (_utcDTtoLocalHuman(utcDT), _utcDTtoEOPCH(utcDT), last)

    result = session.execute("select * from %s.tick where symbol='%s' order by datetime desc limit 1;"%(keyspace,symbol))
    if result != None and len(result.current_rows)>0:
        utcDT = result[0].datetime
        last = result[0].keyval['C'] 
        lastInfo['tick'] = (_utcDTtoLocalHuman(utcDT), _utcDTtoEOPCH(utcDT), last)

    for key in lastInfo.keys():
        if lastInfo[key][1] != None and (lastInfo['last'][1]==None or lastInfo[key][1]>lastInfo['last'][1]):
            lastInfo['last'] = (lastInfo[key][0], lastInfo[key][1], lastInfo[key][2])
_main('tqdb1', sys.argv[1])
#print lastInfo
for key in ('last', 'tick', 'minbar'):
    if lastInfo[key][0] == None:
        print("%s,-1,-1,-1"%(key))
    else:
        print("%s,%s,%d,%f"%(key, lastInfo[key][0], lastInfo[key][1], lastInfo[key][2]))
