%{!?_httpd_mmn: %{expand: %%global _httpd_mmn %%(cat %{_includedir}/httpd/.mmn || echo 0-0)}}
%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}

Summary: PAM authorization checker and PAM Basic Authentication provider
Name: mod_authnz_pam
Version: 0.9.3
Release: 1%{?dist}
License: ASL 2.0
Group: System Environment/Daemons
URL: http://www.adelton.com/apache/mod_authnz_pam/
Source0: http://www.adelton.com/apache/mod_authnz_pam/%{name}-%{version}.tar.gz
BuildRequires: httpd-devel
BuildRequires: pam-devel
BuildRequires: pkgconfig
Requires(pre): httpd
Requires: httpd-mmn = %{_httpd_mmn}
Requires: pam

# Suppres auto-provides for module DSO per
# https://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering#Summary
%{?filter_provides_in: %filter_provides_in %{_libdir}/httpd/modules/.*\.so$}
%{?filter_setup}

%description
mod_authnz_pam is a PAM authorization module, supplementing
authentication done by other modules, for example mod_auth_kerb; it
can also be used as full Basic Authentication provider which runs the
[login, password] authentication through the PAM stack.

%prep
%setup -q -n %{name}-%{version}

%build
%{_httpd_apxs} -c -Wc,"%{optflags} -Wall -pedantic -std=c99" -lpam mod_authnz_pam.c
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
cp authnz_pam.conf authnz_pam.confx
%else
cat authnz_pam.module > authnz_pam.confx
cat authnz_pam.conf >> authnz_pam.confx
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -Dm 755 .libs/mod_authnz_pam.so $RPM_BUILD_ROOT%{_httpd_moddir}/mod_authnz_pam.so

%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
# httpd >= 2.4.x
install -Dp -m 0644 authnz_pam.module $RPM_BUILD_ROOT%{_httpd_modconfdir}/55-authnz_pam.conf
%endif
install -Dp -m 0644 authnz_pam.confx $RPM_BUILD_ROOT%{_httpd_confdir}/authnz_pam.conf

%files
%doc README LICENSE
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_modconfdir}/55-authnz_pam.conf
%endif
%config(noreplace) %{_httpd_confdir}/authnz_pam.conf
%{_httpd_moddir}/*.so

%changelog
* Mon Jun 23 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.9.3-1
- Fix module loading/configuration for Apache 2.4.
- Set PAM_RHOST.

* Tue May 13 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.9.2-1
- Silence compile warnings by specifying C99.

* Tue Apr 15 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.9.1-1
- Fix error message when pam_authenticate step is skipped.

* Wed Mar 19 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.9-1
- One more function made static for proper isolation.

* Thu Jan 30 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.8.1-1
- Fixing regression from previous change.

* Thu Jan 30 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.8-1
- 1058805 - .spec changes for Fedora package review.

* Thu Jan 09 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.7-1
- Declare all functions static for proper isolation.

* Wed Jan 08 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.6-1
- Make pam_authenticate_with_login_password available for other modules.
- Reformat documentation to make the Basic Auth usage less prominent.

* Mon Jan 06 2014 Jan Pazdziora <jpazdziora@redhat.com> - 0.5-1
- Initial release.
