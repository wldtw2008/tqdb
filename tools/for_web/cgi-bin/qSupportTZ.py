#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import json

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

#allTZ = {'all': runCmd("/home/tqdb/codes/tqdb/tools/tzconv -tz"), 'server': 'xx'}
allTZ = {'all': runCmd("timedatectl list-timezones"), 'server': 'xx'}
sys.stdout.write("Content-Type: application/json\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(json.dumps(allTZ))
sys.stdout.flush()
