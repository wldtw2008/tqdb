#!/bin/bash


if [ $EUID -ne 0 ]; then
   echo "This script must be run as root!" 
   exit 1
fi

echo "==== CAUTION!! CAUTION!! CAUTION!! CAUTION!! CAUTION!! CAUTION!! ===="
echo ""
echo "This script will remove all tick data from database and re-create tick table"
echo ""
echo "The system have purged tick data(and backuped to ~/oldtick at the same time) "
echo "on each Sunday. But I have no idea why Cassandra keep growing up the tick data."
echo "Anyway, if the disk space is going to fulled, we need to drop tick table and "
echo "rebuild it to free useless disk space."
echo ""
echo "==== CAUTION!! CAUTION!! CAUTION!! CAUTION!! CAUTION!! CAUTION!! ===="
echo ""

if [ "$1" != "GO!" ] ; then
    echo "Use '"$0" GO!' to run this script!"
    exit 1;
fi

echo "Restart Cassandra..."
CMD='/etc/init.d/cassandra restart'
echo "  "$CMD
eval $CMD
sleep 30

echo "Run drop tick table..."
CMD='cd /var/cassandra/bin/ && ./cqlsh -e "drop table tqdb1.tick"'
echo "  "$CMD
eval $CMD

echo "Remove old tick files from file system..."
CMD='rm -rf /var/cassandra/data/data/tqdb1/tick-*'
echo "  "$CMD
eval $CMD

echo "Re-create tick table..."
CMD='cd /var/cassandra/bin/ && ./cqlsh -e "CREATE TABLE tqdb1.tick (symbol text,datetime timestamp,keyval map<text, double>,type int,PRIMARY KEY (symbol, datetime));"'
echo "  "$CMD
eval $CMD

echo "Now current tick data file:"
ls -lrt /var/cassandra/data/data/tqdb1/tick-*

