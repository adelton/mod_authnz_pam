%{!?_httpd_mmn: %{expand: %%global _httpd_mmn %%(cat %{_includedir}/httpd/.mmn || echo 0-0)}}
%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}

Summary: PAM authorization checker and PAM Basic Authentication provider
Name: mod_authnz_pam
Version: 1.2.3
Release: 1%{?dist}
License: ASL 2.0
Group: System Environment/Daemons
URL: https://www.adelton.com/apache/mod_authnz_pam/
Source0: https://www.adelton.com/apache/mod_authnz_pam/%{name}-%{version}.tar.gz
BuildRequires: gcc
BuildRequires: httpd-devel
BuildRequires: pam-devel
BuildRequires: pkgconfig
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
%{_httpd_apxs} -c -Wc,"%{optflags} -Wall -Werror -pedantic -std=c99" -lpam mod_authnz_pam.c
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
echo > authnz_pam.confx
echo "# Load the module in %{_httpd_modconfdir}/55-authnz_pam.conf" >> authnz_pam.confx
cat authnz_pam.conf >> authnz_pam.confx
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
* Sun Jan 23 2022 Jan Pazdziora <jpazdziora@redhat.com> - 1.2.3-1
- Change default redirect status for AuthPAMExpiredRedirect
  to 303 See Other, make it configurable.

* Tue Mar 30 2021 Jan Pazdziora <jpazdziora@redhat.com> - 1.2.2-1
- Use ap_get_useragent_host for interoperability with mod_remoteip.

* Thu Jul 09 2020 Jan Pazdziora <jpazdziora@redhat.com> - 1.2.1-1
- Store password to cache only after passing all PAM checks, including account.

* Tue Jul 17 2018 Jan Pazdziora <jpazdziora@redhat.com> - 1.2.0-1
- Add support for mod_authn_socache.

* Fri Feb 23 2018 Jan Pazdziora <jpazdziora@redhat.com> - 1.1.0-8
- https://fedoraproject.org/wiki/Packaging:C_and_C%2B%2B#BuildRequires_and_Requires

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.0-7
- Escape macros in %%changelog

* Tue Nov 22 2016 Jan Pazdziora <jpazdziora@redhat.com> - 1.1.0-1
- Logging improvements; success logging moved from notice to info level.
- Fix redirect for AuthPAMExpiredRedirect with Basic Auth.
- Fix AuthPAMExpiredRedirect %%s escaping on Apache 2.2.

* Mon Mar 21 2016 Jan Pazdziora <jpazdziora@redhat.com> - 1.0.2-1
- 1319166 - the Requires(pre) httpd does not seem to be needed.

* Tue Nov 10 2015 Jan Pazdziora <jpazdziora@redhat.com> - 1.0.1-1
- Fix handling of pre-auth / OTP / 2FA situations.

* Thu Jun 25 2015 Jan Pazdziora <jpazdziora@redhat.com> - 1.0.0-1
- Add support for AuthPAMExpiredRedirect.

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
