#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

if [ "$1" = "" ] ; then
       echo "Systex Error!  $0 Symbol BeginDate EndDate TmpFile ISGZIP MarketOpenHHMMSS MarketCloseHHMMSS"
       echo "ie: $0 WTX 2015-1-1 2015-6-15 /tmp/wtx.min 0 084500 134500"
       exit 0
fi


TQDB_DB="tqdb1"
SYMBOL=$1
DTBEG=$2
DTEND=$3
EPID=-1
FILE=$4
GZIP=$5
MKOPEN=$6
MKCLOSE=$7
DBG=0
if [ "$FILE" == "" ] ; then
	FILE=/tmp/1day
fi

if [ -f $FILE ] ; then
	rm $FILE
fi
if [ -f ${FILE}.1  ] ; then
        rm ${FILE}.1
fi

CMD="$TQDB_DIR/tools/q1min $CASS_IP $CASS_PORT ${TQDB_DB}.minbar 0 '${SYMBOL}' '$DTBEG' '$DTEND'"
if [ $DBG -eq 1 ] ; then
	echo $CMD
fi
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
	if [ $DBG -eq 1 ] ; then
        	echo $CMD
	fi

	eval $CMD >> $FILE
fi

mv $FILE ${FILE}.1

cat ${FILE}.1 | python $TQDB_DIR/tools/Min2Day.py $MKOPEN $MKCLOSE > ${FILE}
rm ${FILE}.1
if [ "$GZIP" == "1" ] ; then
	gzip $FILE
fi
#cat $FILE
