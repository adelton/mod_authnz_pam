
PACKAGE := mod_authnz_pam

outdir := $(CURDIR)
spec := $(PACKAGE).spec

spec_dir := .
ifeq ($(shell test -d $(spec) && echo true),true)
	spec_dir = $(spec)
	spec_file = $(spec)/$(PACKAGE).spec
else
	spec_dir = $(dir $(spec))
	spec_file = $(spec)
endif

VERSION := $(shell rpm -q --qf '%{name}-%{version}\n' --specfile mod_authnz_pam.spec 2> /dev/null | head -1)

srpm:
	cd $(spec_dir) && mkdir -p .source/$(VERSION) && cp -rp * .source/$(VERSION) && cd .source && tar cvzf $(VERSION).tar.gz $(VERSION)
	cd $(spec_dir) && rpmbuild -D '_srcrpmdir $(outdir)' -D '_sourcedir .source' -bs $(spec_file)
	cd $(spec_dir) && rm -rf .source

