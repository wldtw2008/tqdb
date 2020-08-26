#!/bin/bash
. /etc/profile.d/profile_tqdb.sh
echo "===========Backup & Purge old tick file==========="
echo "Note:"
echo "  Please run this sh at sunday or no tick data day"
echo "=================================================="

#OROOT_DIR=$HOME"/oldtick/"
OROOT_DIR="/home/tqdb/oldtick/"

ODIR=""
TQDB="tqdb1"
TODAY="2037-1-1" #$1  <== not allow input date

function runCmd(){
	#echo "    runCmd: "$1
	eval $1
}

CNT=0
while [ 1 ] 
do
    DT=`date +%Y%m%d`
    ODIR=${OROOT_DIR}${DT}"."${CNT}
    echo $ODIR
    if [ ! -d "$ODIR" ] ; then
        CMD='mkdir '$ODIR
	runCmd "$CMD"
          echo "break" $ODIR
        break
    fi
    CNT=$(($CNT+1))
done
echo "Backup data to: "$ODIR

echo "=================================================="
ALLSYM=`./qsym $CASS_IP $CASS_PORT  ${TQDB}.symbol 0 ALL 0 | grep 'symbol=' | cut -f 2 -d '='`
#CMD="./qsym "$CASS_IP" "$CASS_PORT" "${TQDB}".symbol 0 ALL 0 | grep 'symbol=' | cut -f 2 -d '='"
#ALLSYM=`runCmd "$CMD"`
ALLSYMCNT=`echo "$ALLSYM" | wc -w`
CNT=1
for SYM in $ALLSYM
do
    #if [ "$SYM" != 'TXO;201507;9000C' ] ; then 
    #    continue
    #fi
    echo "Exporting & Purging tick: "$SYM" ("$CNT"/"$ALLSYMCNT")"
    CMD="./qtick "$CASS_IP" "$CASS_PORT" "${TQDB}".tick 1 '"$SYM"' 1970-1-1 "$TODAY" -1 > "$ODIR"/'"$SYM".tick'"
    echo "  Ready to run export tick CMD: "$CMD
    runCmd "$CMD"
    echo "    Export done."
    CMD="/var/cassandra/bin/cqlsh -e \"delete from "${TQDB}".tick where symbol='"$SYM"';\""
    echo "  Ready to delete tick data CMD: "$CMD
    runCmd "$CMD"
    echo "    Delete done."
    CNT=$(($CNT+1))
done

echo "=================================================="
CMD="/var/cassandra/bin/nodetool -h "${CASS_IP}" compact "${TQDB}" tick"
echo "Compacting DB... (This may cost several minutes, depend on your CPU/HD , be patient.)"
echo "  Ready to run compact CMD: "$CMD
runCmd "$CMD"
echo "All Done!!"
