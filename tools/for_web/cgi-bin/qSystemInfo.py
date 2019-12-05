#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import json
from webcommon import *


szCassIP1="127.0.0.1"
szCassDB="tqdb1"
szBinDir='/home/tqdb/codes/tqdb/tools/'

allInfo=[] #[key, val]

def runCql(szCql, objRet):
    p = subprocess.Popen(["/var/cassandra/bin/cqlsh", "-e", szCql], cwd="/var/cassandra/bin/",  
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    objRet['output'], objRet['err'] = p.communicate()
    objRet['retcode'] = p.returncode
def runCmd(cmd):
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
    ret = []
    while True:
        line = proc.stdout.readline()
        if line is not None and line != '':
            ret.append(line.replace('\n', ''))
        else:
            break
    return ret

if False:
	tmpFile="/tmp/qsummery.%d.%d.txt"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
        objRet = {}
	cql="select * from %s.tick where symbol='%s' order by datetime limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['tick.first'] = objRet['output']

if True: #get hostname
    hostInfo = []
    lines = runCmd('hostname')
    for line in lines:
        if len(line)<=0: continue
        hostInfo.append("Hostname: %s"%line)
    lines = runCmd('hostname -I')
    for line in lines:
        for ip in line.split(' '):
            if len(ip)<=0: continue
            hostInfo.append("IP: %s" % ip)
    allInfo.append(['Host Info', '\n'.join(hostInfo)])

if True: #get system time zone
    linuxFamily = '?'
    if True:
        tempId = runCmd('cat /etc/os-release | grep "^ID="')[0]
        if tempId.find("rhel")>=0: linuxFamily="RedHat"
        elif tempId.find("centos")>=0: linuxFamily="RedHat"
        elif tempId.find("debian")>=0: linuxFamily="Debian"

    zones = []
    lines = runCmd('readlink -s /etc/localtime')
    for line in lines:
        zones.append(line)

    zones.append(os.path.realpath('/etc/localtime'))

    for i in range(0,len(zones)):
        posi = zones[i].find("zoneinfo/")
        if posi > 0:
            zones[i] = zones[i][posi+9:]
    tzdbVer = "?"
    if linuxFamily == "Debian":
        tzdbVer = runCmd('dpkg -s tzdata  | grep Version')[0].replace('Version: ','')
    elif linuxFamily == "RedHat":
        tzdbVer = runCmd('yum list installed | grep tzdata.noarch | awk "{print \\$2}"')
    lines = []
    lines.append('Now=%s' % ', '.join(runCmd("date +'%Y-%m-%d %H:%M:%S (%Z)'")))
    lines.append('TimeZone=%s (/etc/localtime)' % ', '.join(zones))
    lines.append('TimeZone=%s (/etc/timezone)' % ', '.join(runCmd('cat /etc/timezone')))
    lines.append('tzdata Version=%s' % tzdbVer)
    allInfo.append(['Server Time', '\n'.join(lines)])

if True:
    lines = runCmd('cat /etc/crontab | grep purgeTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Purge Tick Schedule', '\n'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep build1MinFromTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Build 1Min Schedule', '\n'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep build1SecFromTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Build 1Sec Schedule', '\n'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep -E "reboot|shutdown|halt" | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Reboot Schedule', '\n'.join(lines)])


if True:
    lines = []
    #lines += ["----%s %s----" % (linuxFamily, ''.join(runCmd('arch')))]
    lines += runCmd('grep -E "^PRETTY_NAME=" /etc/os-release | sed "s/\\"//g" | cut -f 2 -d "="')
    lines += [''.join(runCmd('arch'))] 
    allInfo.append(['Linux Info', '\n'.join(lines)])

if True:
    lines = []
    lines += runCmd('cat /proc/cpuinfo | grep -E "cores|model name" |sort | uniq ')
    allInfo.append(['CPUs Info', '\n'.join(lines)])

if True:
    lines = runCmd('top -bn1 | head -10')
    allInfo.append(['Top Info', '\n'.join(lines)])

if True:
    lines = runCmd('df -h')
    allInfo.append(['Disk Info', '\n'.join(lines)])

sys.stdout.write("Content-Type: application/json; charset=UTF-8\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(allInfo))
sys.stdout.flush()
