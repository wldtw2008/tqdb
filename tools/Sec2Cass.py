import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import re
szCassIP1=""
szCassDB=""
szCassTable="secbar"
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
	iShowInsertLog=0
	print("Ready to insert sec bars to db")
	for line in sys.stdin:
		linesplit = line.replace('\r','').replace('\n','').split(',')
		if (len(linesplit)<3):
			linesplit = line.replace('\r','').replace('\n','').split(' ')
		iYYYYMMDD = -1
		iHHMMSS = -1
		try:
			testSplit = linesplit[0].split('/')
			if (iYYYYMMDD==-1 and len(testSplit) == 3):
				iYYYYMMDD = int(testSplit[0])*10000+int(testSplit[1])*100+int(testSplit[2])
			if (iYYYYMMDD==-1):
				iYYYYMMDD = int(linesplit[0])

			testSplit = linesplit[1].split(':')
			if (iHHMMSS==-1 and len(testSplit) == 3):
				iHHMMSS = int(testSplit[0])*10000+int(testSplit[1])*100+int(testSplit[2])
			if (iHHMMSS==-1):
				iHHMMSS = int(linesplit[1])
		except:
			pass

		if (iYYYYMMDD==-1 or iHHMMSS == -1):
			print("Invalid date or time> date:%d time:%d, from '%s'" % (iYYYYMMDD, iHHMMSS, linesplit))
			continue

		dt = datetime.datetime(iYYYYMMDD/10000, (iYYYYMMDD/100)%100, iYYYYMMDD%100, iHHMMSS/10000, (iHHMMSS/100)%100, iHHMMSS%100)
		tagTime = int(dt.strftime("%s"))*1000
		#print int(round(time.time() * 1000)) 
		#print timetag 
		straa="insert into %s (symbol, datetime, open, high, low, close, vol) values ('%s', %d, %.9f, %.9f, %.9f, %.9f, %f);" % (szCassTable, szSymbol, tagTime, float(linesplit[2]), float(linesplit[3]), float(linesplit[4]), float(linesplit[5]), float(linesplit[6]))
		#print straa
		iLineCnt = iLineCnt+1
		
		session.execute(straa)
		iShowInsertLog = 0
		if (iLineCnt<10):
			iShowInsertLog=1
		elif (iLineCnt<100 and (iLineCnt%10) == 0):
			iShowInsertLog=1
		elif (iLineCnt<1000 and (iLineCnt%100) == 0):
			iShowInsertLog=1
		elif ((iLineCnt%1000) == 0):
			iShowInsertLog=1
		if (iShowInsertLog!=0):
			print("Ineserted %d Bars"%iLineCnt)
		#print mapData
		#mTable.insert(mapData)
		#put wtx.c 1417096644358 9002
		if (str2KairosDB != ""):
			sys.stdout.write(str2KairosDB)
			sys.stdout.flush()

	print("Ineserted %d Bars"%iLineCnt)
szCassIP1=sys.argv[1];
szCassPort=sys.argv[2];
szCassDB=sys.argv[3];
szSymbol=sys.argv[4];
#szCassTable=sys.argv[5];

loopReadFromStdin();
