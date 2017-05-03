#!/bin/bash
SRCROOTDIR=/usr/local # ../../cpp-driver/
CASSLIB=/usr/lib64/libcassandra.so #../../cpp-driver/build/libcassandra.so
SRC=./
BIN=../
rm *.o

CC=g++ #/usr/bin/cc
STRIP=strip

function buildObj(){
	TRG=$1
	if [ -e ${SRC}/${TRG}.o ] ; then
		rm ${SRC}/${TRG}.o
	fi
	${CC}  -DCASS_USE_OPENSSL -D_GNU_SOURCE -I${SRCROOTDIR}/include -I${SRCROOTDIR}/src -I${SRCROOTDIR}/src/third_party/rapidjson -I${SRCROOTDIR}/src/third_party/boost -D_GNU_SOURCE -Wall -pedantic -Wextra -Wno-long-long -Wno-deprecated-declarations -Wno-unused-parameter -Wno-unused-local-typedefs -o ${SRC}/${TRG}.o   -c ${SRC}/${TRG}.cpp


	if [ "$?" == "1" ] ; then
		echo "!!!Some error while compliing..."
		exit 1
	fi
}
function buildExe(){
	TRG=$1
	if [ -e ${BIN}/${TRG} ] ; then
		rm ${BIN}/${TRG}
	fi
	buildObj $TRG
	${CC}   -D_GNU_SOURCE ${SRC}/common.o ${SRC}/${TRG}.o  -o ${BIN}/${TRG} -rdynamic  -lssl -lcrypto ${CASSLIB}  -lssl -lcrypto -Wl,-rpath,./

	if [ "$?" == "1" ] ; then
                echo "!!!Some error while linking..."
                exit 1
        fi
	${STRIP} ${BIN}/${TRG}
}

buildObj common
buildExe q1minsec
buildExe qtick
buildExe qquote
buildExe qsym
buildExe itick
echo "=== All builded!! ==="
exit 0
