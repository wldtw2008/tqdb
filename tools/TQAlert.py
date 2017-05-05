#!/usr/bin/python
# -*- coding: utf-8 -*-   

import sys,json,os,urllib, urllib2,cgi,cgitb,math,time,subprocess
from datetime import datetime
from dateutil import tz, parser
from cassandra.cluster import Cluster

def _log(str):
    print(str)

def _readConfig(keyspace, allTimeRule, allAlertCmd):
    allTimeRule.clear()
    del allAlertCmd[:]
    cluster = Cluster()
    session = cluster.connect(keyspace)
    queryStr = "select confVal from %s.conf where confKey='tqconf'" %(keyspace)
    qResult = None
    try:
        qResult = session.execute(queryStr)
    except:
        _log('Error! Failed to excute [%s]!'%queryStr)
        return
        
    if qResult is None or len(qResult.current_rows)<=0:
        _log('Error! No Such Data')
        return

    objTQConf = json.loads(qResult[0][0].replace('&quot;', '"').replace('&apos;', '\'').replace('&bsol;', '\\'))
    for k,v in objTQConf['TimeRule'].items(): allTimeRule[k]=v
    for s in objTQConf['AlertCMD']: allAlertCmd.append(s) 
    # do log here
    if (True): #log setting
        _log("Time Rules:")
        for key in allTimeRule.keys():
            _log("    Symbol: %s" % key)
            for i in range(0, len(allTimeRule[key])):
                _log("        Rule#%d: %s" %(i+1,allTimeRule[key][i]))
        _log("-"*80)
        _log("Alert Cmds:")
        for i in range(0, len(allAlertCmd)):
            _log("    Cmd#%d: [%s]" %(i+1,allAlertCmd[i]))

def _readLastTQTime(sym, type):
    #/tmp/lastTQ/STW.LastQ
    filename = '/tmp/lastTQ/%s.%s' % (sym, type)
    try:
        with open(filename, 'r') as f:
            line = f.readline()
            return int(line)
    except:
        return 0
def _runCmd(cmd, HEADER, BODY):
    finalCmd = cmd.replace('{HEADER}', HEADER).replace('{BODY}', BODY)
    _log("Alert Cmd: [%s] --> [%s]" % (cmd, finalCmd))
    if (finalCmd.strip().find('#') == 0):
        _log("    Skip run!")
    else:
        subprocess.call(cmd, shell=True)
        _log("    Ran!")
    

def _main():
    allTimeRule = {}
    allAlertCmd = []
    _readConfig('tqdb1', allTimeRule, allAlertCmd)
    lastCheckWeekVal=0
    matchingWeekValRule = []
    sleepSec=5
    while(True):
        try:
            for cmdIdx in range(0,len(allAlertCmd)):
                testCmdFile='/tmp/TQAlert/TQAlert.testcmd.%d' % cmdIdx
                print testCmdFile
                if (os.path.isfile(testCmdFile)):
                    _runCmd(allAlertCmd[cmdIdx], '!!TEST!!', 'Hello, this is test of TQAlert#%d.'%(cmdIdx+1))
                    os.remove(testCmdFile)
        except:
            _log("Failed in run test command!")
            pass
        curHHMMSS = int(datetime.now().strftime('%H%M%S'))
        curTimeS =  int(datetime.now().strftime('%s'))
        curWeekday = int(datetime.today().isoweekday())
        curWeekVal = int(math.pow(10, 7-curWeekday)) #monday=1000000, tuesday=0100000 ... sunday=0000001
        # if config change!
        try:
            with open('/tmp/TQAlert/TQAlert.confchange', 'r') as f:
                lastChangeTimeS = int(f.readline().strip())
                if curTimeS<lastChangeTimeS+sleepSec*1.5:
                    _log("%s>Config change<%s"%('='*20, '='*20))
                    _readConfig('tqdb1', allTimeRule, allAlertCmd)
                    lastCheckWeekVal=999
        except:
            pass

        if (lastCheckWeekVal != curWeekVal):
            matchingWeekValRule = []
            lastCheckWeekVal = curWeekVal
            for key in allTimeRule.keys():
                for i in range(0, len(allTimeRule[key])):
                    if (int((allTimeRule[key][i][0])/curWeekVal)%10) == 1:
                        matchingWeekValRule.append({'Symbol':key, 'RuleIdx':i, 'Rule': allTimeRule[key][i]})
            _log("-"*80)
            _log("Detected day change...")
            _log("Current rules (count=%d):" % len(matchingWeekValRule))
            for rule in matchingWeekValRule:
                _log("    %s" % rule)

        print("Current WeekVal:%07d, HHMMSS:%d, TimeS:%d" %(curWeekVal, curHHMMSS, curTimeS))
        for rule in matchingWeekValRule:
            skipFile='/tmp/TQAlert/TQAlert.skip.%s' % rule['Symbol']
            if (os.path.isfile(skipFile)):
                _log("File: %s exist, so skip %s" % (skipFile, rule['Symbol']))
                continue
            HEADER=""
            BODY=""
            (Beg, End, TickSec, QuoteSec)=(rule['Rule'][1], rule['Rule'][2], rule['Rule'][3], rule['Rule'][4])
            if curHHMMSS>=Beg and curHHMMSS<End:
                if QuoteSec>0:
                    lastTimeS = _readLastTQTime(rule['Symbol'], 'LastQ')
                    print "Q-->",rule['Rule'],curTimeS,lastTimeS,QuoteSec
                    if (curTimeS>lastTimeS+QuoteSec):
                        HEADER="No Quote Alert"
                        BODY="%s is no quote for %d secs!" % (rule['Symbol'], QuoteSec)
                if TickSec>0:
                    lastTimeS = _readLastTQTime(rule['Symbol'], 'LastT')
                    print "T-->",rule['Rule'],curTimeS,lastTimeS,TickSec
                    if (curTimeS>lastTimeS+TickSec):
                        HEADER="No Tick Alert"
                        BODY="%s is no tick for %d secs!" % (rule['Symbol'], TickSec)
            if (HEADER != ""):
                _log("!!!%s!!! %s" % (HEADER, BODY))
                for cmd in allAlertCmd:
                    _runCmd(cmd, HEADER, BODY)
        time.sleep(sleepSec)

while(True):
    try:
        _main()
    except:
        _log("Exception in _main")
        time.sleep(30)

