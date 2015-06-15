#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

THISPID=`echo $$`
ps -ef | grep itick | awk '{print $2}'| xargs -i kill {}
DBG=0
while [ 1 ] ;
do
	netcat -d $D2TQ_IP $D2TQ_PORT | $TQDB_DIR/tools/bin/itick $CASS_IP $CASS_PORT tqdb1 ${DBG} 1 
        sleep 10
done
