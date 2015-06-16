#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

#  ./qTick2Min.sh 'WTX' '2015-06-04 13:20' '2037-1-1' -1

TOOLDIR="/home/trade888/study/cassandra/mytool/"
CASSIP="127.0.0.1"
CASSPORT="9042"
TQDB="tqdb1"
SYMBOL=$1
DTBEG=$2
DTEND=$3
EPID=-1
CMD=`echo "${TOOLDIR}/qtick $CASSIP $CASSPORT ${TQDB}.tick 0 '$SYMBOL' '$DTBEG' '$DTEND' $EPID | ${TOOLDIR}/tick21min -F1"`
eval $CMD

DATE=`date`
echo $DATE"> "$CMD>> /tmp/cgi_qTick2Min.sh.log
