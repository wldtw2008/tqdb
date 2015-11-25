#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

echo $CASS_IP":"$CASS_PORT > /tmp/cass.info
echo $D2TQ_IP":"$D2TQ_PORT > /tmp/d2tq.info

#cd $TQDB_DIR/script_for_sys && ./demo_d2tq_server.sh > /tmp/demo_d2tq_server.log &

sleep 10

cd $TQDB_DIR/tools && ./autoIns2Cass.sh > /tmp/autoIns2Cass.log &

su - tqdb -c "cd /home/tqdb/.ipython && ipython notebook --profile=nbserver &"
