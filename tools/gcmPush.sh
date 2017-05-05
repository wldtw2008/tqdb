#!/bin/bash
TITLE=$1
BODY=$2
PUSHKEY=$3   #PUSHKEY='BIzaTyCml-Gxos_THNjRN1mTd-ULQrVo912MpnV'

TO="d02zeaE2xE4:APA91bEXMC94D6xkOjg1MNO_F1KgG_KYG66S_4ZYtxUMpSDAX3lcfLkfnbRubxGYWLiM5qYHPkIJiSyHkP-7iTveTuVZlYopnpTghipyCRW4O-Nk8vFdtcIf4G7gAg7N3dzzWBtHfFPK"
TRIGGER_TIME=`date +"%Y-%m-%d %H:%M:%S"`

wget -q  -O - --header "Authorization: key=${PUSHKEY}" --header "Content-Type: application/json" https://android.googleapis.com/gcm/send --post-data="{\"to\":\"/topics/global\",\"data\":{\"title\":\"${TITLE}\",\"body\":\"${BODY}\",\"trigger_time\":\"${TRIGGER_TIME}\"}}"

