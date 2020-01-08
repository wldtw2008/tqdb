#!/bin/bash
TQDB_FORWEB_DIR=/home/tqdb/codes/tqdb/tools/for_web/
APACHE_CONF_DIR=/etc/httpd/conf.d/
TDIR=/var/www/

mv ${APACHE_CONF_DIR}/welcome.conf ${APACHE_CONF_DIR}/welcome.conf.orig
ln -s ${TQDB_FORWEB_DIR}/TQDB.vhost.conf ${APACHE_CONF_DIR}/


chmod -R +x /home/tqdb/
chmod -R +r /home/tqdb/
rm -rf ${TDIR}/*
ln -s ${TQDB_FORWEB_DIR}/cgi-bin ${TDIR}/

ln -s ${TQDB_FORWEB_DIR}/html ${TDIR}/
ln -s ${TQDB_FORWEB_DIR}/images/* ${TDIR}/html/
ln -s ${TQDB_FORWEB_DIR}/js ${TDIR}/html/

echo ==== Disable PrivateTmp for Apache with systemd ====
mkdir /etc/systemd/system/httpd.service.d
echo "[Service]" >  /etc/systemd/system/httpd.service.d/nopt.conf
echo "PrivateTmp=false" >> /etc/systemd/system/httpd.service.d/nopt.conf
systemctl daemon-reload
systemctl cat httpd.service

echo ==== Set HTTP Timeout to 10 mins ====
echo "Timeout 600" >> /etc/httpd/conf/httpd.conf

echo ==== Ready to restart httpd ====
sudo systemctl restart httpd

echo ==== All done. ====

