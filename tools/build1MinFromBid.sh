#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

TQDB="tqdb1"
SYMBOL=$1
NDAYAGO=$2
if [ "$NDAYAGO" == "" ] ; then 
	NDAYAGO=0
fi
EPID=-1
DTBEG=`date +%Y-%m-%d --date="$(($NDAYAGO+1)) day ago"`
DTEND=`date +%Y-%m-%d --date="$NDAYAGO day ago"`

if [ "$SYMBOL" != "" ] ; then
	CMD="./qquote $CASS_IP $CASS_PORT ${TQDB}.tick 0 $SYMBOL BID $DTBEG $DTEND $EPID | ./tick21min | python Min2Cass.py $CASS_IP $CASS_PORT $TQDB ${SYMBOL}.BID
"
	echo "ready to run:"$CMD
	eval $CMD
fi
