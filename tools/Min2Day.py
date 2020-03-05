import time
import sys
import time
import datetime
import re
param={'MarketOpen': 84500, 'MarketClose': 134500, 'Debug': False}
dailyData={}
def _getTradeDateByMkOMkC(iDate, iTime, iMkO, iMkC):
	d = datetime.date(iDate/10000, (iDate/100)%100, iDate%100)
	if iMkO==iMkC:
		iMkCSec = (iMkO/10000)*60*60 + ((iMkO/100)%100)*60 +(iMkO%100)
		iMkOSec = iMkCSec - 1
		if iMkOSec < 0: iMkOSec = 86400-1
		iMkO = (iMkOSec/60/60)*10000+((iMkOSec/60)%60)*100+(iMkOSec%60)
	if (iMkC > iMkO):
		if (iTime>=iMkO and iTime < iMkC):
			return d.year*10000+d.month*100+d.day
		else:
			return -1
	elif (iMkC < iMkO):
		if (iTime<iMkC):
			d -= datetime.timedelta(days=1)
		elif (iTime>=iMkO):
			pass
		else:
			return -1
		return d.year*10000+d.month*100+d.day
	return -1
		
def _updateData(iDate, iTime, dbOpen, dbHigh, dbLow, dbClose, dbVol):
	global param, dailyData
	iTrgDate = _getTradeDateByMkOMkC(iDate, iTime, param['MarketOpen'], param['MarketClose']);        
	if iTrgDate == -1:
		if (param['Debug']):
			print "Invalid data: %s" % str((iDate, iTime, dbOpen, dbHigh, dbLow, dbClose, dbVol))
		return
	dt = datetime.datetime(iDate/10000, (iDate/100)%100, iDate%100, iTime/10000, (iTime/100)%100, iTime%100)	
	if iTrgDate not in dailyData:
		dailyData[iTrgDate]=[dt, dbOpen, dbHigh, dbLow, dbClose, dbVol]
	else:
		oneDay = dailyData[iTrgDate]
		oneDay[0] = dt
		if oneDay[2] < dbHigh: oneDay[2] = dbHigh
		if oneDay[3] > dbLow: oneDay[3] = dbLow
		oneDay[4] = dbClose
		oneDay[5] += dbVol
 
def loopReadFromStdin():
	iLineCnt = 0
	for line in sys.stdin:
		linesplit = line.replace('\r','').replace('\n','').split(',')
		if (len(linesplit)<6):
			continue

		iDate = int(linesplit[0])
		iTime = int(linesplit[1])
		dbOpen = float(linesplit[2])
		dbHigh = float(linesplit[3])
		dbLow = float(linesplit[4])
		dbClose = float(linesplit[5])
		dbVol = 0
		if len(linesplit)>=7: dbVol = float(linesplit[6])

		_updateData(iDate, iTime, dbOpen, dbHigh, dbLow, dbClose, dbVol)
		iLineCnt = iLineCnt+1
	if (param['Debug']):
		print("Processed %d bars"%iLineCnt)



param['MarketOpen']=int(sys.argv[1]);
param['MarketClose']=int(sys.argv[2]);
if (len(sys.argv)>3 and int(sys.argv[3])>0):
	param['Debug'] = True
loopReadFromStdin();
keys = dailyData.keys()
keys.sort()
for key in keys:
	val = dailyData[key]
	if (param['Debug']):
		print "%d,%.9f,%.9f,%.9f,%.9f,%f,%s" % (key, val[1], val[2], val[3], val[4], val[5], val[0])
	else:
		print "%d,%.9f,%.9f,%.9f,%.9f,%f" % (key, val[1], val[2], val[3], val[4], val[5])
