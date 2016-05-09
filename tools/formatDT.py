#this python file can read from stdin and normailize the datetime to YYYYMMDD, HHMMSS.sss, O, H, L, C, V ...

import time
import sys
import time
import datetime
import re
def formatDate(strDate):
    iDate = 0
    tmpSplits = strDate.split('/')
    if len(tmpSplits) == 3:
        iDate = int(tmpSplits[0])*10000+int(tmpSplits[1])*100+int(tmpSplits[2])
        return str(iDate)

    if len(strDate) == 8:
        iDate = int(strDate)
        return str(iDate)
    return ""

def formatTime(strTime):
    hh,mm,ss,ms=(0,0,0,0)
    tmpSplits = strTime.split(':')
    if len(tmpSplits) == 3:
        if tmpSplits[2].find('.')>0:
            ssms=tmpSplits[2].split('.')
            hh,mm,ss,ms=(int(tmpSplits[0]), int(tmpSplits[1]), int(ssms[0]), int(ssms[1]))
        else:
            hh,mm,ss,ms=(int(tmpSplits[0]), int(tmpSplits[1]), int(tmpSplits[2]), 0)

    return "%02d%02d%02d.%d"%(hh,mm,ss,ms)

def loopReadFromStdin():
    for line in sys.stdin:
        tags = line.strip().split(',')
        tags[0] = formatDate(tags[0])
        tags[1] = formatTime(tags[1])
        if tags[0] == "": continue
        for i in range(2, len(tags)):
            tags[i] = str(float(tags[i]))
        print ",".join(tags)

loopReadFromStdin();
