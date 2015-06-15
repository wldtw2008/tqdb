import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster

szCassIP1=""
szCassDB=""
szCassTable="minbar"
szSymbol = "";	
def loopReadFromStdin():
	#mongoClient = pymongo.MongoClient('mongodb://192.168.1.217/TQDB')
	#mDB = mongoClient['TQDB']
        #mTable = mDB['DATA']
	#mTable = mongoClient['DATA']
	#cluster = Cluster(['192.168.1.217'])
	cluster = Cluster([szCassIP1])
	session = cluster.connect()
	#session.set_keyspace('test1')
	session.set_keyspace(szCassDB)

	str2KairosDB = ""
	iLineCnt=0
	for line in sys.stdin:
		linesplit = line.replace('\r','').replace('\n','').split(',')
		iYYYYMMDD = int(linesplit[0])
		iHHMMSS = int(linesplit[1])
		dt = datetime.datetime(iYYYYMMDD/10000, (iYYYYMMDD/100)%100, iYYYYMMDD%100, iHHMMSS/10000, (iHHMMSS/100)%100, iHHMMSS%100)
		tagTime = int(dt.strftime("%s"))*1000
		#print int(round(time.time() * 1000)) 
		#print timetag 
		straa="insert into %s (symbol, datetime, open, high, low, close, vol) values ('%s', %d, %f, %f, %f, %f, %f);" % (szCassTable, szSymbol, tagTime, float(linesplit[2]), float(linesplit[3]), float(linesplit[4]), float(linesplit[5]), float(linesplit[6]))
		#print straa
		iLineCnt = iLineCnt+1
		if ((iLineCnt%1000) == 0):
			print("Ineserted %d Bars"%iLineCnt)
		session.execute(straa)
		#print mapData
		#mTable.insert(mapData)
		#put wtx.c 1417096644358 9002
		if (str2KairosDB != ""):
			sys.stdout.write(str2KairosDB)
			sys.stdout.flush()


szCassIP1=sys.argv[1];
szCassPort=sys.argv[2];
szCassDB=sys.argv[3];
szSymbol=sys.argv[4];
#szCassTable=sys.argv[5];

loopReadFromStdin();
