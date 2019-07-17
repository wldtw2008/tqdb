#!/bin/bash
. /etc/profile.d/profile_tqdb.sh
LASTSTATUS="NG"
while [ 1 ] ;
do
    LAST_TS=`cut -b 1- /tmp/lastTQ/*.LastT  | sort | tail -1`
    CURR_TS=`date +%s`
    DIFF=`echo ${CURR_TS}-${LAST_TS} | bc `
    echo "Difference of current and last tick is "${DIFF}" Sec(s)"
    if [ "${DIFF}" -gt "600" ] ; then
        ps -ef | grep itick | awk '{print $2}'| xargs -i kill {}
        echo '${CURR_TS}' > /tmp/lastTQ/watchdogAutoIns2Cass.sh.LastT
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

