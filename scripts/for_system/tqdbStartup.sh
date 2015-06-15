#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

echo $CASS_IP":"$CASS_PORT > /tmp/cass.info
echo $D2TQ_IP":"$D2TQ_PORT > /tmp/d2tq.info


cd $TQDB_DIR/scripts && ./autoIns2Cass.sh > /tmp/autoIns2Cass.log &
