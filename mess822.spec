Summary:	Collection of utilities for parsing Internet mail messages
Summary(pl):	Zestaw narzêdzi do przetwarzania internetowych listów elektronicznych
Name:		mess822
Version:	0.58
Release:	0.68
License:	http://cr.yp.to/distributors.html (free to use)
Group:		Networking/Daemons
Source0:	http://cr.yp.to/software/%{name}-%{version}.tar.gz
# Source0-md5:	8ce4c29c994a70dcaa30140601213dbe
Source1:	http://glen.alkohol.ee/pld/qmail/qmail-conf-20050131.3.tar.bz2
# Source1-md5:	8336934dbecd48e9262ceeefc369bc70
Patch0:		%{name}-errno.patch
Patch1:		http://qmail.gurus.com/mess822-smtp-auth-patch.txt
Patch2:		http://www.inwonder.net/~dayan/soft/ofmipd-date-localtime.patch
Patch3:		%{name}-quote.patch
URL:		http://cr.yp.to/mess822.html
Requires:	daemontools >= 0.76-1.4
Requires:	qmail >= 1.03-56.87
Requires:	ucspi-tcp >= 0.88
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define 	tcprules 	/etc/tcprules.d
%define		supervise	%{_sysconfdir}/ofmipd

%description
The mess822 package contains several applications that work with
qmail:
- ofmipd rewrites messages from dumb clients. It supports a database
  of recognized senders and From lines, using cdb for fast lookups.
- new-inject is an experimental new version of qmail-inject. It
  includes a flexible user-controlled hostname rewriting mechanism.
- iftocc can be used in .qmail files. It checks whether a known
  address is listed in To or Cc.
- 822header, 822field, 822date, and 822received extract various pieces
  of information from a mail message.
- 822print converts a message into an easier-to-read format.

Additionally this package contains support for LOGIN and PLAIN
authorization. Please read README.auth.

Also this package contains patch for $QMAILQUEUE support.

%description -l pl
Pakiet mess822 zawiera kilka aplikacji dzia³aj±cych z qmailem:
- ofmipd przepisuje wiadomo¶ci od prymitywnych klientów. Obs³uguje
  bazê danych rozpoznawanych nadawców i linii From, korzystaj±c z cdb
  w celu szybkiego wyszukiwania.
- new-inject to eksperymentalna nowa wersja programu qmail-inject.
  Zawiera elastyczny mechanizm przepisywania nazw hostów sterowany
  przez u¿ytkownika.
- iftocc mo¿e byæ u¿ywany w plikach .qmail. Sprawdza, czy znany adres
  jest wymieniony w To lub Cc.
- 822header, 822field, 822date i 822received wyci±gaj± ró¿ne
  informacje z wiadomo¶ci.
- 822print konwertuje wiadomo¶æ do formatu ³atwiejszego do
  przeczytania.

Dodatkowo pakiet zawiera obs³ugê autoryzacji LOGIN i PLAIN. Proszê
przeczytaæ plik README.auth.

Ten pakiet zawiera tak¿e ³atê do obs³ugi $QMAILQUEUE.

%package devel
Summary:	mess822 - Development header files and libraries
Summary(pl):	mess822 - pliki nag³ówkowe i biblioteki programistyczne
Group:		Development/Libraries

%description devel
This package contains the development header files and libraries.

%description devel -l pl
Ten pakiet zawiera pliki nag³ówkowe i biblioteki programistyczne.

%prep
%setup -q -a1
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p1

%build
echo %{__cc} %{rpmcflags} > conf-cc
echo %{__cc} > conf-ld
echo %{_prefix} > conf-home
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sysconfdir},%{_includedir},%{_libdir}} \
	$RPM_BUILD_ROOT{%{_mandir}/man{1,3,5,8},%{_sbindir}}

install leapsecs.dat $RPM_BUILD_ROOT%{_sysconfdir}
install ofmipname iftocc new-inject 822field 822header 822date \
	822received 822print $RPM_BUILD_ROOT%{_bindir}
install ofmipd $RPM_BUILD_ROOT%{_sbindir}

install mess822.h $RPM_BUILD_ROOT%{_includedir}
install mess822.a $RPM_BUILD_ROOT%{_libdir}

install iftocc.1 new-inject.1 822field.1 822header.1 822date.1 822received.1 \
	822print.1 $RPM_BUILD_ROOT%{_mandir}/man1
install rewriting.5 $RPM_BUILD_ROOT%{_mandir}/man5
install ofmipd.8 ofmipname.8 $RPM_BUILD_ROOT%{_mandir}/man8
install mess822.3 mess822_addr.3 mess822_date.3 mess822_fold.3 mess822_quote.3 \
	mess822_token.3 mess822_when.3 $RPM_BUILD_ROOT%{_mandir}/man3

