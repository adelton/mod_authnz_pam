#!/bin/bash

set -e
set -x

DNF=yum
BUILDDEP_PROVIDER=yum-utils
BUILDDEP=yum-builddep
if type dnf 2> /dev/null ; then
	DNF=dnf
	BUILDDEP_PROVIDER='dnf-command(builddep)'
	BUILDDEP='dnf builddep'
fi

$DNF install -y rpm-build "$BUILDDEP_PROVIDER"
$BUILDDEP -y mod_authnz_pam.spec
NAME_VERSION=$( rpm -q --qf '%{name}-%{version}\n' --specfile mod_authnz_pam.spec | head -1 )
mkdir .$NAME_VERSION
cp -rp * .$NAME_VERSION
mv .$NAME_VERSION $NAME_VERSION
mkdir -p ~/rpmbuild/SOURCES
tar cvzf ~/rpmbuild/SOURCES/$NAME_VERSION.tar.gz $NAME_VERSION
rpmbuild -bb --define "dist $( rpm --eval '%{dist}' ).localbuild" mod_authnz_pam.spec
$DNF install -y ~/rpmbuild/RPMS/*/$NAME_VERSION-*.localbuild.*.rpm
