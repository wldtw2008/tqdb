#!/bin/bash
SYM=$1
if [ "${SYM}" == "" ] ; then 
    echo "Please input symbol to remove all data of this symbol!"
    echo "Ex: $0 AAABBB"
    exit
fi

/var/cassandra/bin/cqlsh -e "delete from tqdb1.symbol where Symbol='${SYM}';delete from tqdb1.minbar where Symbol='${SYM}';delete from tqdb1.secbar where Symbol='${SYM}';delete from tqdb1.tick where Symbol='${SYM}';"
echo "removed all data of '"${SYM}"'"
