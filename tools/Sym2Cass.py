import json
import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import re
szCassIP1=""
szCassDB=""
szSymbol = ""
dictSymbolInfo = {}
def deleteSymbol():
        cluster = Cluster([szCassIP1])
        session = cluster.connect()
        session.set_keyspace(szCassDB)
        session.execute("delete from %s.symbol where symbol='%s'" % (szCassDB, szSymbol))
        print("Delete done.")
 
def insertOrUpdateSymbol():
	cluster = Cluster([szCassIP1])
	session = cluster.connect()
	session.set_keyspace(szCassDB)

	szKeyVal = '{}'
	if True:
		param = {'DESC':"", 'BPV':'1', 'MKO':'0', 'MKC':'0', 'SSEC':'0'}
		for key in param.keys():
			if key in dictSymbolInfo:
				param[key] = dictSymbolInfo[key]		
       		szKeyVal = json.dumps(param).replace('"', "'") 
        cqlCmd = "select * from %s.symbol where symbol='%s'" % (szCassDB, szSymbol)
        result = session.execute(cqlCmd)
        if result != None and len(result.current_rows)>0:
		cqlCmd = "update %s.symbol set keyval=%s where symbol='%s'" %(szCassDB, szKeyVal, szSymbol)
	else:
		cqlCmd = "insert into %s.symbol (symbol, keyval) values ('%s', %s)" % (szCassDB, szSymbol, szKeyVal)
        #print "----CMD=%s"%cqlCmd
	session.execute(cqlCmd)
        if cqlCmd[0]=='i':
		print("Inserted done.")
        else:
                print("Updated done.")

szCassIP1=sys.argv[1]
szCassPort=sys.argv[2]
szCassDB=sys.argv[3]
szSymbol=sys.argv[4]

if sys.argv[5].lower() == 'delete':
    deleteSymbol()
else:
    try:
        szSymbolInfo=sys.argv[5]
        dictSymbolInfo = json.loads(szSymbolInfo)
    except:
        print("Error in parse SymbolInfo!!")
    insertOrUpdateSymbol()
