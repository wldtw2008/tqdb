#!/bin/bash
EZID=$1
TITLE=$2
BODY=$3
LV=$4

./uniNotifyCMD.x86_64 ${EZID} "${TITLE}" "${BODY}" ${LV}
