#!/bin/bash
. /etc/profile.d/profile_tqdb.sh

if [ "$1" == "" ] ; then
	echo "Systex Error!"
	echo "Systex:  $0 [OldTickDir] [RestoreDate] [GO]"
	echo "Example: $0 '/home/tqdb/oldtick/20190629.0/*.tick' 20190628 GO"
	exit
fi
OLDTICK_FILES=$1
RESTORE_DATE=$2
GO=$3

FILES=`ls ${OLDTICK_FILES}`

for F in ${FILES}
do
    SYM=`basename ${F} .tick `
    CMD="grep '^"${RESTORE_DATE}"' "${F}" | ./tick21min | python Min2Cass.py "$CASS_IP" "$CASS_PORT" tqdb1 '"${SYM}"'"
    echo "Ready to run: "${CMD}
    if [ "${GO}" == "GO" ] ; then
        eval ${CMD}
    else
        echo "    ---Simulate--- If you realy want to insert 1-Min data, Please put GO at 3rd parameter and run again."
    fi
    echo "    done."
done
