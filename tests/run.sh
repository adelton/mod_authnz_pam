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

cp /var/log/httpd/pam_exec.log /var/log/httpd/pam_exec.log.old

function next_log () { set +x
	tail -c +$(( $( stat -c%s /var/log/httpd/pam_exec.log.old ) + 1 )) /var/log/httpd/pam_exec.log | sed 's/^/:: /'
	# echo '###' >> /var/log/httpd/pam_exec.log
	cp /var/log/httpd/pam_exec.log /var/log/httpd/pam_exec.log.old
	set -x
}

rm -f /etc/pam-auth/*

echo "Testing Require pam-account"
curl -s -D /dev/stdout -o /dev/null http://localhost/authz | tee /dev/stderr | grep 401
curl -u alice:Tajnost -s -D /dev/stdout -o /dev/null http://localhost/authz | tee /dev/stderr | grep 401
touch /etc/pam-account/alice
curl -u alice:Tajnost -s http://localhost/authz | tee /dev/stderr | grep 'User alice'

echo "Testing AuthBasicProvider PAM"
curl -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
touch /etc/pam-auth/bob
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
echo Secret > /etc/pam-auth/bob
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
next_log > /dev/null
touch /etc/pam-account/bob
curl -u bob:Secret -s http://localhost/authn | tee /dev/stderr | grep 'User bob'
next_log | grep 'account .bob. ok' | wc -l | grep '^1$'
curl -u bob:Secret -s http://localhost/authnp | tee /dev/stderr | grep 'User bob'
next_log | grep 'account .bob. ok' | wc -l | grep '^2$'
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authnp2 | tee /dev/stderr | grep 401
next_log | grep -E 'account .bob. ok|No ./etc/pam-account2/bob' | uniq | wc -l | grep '^2$'
touch /etc/pam-account2/bob
curl -u bob:Secret -s http://localhost/authnp | tee /dev/stderr | grep 'User bob'
next_log | grep 'account .bob. ok' | wc -l | grep '^2$'
echo Secret2 > /etc/pam-auth/bob
curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401

if rpm -ql httpd | grep mod_authn_socache ; then
	echo "Testing AuthBasicProvider socache PAM + AuthnCacheProvideFor PAM"
	rm /etc/pam-account/bob
	curl -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
	echo Secret > /etc/pam-auth/bob
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
	# rerun the same request, verify that passing auth did not store password into cache
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
	touch /etc/pam-account/bob
	curl -u bob:Secret -s http://localhost/authn-cached | tee /dev/stderr | grep 'User bob'
	echo Secret2 > /etc/pam-auth/bob
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn | tee /dev/stderr | grep 401
	curl -u bob:Secret -s http://localhost/authn-cached | tee /dev/stderr | grep 'User bob'
	sleep 11
	curl -u bob:Secret -s -D /dev/stdout -o /dev/null http://localhost/authn-cached | tee /dev/stderr | grep 401
fi

echo OK $0.
