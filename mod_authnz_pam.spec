%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}

Summary: PAM Basic Authentication provider and authorization checker
Name: mod_authnz_pam
Version: 0.5
Release: 1%{?dist}
License: ASL 2.0
Group: System Environment/Daemons
URL: http://www.adelton.com/apache/mod_authnz_pam/
Source0: http://www.adelton.com/apache/mod_authnz_pam/%{name}-%{version}.tar.gz
BuildRequires: httpd-devel
BuildRequires: pam-devel
BuildRequires: pkgconfig
Requires(pre): httpd
Requires: httpd
Requires: pam

# Suppres auto-provides for module DSO
%{?filter_provides_in: %filter_provides_in %{_libdir}/httpd/modules/.*\.so$}
%{?filter_setup}

%description
mod_authnz_pam is a Basic Authentication provider which runs the
[login, password] authentication through the PAM stack; it can also
be used as an authorization module, supplementing authentication
done by other modules, for example mod_auth_kerb.

%prep
%setup -q -n %{name}-%{version}

%build
%{_httpd_apxs} -c mod_authnz_pam.c -lpam -Wall -pedantic

%install
rm -rf $RPM_BUILD_ROOT
install -Dm 755 .libs/mod_authnz_pam.so $RPM_BUILD_ROOT%{_httpd_moddir}/mod_authnz_pam.so

%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
# httpd >= 2.4.x
install -Dp -m 0644 authnz_pam.conf $RPM_BUILD_ROOT%{_httpd_modconfdir}/55-authnz_pam.conf
%else
# httpd <= 2.2.x
install -Dp -m 0644 authnz_pam.conf $RPM_BUILD_ROOT%{_httpd_confdir}/authnz_pam.conf
%endif

%files
%doc README LICENSE
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_modconfdir}/*.conf
%else
%config(noreplace) %{_httpd_confdir}/authnz_pam.conf
%endif
%{_httpd_moddir}/*.so

%changelog
* Mon Jan 06 2014 Jan Pazdziora - 0.5-1
- Initial release.
