#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
from cassandra.cluster import Cluster
import os
import subprocess
import json

szCassIP1="127.0.0.1"
szCassDB="tqdb1"

importTicket=""

querystrings=os.environ.get("QUERY_STRING", "NA=NA")
mapQS={}
for qs in querystrings.split("&"):
        mapQS[qs.split("=")[0]] = qs.split("=")[1]
if 'importTicket' in mapQS: importTicket = mapQS['importTicket']


def _doubleFork():
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first paren
            #print "fork #1.parent %d exit"%pid
            os._exit(0) 
    except OSError, e: 
        print "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        os._exit(1)
    #print "fork #1.child %d here"%os.getpid()
    # decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            #print "fork #2.parent %d exit"%pid
            #file(pidfile, 'w').write('%d\n'%pid)
            os._exit(0) 
    except OSError, e: 
        print "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        os._exit(1)
    #print "fork #2.child %d here"%os.getpid()

cmdfile = '/tmp/%s.cmd' % importTicket
if os.path.isfile(cmdfile):
    sys.stdout.write("Content-Type: text/html\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write("<html><body>\r\n")
    sys.stdout.write("<script language='javascript'>window.location.href='./i1min_readstatus.py?importTicket=%s';</script>"%importTicket)
    sys.stdout.write("</body></html>\r\n")
    sys.stdout.flush()
    sys.stdout.close()
    _doubleFork()
    #sys.exit(0)
    #subprocess.call(cmdfile, shell=True, cwd='/tmp')
    NULLOUT = open(os.devnull, 'w')
    NULLIN = open(os.devnull, 'r')
    subprocess.Popen(cmdfile, shell=True, stdin=NULLIN,stdout=NULLOUT,stderr=NULLOUT)
    close(NULLOUT)
    close(NULLIN)
else:
    sys.stdout.write("Content-Type: text/html\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.write("<html><body>\r\n")
    sys.stdout.write("Can't find the ticket: '%s'\r\n"%importTicket)
    sys.stdout.write("</body></html>\r\n")

sys.stdout.write("\r\n")
sys.stdout.flush()

