#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

THISPID=`echo $$`
ps -ef | grep itick | awk '{print $2}'| xargs -i kill {}
DBG=0
while [ 1 ] ;
do
	stdbuf -i0 -o0 -e0 netcat --recv-only $D2TQ_IP $D2TQ_PORT | $TQDB_DIR/tools/itick $CASS_IP $CASS_PORT tqdb1 ${DBG} 0 
        sleep 10
done
