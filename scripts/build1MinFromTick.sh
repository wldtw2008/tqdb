#!/bin/bash

TQDB="tqdb1"
SYMBOL=$1
NDAYAGO=$2
if [ "$NDAYAGO" == "" ] ; then 
	NDAYAGO=0
fi


EPID=-1
DTBEG=`date +%Y-%m-%d --date="$(($NDAYAGO+1)) day ago"`
DTEND=`date +%Y-%m-%d --date="$NDAYAGO day ago"`
ALLSYM=''
if [ "$SYMBOL" != "ALL" ] ; then
	ALLSYM=$SYMBOL
else
	ALLSYM=`./qsym  $CASS_IP $CASS_PORT  ${TQDB}.symbol 0 ALL|grep -E "^symbol=" | cut -f 2 -d '='`
fi

for SYM in $ALLSYM
do
	SYMBOL=$SYM
	CMD="./qtick $CASS_IP $CASS_PORT ${TQDB}.tick 0 '$SYMBOL' $DTBEG $DTEND $EPID | ./tick21min | python Min2Cass.py $CASSIP $CASSPORT $TQDB '$SYMBOL'"
	echo "ready to run:"$CMD
	eval $CMD	
done

