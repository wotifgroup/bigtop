%define etc_zookeeper /etc/zookeeper
%define bin_zookeeper %{_bindir}
%define doc_zookeeper %{_docdir}/zookeeper-%{zookeeper_version}
%define lib_zookeeper /usr/lib/zookeeper
%define log_zookeeper /var/log/zookeeper
%define run_zookeeper /var/run/zookeeper
%define man_dir %{_mandir}

%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# SLES is more strict anc check all symlinks point to valid path
# But we do point to a hadoop jar which is not there at build time
# (but would be at install time).
# Since our package build system does not handle dependencies,
# these symlink checks are deactivated
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}


%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d

%else

%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d

%endif



Name: hadoop-zookeeper
Version: %{zookeeper_version}
Release: %{zookeeper_release}
Summary: A high-performance coordination service for distributed applications.
URL: http://hadoop.apache.org/zookeeper/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
License: APL2
Source0: zookeeper-%{zookeeper_base_version}.tar.gz
Source1: hadoop-zookeeper.sh
Source2: hadoop-zookeeper.sh.suse
Source3: install_zookeeper.sh
Source4: zookeeper.1
BuildArch: noarch
BuildRequires: autoconf, automake, subversion

# RHEL6 provides natively java
%if 0%{?rhel} == 6
BuildRequires: java-1.6.0-sun-devel
Requires: java-1.6.0-sun
%else
BuildRequires: jdk >= 1.6
Requires: jre >= 1.6
%endif


%description 
ZooKeeper is a centralized service for maintaining configuration information, 
naming, providing distributed synchronization, and providing group services. 
All of these kinds of services are used in some form or another by distributed 
applications. Each time they are implemented there is a lot of work that goes 
into fixing the bugs and race conditions that are inevitable. Because of the 
difficulty of implementing these kinds of services, applications initially 
usually skimp on them ,which make them brittle in the presence of change and 
difficult to manage. Even when done correctly, different implementations of these services lead to management complexity when the applications are deployed.  

%package server
Summary: The Hadoop Zookeeper server
Group: System/Daemons
Provides: hadoop-zookeeper-server
Requires: hadoop-zookeeper = %{version}-%{release}
BuildArch: noarch

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%else
# Required for init scripts
Requires: redhat-lsb
%endif

%description server
This package starts the zookeeper server on startup

%prep
%setup -n zookeeper-%{zookeeper_base_version}

%build
ant -f build.xml package -Dversion=%{version}

%install
%__rm -rf $RPM_BUILD_ROOT
cp $RPM_SOURCE_DIR/zookeeper.1 .
sh $RPM_SOURCE_DIR/install_zookeeper.sh \
          --build-dir=. \
          --doc-dir=%{doc_zookeeper} \
          --prefix=$RPM_BUILD_ROOT


%if  %{?suse_version:1}0
orig_init_file=$RPM_SOURCE_DIR/hadoop-zookeeper.sh.suse
%else
orig_init_file=$RPM_SOURCE_DIR/hadoop-zookeeper.sh
%endif

%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/
init_file=$RPM_BUILD_ROOT/%{initd_dir}/hadoop-zookeeper-server
%__cp $orig_init_file $init_file
chmod 755 $init_file


%pre
getent group zookeeper >/dev/null || groupadd -r zookeeper
getent passwd zookeeper > /dev/null || useradd -c "ZooKeeper" -s /sbin/nologin -g zookeeper -r -d %{run_zookeeper} zookeeper 2> /dev/null || :

%__install -d -o zookeeper -g zookeeper -m 0755 %{run_zookeeper}
%__install -d -o zookeeper -g zookeeper -m 0755 /var/log/zookeeper

# Manage configuration symlink
%post
%{alternatives_cmd} --install %{etc_zookeeper}/conf %{name}-conf %{etc_zookeeper}/conf.dist 30
%__install -d -o zookeeper -g zookeeper -m 0755 /var/lib/zookeeper

%preun
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_zookeeper}/conf.dist
fi

%post server
	chkconfig --add hadoop-zookeeper-server

%preun server
	service hadoop-zookeeper-server stop
	chkconfig --del hadoop-zookeeper-server

%files server
	%attr(0755,root,root) %{initd_dir}/hadoop-zookeeper-server

#######################
#### FILES SECTION ####
#######################
%files
%defattr(-,root,root)
%config %{etc_zookeeper}/conf.dist
%{lib_zookeeper}
%{bin_zookeeper}/zookeeper-server
%{bin_zookeeper}/zookeeper-client
%doc %{doc_zookeeper}
%{man_dir}/man1/zookeeper.1.gz
