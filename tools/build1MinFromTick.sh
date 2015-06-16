#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

if [ "$1" = "" ] ; then
       echo "Systex Error!  $0 Symbol DayAgo"
       echo "ie: $0 WTX 0"
       echo "    $0 ALL 0"
       exit 0
fi


TQDB="tqdb1"
SYMBOL=$1
NDAYAGO=$2
if [ "$NDAYAGO" == "" ] ; then 
	NDAYAGO=0
fi


EPID=-1
DTBEG=`date +%Y-%m-%d --date="$(($NDAYAGO+1)) day ago"`
DTEND=`date +'%Y-%m-%d 00:00:01' --date="$NDAYAGO day ago"`
ALLSYM=''
if [ "$SYMBOL" != "ALL" ] ; then
	ALLSYM=$SYMBOL
else
	ALLSYM=`$TQDB_DIR/tools/qsym  $CASS_IP $CASS_PORT  ${TQDB}.symbol 0 ALL|grep -E "^symbol=" | cut -f 2 -d '='`
fi

for SYM in $ALLSYM
do
	SYMBOL=$SYM
	CMD="$TQDB_DIR/tools/qtick $CASS_IP $CASS_PORT ${TQDB}.tick 0 '$SYMBOL' '$DTBEG' '$DTEND' $EPID | $TQDB_DIR/tools/tick21min | python Min2Cass.py $CASS_IP $CASS_PORT $TQDB '$SYMBOL'"
	echo "ready to run:"$CMD
	eval $CMD	
done

