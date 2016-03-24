#!/bin/bash
. /etc/profile.d/profile_tqdb.sh
IFS=$'\n'
echo "===========Backup & Purge old tick file==========="
echo "Note:"
echo "  Please run this sh at sunday or no tick data day"
echo "=================================================="

if [ "$1" == "" ] ; then
    echo "please input symbol"
    exit
fi

TQDB="tqdb1"
SYM=$1
ACT=$2
function runCMD(){
    INFUNC_CMD=$1
    echo "ready to run:${CMD}"
    if [ "$ACT" == "GO" ] ; then
        eval ${INFUNC_CMD}
    else 
        echo "skip!"
    fi
}

CMD="/var/cassandra/bin/cqlsh -e \"delete from ${TQDB}.tick where symbol='$SYM';\""
runCMD $CMD
CMD="/var/cassandra/bin/cqlsh -e \"delete from ${TQDB}.secbar where symbol='$SYM';\""
runCMD $CMD
CMD="/var/cassandra/bin/cqlsh -e \"delete from ${TQDB}.minbar where symbol='$SYM';\""
runCMD $CMD
CMD="/var/cassandra/bin/cqlsh -e \"delete from ${TQDB}.symbol where symbol='$SYM';\""
runCMD $CMD

