#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

if [ "$1" = "" ] ; then
       echo "Systex Error!  $0 Symbol BeginDate EndDate TmpFile ISGZIP"
       echo "ie: $0 WTX 2015-1-1 2015-6-15 /tmp/wtx.min 0"
       exit 0
fi


TQDB="tqdb1"
SYMBOL=$1
DTBEG=$2
DTEND=$3
EPID=-1
FILE=$4
GZIP=$5
if [ "$FILE" == "" ] ; then
	FILE=/tmp/1min
fi

if [ -f $FILE ] ; then
	rm $FILE
fi
CMD="${TQDB_DIR}/tools/qtick $CASS_IP $CASS_PORT ${TQDB}.tick 0 '$SYMBOL' '$DTBEG' '$DTEND' $EPID | ${TQDB_DIR}/tools/tick21min -F1"
#echo $CMD
eval $CMD >> $FILE

if [ "$GZIP" == "1" ] ; then
	gzip $FILE
fi
#cat $FILE
