#!/bin/bash
SDIR=/home/tqdb/codes/tqdb/tools/for_web/
TDIR=/var/www/

ln -s ${SDIR}/cgi-bin ${TDIR}/

ln -s ${SDIR}/html/*.html ${TDIR}/
ln -s ${SDIR}/html/*.css ${TDIR}/

ln -s ${SDIR}/js ${TDIR}/
