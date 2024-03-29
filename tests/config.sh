#!/bin/bash

set -e
set -x

sed -i 's/^MaxClients.*/MaxClients 1/' /etc/httpd/conf/httpd.conf
mkdir -p /etc/pam-auth
mkdir -p /etc/pam-account
mkdir -p /etc/pam-account2
cp -p tests/auth.cgi /var/www/cgi-bin/auth.cgi
cp -p tests/pam-exec /usr/bin/pam-exec
cp tests/pam-web /etc/pam.d/web
cp tests/pam-web /etc/pam.d/web2
cp tests/pam-webl /etc/pam.d/webl
chmod a+x /var/log/httpd
touch /var/log/httpd/pam_exec.log
chown apache /var/log/httpd/pam_exec.log
cp tests/auth.conf /etc/httpd/conf.d/
if rpm -ql httpd | grep mod_authn_socache ; then
	cat tests/auth-socache.conf >> /etc/httpd/conf.d/auth.conf
fi
htpasswd -bc /etc/htpasswd alice Tajnost
useradd user1
echo user1:heslo1 | chpasswd
chgrp apache /etc/shadow
chmod g+r /etc/shadow
