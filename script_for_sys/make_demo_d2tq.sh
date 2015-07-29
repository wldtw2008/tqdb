#!/bin/bash

while [ 1 ];
do

	CLOSE=10000
	BID=9995
	ASK=10005
	HIGH=$CLOSE
	LOW=$CLOSE
	VOL=0
	TICKCNT=0
	TICKVOL=0
	while [ 1 ];
	do
		TIME=`date +%H%M%S00`
		if [ $TIME -gt 23550000 ]; then break; fi;
		#if [ $TIME -gt 15490000 ]; then break; fi;
		CHG=`echo $RANDOM | awk '{print $0%10-5}'`
		TICKVOL=`echo $RANDOM | awk '{print $0%10}'`
		CLOSE=$(( $CLOSE+$CHG ))
		BID=$(( $CLOSE-5))
		ASK=$(( $CLOSE+5))
        	if [ $CLOSE -gt $HIGH ] ; then HIGH=$CLOSE; fi
		if [ $CLOSE -lt $LOW ] ; then LOW=$CLOSE; fi
		VOL=$(( $VOL+$TICKVOL))

		TICKCNT=$(($TICKCNT+1))
		TICKSTR="01_ID=DEMO,TIME="$TIME",TC="$TICKCNT",C="$CLOSE",V="$TICKVOL","
		QUOTESTR="00_ID=DEMO,TIME="$TIME",TickCount="$TICKCNT",O="$OPEN",H="$HIGH",L="$LOW",C="$CLOSE",V="$VOL",Bid="$BID",Ask="$ASK","
		echo $TICKSTR
		echo $QUOTESTR
		sleep 1
	done

	sleep 1
done

