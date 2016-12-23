# Define the kmod package name here.
%define kmod_name ufs

# If kversion isn't defined on the rpmbuild line, define it here.
%{!?kversion: %define kversion %(uname -r)}

%{!?name_suff: %define name_suff %{nil}}
%{!?onapp_release: %define onapp_release %{nil}}

%{!?version: %define version %(echo %{kversion} | cut -d'-' -f1)}
%{!?release: %define release %(echo %{kversion} | cut -d'-' -f2)}

Name:    %{kmod_name}-kmod
Version: %{version} 
Release: %{release}%{onapp_release} 
Group:   System Environment/Kernel
License: GPLv2
Summary: %{kmod_name} kernel module(s)
URL:     http://www.kernel.org/

BuildRequires: redhat-rpm-config
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-build-%(%{__id_u} -n)
ExclusiveArch: i686 x86_64

# Sources.
Source0:  %{kmod_name}-%{version}.tar.gz
Source5:  GPL-v2.0.txt
Source10: kmodtool-%{kmod_name}-el6%{name_suff}.sh
Patch0: ufs-kmod-super-ufs_fs_write.patch

# Magic hidden here.
%{expand:%(sh %{SOURCE10} rpmtemplate %{kmod_name}%{?name_suff} %{kversion} "")}

# Disable the building of the debug package(s).
%define debug_package %{nil}

# Define the filter.
%{!?__find_requires: %define __find_requires sh %{_builddir}/%{buildsubdir}/filter-requires.sh}

%description
This package provides the %{kmod_name} kernel module(s).
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
%setup -q -n %{kmod_name}-%{version}
%patch0 -p0
%{__cp} -a %{SOURCE5} .
echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}%{?name_suff}.conf
echo "/usr/lib/rpm/redhat/find-requires | %{__sed} -e '/^ksym.*/d'" > filter-requires.sh

%build
KSRC=%{_usrsrc}/kernels/%{kversion}
%{__make} -C "${KSRC}" %{?_smp_mflags} modules M=$PWD

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=extra/%{kmod_name}%{?name_suff}
KSRC=%{_usrsrc}/kernels/%{kversion}
%{__make} -C "${KSRC}" modules_install M=$PWD
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}%{?name_suff}.conf %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} -d %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}%{?name_suff}-%{version}/
%{__install} GPL-v2.0.txt %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}%{?name_suff}-%{version}/
# Set the module(s) to be executable, so that they will be stripped when packaged.
find %{buildroot} -type f -name \*.ko -exec %{__chmod} u+x \{\} \;
# Remove the unrequired files.
%{__rm} -f %{buildroot}/lib/modules/%{kversion}/modules.*

%clean
%{__rm} -rf %{buildroot}

%changelog
