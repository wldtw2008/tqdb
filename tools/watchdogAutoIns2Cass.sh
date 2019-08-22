#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

WATCHDOG_LASTT=/tmp/lastTQ/watchdogAutoIns2Cass.sh.LastT

rm -f ${WATCHDOG_LASTT}
LASTSTATUS="NG"
while [ 1 ] ;
do
    LAST_TS=`cut -b 1- /tmp/lastTQ/*.LastT  | sort | uniq | grep '^[0-9]*' | tail -1`
    CURR_TS=`date +%s`
    DIFF=`echo ${CURR_TS}-${LAST_TS} | bc `
    echo "Difference inverval of current and last tick is "${DIFF}" Sec(s)"
    if [ "${DIFF}" -gt "600" ] ; then
        ps -ef | grep itick | grep -v grep | awk '{print $2}' | xargs -i kill {}
        ps -ef | grep netcat | grep ${D2TQ_IP} | awk '{print $2}' | xargs -i kill {}
        echo ${CURR_TS} > ${WATCHDOG_LASTT}
        if [ "${LASTSTATUS}" == "OK" ] ; then  
            #OK to NG      
            logger -i '[E][TQDB] Detected tick loss! Restarting autoIns2Cass.'
        else
            #NG to NG
            logger -i '[I][TQDB] Detected tick loss! Restarting autoIns2Cass.'
        fi
        sleep 600
        LASTSTATUS="NG"
    else
        LASTSTATUS="OK"
    fi
    sleep 60
done

