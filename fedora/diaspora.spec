# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | \
    sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global         debug_package   %{nil}

%define         git_release     HEAD

Summary:        A social network server
Name:           diaspora
Version:        0.0
Release:        0.1.%{git_release}%{?dist}
License:        AGPLv3
Group:          Applications/Communications
URL:            http://www.joindiaspora.com/
Vendor:         joindiaspora.com
Source:         %{name}-%{version}-%{git_release}.tar.gz
Source1:        diaspora
Source2:        diaspora-setup
Source3:        diaspora.logconf
Source4:        make_rel_symlink.py
Source5:        diaspora-thin.conf
Source6:        diaspora-websocket.conf
Source7:        diaspora-redis.conf
Source8:        diaspora-resque.conf
Source9:        diaspora-daemon
BuildArch:      noarch
BuildRoot:      %{_rmpdir}/not-used-in-fedora/

Requires:       mongodb-server
Requires:       redis
Requires:       ruby(abi) = 1.8
Requires:       diaspora-bundle = %{version}


%description
A privacy aware, personally controlled, do-it-all and
open source social network server.


%prep
%setup -q -n %{name}-%{version}-%{git_release}

find . -perm /u+x -type f -exec \
    sed -i 's|^#!/usr/local/bin/ruby|#!/usr/bin/ruby|' {} \; > /dev/null

%build
rm -rf master/vendor/bundle
chmod 755 master/lib/cruise/build.rb

%install
rm -fr $RPM_BUILD_ROOT

cp master/GNU-AGPL-3.0 master/COPYRIGHT master/README.md master/AUTHORS .
cp master/pkg/fedora/README.md README-Fedora.md

mkdir -p $RPM_BUILD_ROOT/etc/init.d
cp %SOURCE1  $RPM_BUILD_ROOT/etc/init.d
sed -i '/^cd /s|.*|cd %{_datadir}/diaspora/master|'  \
       $RPM_BUILD_ROOT/etc/init.d/diaspora
mkdir -p $RPM_BUILD_ROOT/etc/init
cp %SOURCE5 %SOURCE6 %SOURCE7 %SOURCE8 $RPM_BUILD_ROOT/etc/init

mkdir -p  $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
cp %SOURCE3  $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/diaspora
mkdir -p  $RPM_BUILD_ROOT/%{_sysconfdir}/diaspora

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/diaspora
cp -ar master $RPM_BUILD_ROOT/%{_datadir}/diaspora
cp -ar  master/.bundle $RPM_BUILD_ROOT/%{_datadir}/diaspora/master

cp %SOURCE9  $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/script
rm -rf $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/vendor/*
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/uploads
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/tmp

mkdir -p    $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/pkg/fedora
cp %SOURCE2 $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/pkg/fedora
%{SOURCE4}  \
    $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/pkg/fedora/diaspora-setup \
    $RPM_BUILD_ROOT/%{_datadir}/diaspora/diaspora-setup

for file in server.sh environment.rb app_config.yml.example;  do
    mv $RPM_BUILD_ROOT%{_datadir}/diaspora/master/config/$file \
        $RPM_BUILD_ROOT/%{_sysconfdir}/diaspora/$file
    %{SOURCE4} \
        $RPM_BUILD_ROOT/%{_sysconfdir}/diaspora/$file \
        $RPM_BUILD_ROOT%{_datadir}/diaspora/master/config/$file
done

mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/log/diaspora
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/run/diaspora
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/uploads
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/tmp

%{SOURCE4} $RPM_BUILD_ROOT/%{_localstatedir}/log/diaspora \
           $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/log
%{SOURCE4} $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/uploads \
           $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/public/uploads
%{SOURCE4} $RPM_BUILD_ROOT/%{_localstatedir}/lib/diaspora/tmp \
           $RPM_BUILD_ROOT/%{_datadir}/diaspora/master/tmp

find  $RPM_BUILD_ROOT/%{_datadir}/diaspora  -type d        \
    -fprintf dirs '%%%dir "%%p"\n'
find  -L $RPM_BUILD_ROOT/%{_datadir}/diaspora  -type f     \
    -fprintf files '"%%p"\n'
cat files >> dirs && mv -f dirs files
sed -i   -e '\|.*/master/config.ru"$|d'                    \
         -e '\|.*/master/config/environment.rb"$|d'        \
         -e '\|.*/run/diaspora"$|d'                        \
         -e 's|%{buildroot}||' -e 's|//|/|' -e '/""/d'     \
      files


