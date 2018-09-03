#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

TQDB_From=127.0.0.1:8888
TQDB_FromTZ=Asia/Taipei
SYM_From=TWSE_V
BEG=2018-1-1
END=2037-1-1
SYM_To=TWSE_V

if [ "$6" == "" ] ; then
	echo "Systex Error!"
	echo "    $0 [From-TQDB IP:Port] [From-TQDB timezone] [From-Symbol] [Begin date] [End date] [To-Symbol]"
	echo "Ex: $0 192.168.1.100:80 Asia/Taipei TWSE 2018-8-15 2018-9-1 NEWSYM"
	exit
fi

TQDB_From=$1
TQDB_FromTZ=$2
SYM_From=$3
BEG=$4
END=$5
SYM_To=$6
#CMD="wget -O /tmp/sysinfo 'http://${TQDB_From}/cgi-bin/qSystemInfo.py'"
#echo "Ready to run: "$CMD
#eval $CMD

CSV_TZFrom=/tmp/${SYM_From}.tzFrom.csv
CSV_TZTo=/tmp/${SYM_From}.tzTo.csv

CMD="wget -O ${CSV_TZFrom} 'http://${TQDB_From}/cgi-bin/q1min.py?symbol=${SYM_From}&BEG=${BEG}&END=${END}&csv=1'"
echo "Ready to run: "$CMD
eval $CMD

CMD="/home/tqdb/codes/tqdb/tools/csvtzconv.py '${TQDB_FromTZ}' 'local' '${CSV_TZFrom}' > ${CSV_TZTo}"
echo "Ready to run: "$CMD
eval $CMD

CMD="cat ${CSV_TZTo} | python /home/tqdb/codes/tqdb/tools/Min2Cass.py $CASS_IP $CASS_PORT tqdb1 '${SYM_To}'"
echo "Ready to run: "$CMD
eval $CMD