PV=`basename %{SOURCE1}`
cd ${PV%.tar.bz2}

for d in '' log; do
	install -d $RPM_BUILD_ROOT/var/log/{,archiv/}/ofmipd/$d

	install -d $RPM_BUILD_ROOT%{supervise}/$d
	install -d $RPM_BUILD_ROOT%{supervise}/$d/supervise

	> $RPM_BUILD_ROOT%{supervise}/$d/supervise/lock
	> $RPM_BUILD_ROOT%{supervise}/$d/supervise/status
	mkfifo $RPM_BUILD_ROOT%{supervise}/$d/supervise/control
	mkfifo $RPM_BUILD_ROOT%{supervise}/$d/supervise/ok

	install run-ofmipd$d $RPM_BUILD_ROOT%{supervise}/$d/run
done

# FIXME: filename and location?
install ofmipname $RPM_BUILD_ROOT%{_sysconfdir}/ofmipd

install -d $RPM_BUILD_ROOT%{tcprules}
install Makefile.ofmipd $RPM_BUILD_ROOT%{tcprules}/Makefile.ofmip
install tcp.ofmipd.sample $RPM_BUILD_ROOT%{tcprules}/tcp.ofmip
> $RPM_BUILD_ROOT%{tcprules}/tcp.ofmip.cdb
> $RPM_BUILD_ROOT%{_sysconfdir}/ofmipd/ofmipname.cdb

install -d $RPM_BUILD_ROOT/etc/qmail/control
install conf-ofmipd $RPM_BUILD_ROOT/etc/qmail/control
cd ..

sed -ne '/diff/q;p' %{PATCH1} > README.auth

%clean
rm -rf $RPM_BUILD_ROOT

%post
# build .cdb if missing
if [ ! -e %{tcprules}/tcp.ofmip.cdb ]; then
	tcprules %{tcprules}/tcp.ofmip.cdb %{tcprules}/.tcp.ofmip.tmp < %{tcprules}/tcp.ofmip
	chown qmaild:root %{tcprules}/tcp.ofmip.cdb
	chmod 640 %{tcprules}/tcp.ofmip.cdb
fi
if [ ! -e %{_sysconfdir}/ofmipd/ofmipname.cdb ]; then
	ofmipname %{_sysconfdir}/ofmipd/ofmipname.cdb %{_sysconfdir}/ofmipd/ofmipname.cdb.tmp < %{_sysconfdir}/ofmipd/ofmipname
fi

# reload services on upgrade
if [ -d /service/ofmipd/supervise ]; then
	svc -t /service/ofmipd{,/log}
else
	echo "Please setup host and port where the service listens in"
	echo "/etc/qmail/control/conf-ofmipd and then start the service with supervise:"
	echo "ln -s %{supervise} /service/ofmipd"
	echo
fi

%preun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	# remove form supervise
	# http://cr.yp.to/daemontools/faq/create.html#remove
	if [ -d /service/ofmipd/supervise ]; then
		cd /service/ofmipd
		rm /service/ofmipd
		svc -dx . log
	fi
fi

%files
%defattr(644,root,root,755)
%doc BLURB CHANGES INSTALL README THANKS TODO VERSION README.auth

%{_sysconfdir}/leapsecs.dat
%config(noreplace) %verify(not mtime) /etc/qmail/control/conf-ofmipd
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*

%{_mandir}/man[1358]/*

%dir %{supervise}

%attr(1755,root,root) %dir %{supervise}
%attr(755,root,root) %{supervise}/run
%attr(700,root,root) %dir %{supervise}/supervise

%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %ghost %{supervise}/supervise/*
%attr(1755,root,root) %dir %{supervise}/log
%attr(755,root,root) %{supervise}/log/run
%attr(700,root,root) %dir %{supervise}/log/supervise
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %ghost %{supervise}/log/supervise/*
%attr(755,qmaill,root) %dir /var/log/ofmipd
%attr(750,root,root) %dir /var/log/archiv/ofmipd

%{tcprules}/Makefile.ofmip
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{tcprules}/tcp.ofmip
%attr(640,qmaild,root) %config(noreplace) %verify(not size mtime md5) %ghost %{tcprules}/tcp.ofmip.cdb

%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ofmipd/ofmipname
%attr(644,root,root) %config(noreplace) %verify(not size mtime md5) %ghost %{_sysconfdir}/ofmipd/ofmipname.cdb

%files devel
%defattr(644,root,root,755)
%{_includedir}/*.h
%{_libdir}/*.a
