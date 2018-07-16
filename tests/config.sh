#!/bin/bash

set -e
set -x

sed -i 's/^MaxClients.*/MaxClients 1/' /etc/httpd/conf/httpd.conf
mkdir -p /etc/pam-auth
cp -p tests/auth.cgi /var/www/cgi-bin/auth.cgi
cp -p tests/pam-exec /usr/bin/pam-exec
cp tests/pam-web /etc/pam.d/web
chmod a+x /var/log/httpd
touch /var/log/httpd/pam_exec.log
chown apache /var/log/httpd/pam_exec.log
cp tests/auth.conf /etc/httpd/conf.d/
htpasswd -bc /etc/htpasswd alice Tajnost
