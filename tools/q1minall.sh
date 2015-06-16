#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

if [ "$1" = "" ] ; then
       echo "Systex Error!  $0 Symbol BeginDate EndDate TmpFile ISGZIP"
       echo "ie: $0 WTX 2015-1-1 2015-6-15 /tmp/wtx.min 0"
       exit 0
fi


TQDB_DB="tqdb1"
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
CMD="$TQDB_DIR/tools/q1min $CASS_IP $CASS_PORT ${TQDB_DB}.minbar 0 '${SYMBOL}' '$DTBEG' '$DTEND'"
eval $CMD >> $FILE

TAILLINE=`tail -1 $FILE | sed 's/ //g'`
if [ "$TAILLINE" != "" ] ; then
	CMD="tail -1 $FILE | awk 'BEGIN{FS=\",\"}{printf(\"%s-%s-%s %s:%s:%s\",substr(\$1,1,4),substr(\$1,5,2),substr(\$1,7,2),substr(\$2,1,2),substr(\$2,3,2),substr(\$2,5,2))}'"
	TAILDATE=`eval $CMD`
else
	TAILDATE=$DTBEG
fi

if [ "$TAILDATE" != "" ] ; then	
	CMD="$TQDB_DIR/tools/qtick $CASS_IP $CASS_PORT ${TQDB_DB}.tick 0 '${SYMBOL}' '$TAILDATE' '$DTEND' -1| $TQDB_DIR/tools/tick21min"
	eval $CMD >> $FILE
fi

if [ "$GZIP" == "1" ] ; then
	gzip $FILE
fi
#cat $FILE