%post
/sbin/chkconfig --add  diaspora || :


%preun
if [ $1 -eq 0 ] ; then
    service diaspora stop  &>/dev/null || :
    /sbin/chkconfig --del  diaspora
fi


%clean
rm -fr $RPM_BUILD_ROOT


%files -f files
%defattr(-, root, root, 0755)
%doc AUTHORS README.md GNU-AGPL-3.0 COPYRIGHT README-Fedora.md
%attr(-, diaspora, diaspora) %{_datadir}/diaspora/master/config.ru
%attr(-, diaspora, diaspora) %{_datadir}/diaspora/master/config/environment.rb
%attr(-, diaspora, diaspora) %{_datadir}/diaspora/master/pkg/fedora/dist
%attr(-, diaspora, diaspora) %{_datadir}/diaspora/master/pkg/ubuntu/dist
%attr(-, diaspora, diaspora) %{_localstatedir}/log/diaspora
%attr(-, diaspora, diaspora) %{_localstatedir}/lib/diaspora/uploads
%attr(-, diaspora, diaspora) %{_localstatedir}/lib/diaspora/tmp
%attr(-, diaspora, diaspora) %{_localstatedir}/run/diaspora

%dir %{_sysconfdir}/diaspora
%config(noreplace) %{_sysconfdir}/diaspora/environment.rb
%config(noreplace) %{_sysconfdir}/diaspora/server.sh
%config(noreplace) %{_sysconfdir}/diaspora/app_config.yml.example
%{_datadir}/diaspora/master/tmp
%{_datadir}/diaspora/master/public/uploads
%{_datadir}/diaspora/master/log

%config(noreplace) %{_sysconfdir}/logrotate.d/diaspora

%{_sysconfdir}/init.d/diaspora
%{_sysconfdir}/init/diaspora-websocket.conf
%{_sysconfdir}/init/diaspora-thin.conf
%{_sysconfdir}/init/diaspora-redis.conf
%{_sysconfdir}/init/diaspora-resque.conf


%changelog
* Fri Sep 24 2010 Alec Leamas  <leamas.alec@gmail.com>  0.0-1.1009280542_859ec2d
  - Initial attempt to create a spec fi+le

# rubygem-term-ansicolor  in repo (1.0.5)
# rubygem-abstract:       in repo (1.0)
# rubygem-actionpack      in repo (2.3.5), rawhide (2.3.8)
# rubygem-builder         in repo (2.1.2)
# rubygem-columnize       in repo (0.3.1)
# rubygem-crack           in repo (0.1.8)
# rubygem-cucumber        in repo (0.9.0)
# diff-lcs                in rep  (1.1.2)
# eventmachine            in repo (0.12.10)
# gherkin                 in repo (2.2.4)
# rubygem-json            in repo (1.1.9), rawhide(1.4.6)
# rubygem-linecache       in repo (0.43)
# rubygem-mime-types      in repo (1.16)
# rubygem-mocha           in repo (0.9.8)
# rubygem-net-ssh         in repo (2.0.23)
# rubygem-nokogiri        in repo (1.4.3.1)
# rubygem-rake            in repo (0.8.7)
# rubygem-ruby-debug      in repo (0.10.4)
# rubygem-ruby-debug-base in repo (0.10.4)
# rubygem-term-ansicolor  in repo (1.0.5)
# rubygem-thin            in repo(1.2.5), rawhide(1.2.7)
# rubygem-uuidtools       in repo(2.1.1)
