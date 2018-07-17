#!/bin/bash

set -e
set -x

echo "Wait for the HTTP server to start ..."
for i in $( seq 1 10 ) ; do
	if curl -s -o /dev/null http://localhost/ ; then
		break
	fi
	sleep 3
done

echo "Testing Require pam-account"
curl -s -D /dev/stdout -o /dev/null http://localhost/authz | tee /dev/stderr | grep 401
curl -u alice:Tajnost -s -D /dev/stdout -o /dev/null http://localhost/authz | tee /dev/stderr | grep 401
touch /etc/pam-auth/alice
curl -u alice:Tajnost -s http://localhost/authz | tee /dev/stderr | grep 'User alice'

echo "Testing AuthBasicProvider PAM"
curl -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
touch /etc/pam-auth/bob
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
echo Secret > /etc/pam-auth/bob
curl -u bob:Secret -s http://localhost/authn | tee /dev/stderr | grep 'User bob'
echo Secret2 > /etc/pam-auth/bob
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401

if rpm -ql httpd | grep mod_authn_socache ; then
	echo "Testing AuthBasicProvider socache PAM + AuthnCacheProvideFor PAM"
	curl -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
	echo Secret > /etc/pam-auth/bob
	curl -u bob:Secret -s http://localhost/authn-cached | tee /dev/stderr | grep 'User bob'
	echo Secret2 > /etc/pam-auth/bob
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
	curl -u bob:Secret -s http://localhost/authn-cached | tee /dev/stderr | grep 'User bob'
	sleep 11
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
fi
