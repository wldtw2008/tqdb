#!/usr/bin/python
import sys, subprocess 

def doConv(tzFrom, tzTo, csvFile):
    allCsvData = []
    allDtStr = []
    allConvedTZ = []
    with open(csvFile, "r") as f:
        lines = f.readlines();
        for line in lines:
            cols = line.strip().split(',');
            if (len(cols)>2):
                d = 0
                t = 0 
                try:
                    d = int(cols[0])
                    t = int(cols[1])
                except:
                    pass
                if d==0 or t==0:
                    continue
                dtstr = "%04d-%02d-%02d %02d:%02d:%02d" % (d/10000,(d/100)%100,d%100,t/10000,(t/100)%100,t%100)
                allCsvData.append(cols)
                allDtStr.append(dtstr)
    runCmd = "/home/tqdb/codes/tqdb/tools/tzconv -s '%s' -t '%s' -stdin -f 1 " % (tzFrom, tzTo) 
    process = subprocess.Popen(runCmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    convedStdout = process.communicate(input='\n'.join(allDtStr))[0]
    for convedLine in convedStdout.split('\n'):
        if len(convedLine)<8:
            continue
        allConvedTZ.append(convedLine.split(' '))

    if len(allCsvData) == len(allDtStr) and len(allCsvData) == len(allConvedTZ):
        for i in range(0,len(allCsvData)):
            allCsvData[i][0] = allConvedTZ[i][0]
            allCsvData[i][1] = allConvedTZ[i][1]
    for i in range(0,len(allCsvData)):
        print '%s' % ','.join(allCsvData[i])
    return

if len(sys.argv)<4:
    print "error params!"
    exit(0)
doConv(sys.argv[1], sys.argv[2], sys.argv[3])
#doConv('local', 'UTC', '/tmp/1_1_scn006207.csv')
