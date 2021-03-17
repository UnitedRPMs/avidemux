%global _iconsdir %{_datadir}/icons
%bcond_without aften
%global gitdate 20200713
%global commit0 0298788c4872990215190e7351c7456f2801daa8
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

# translation files
%global commit1 5543d9240c656062fd04108f15770694c04865ca
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

%define _legacy_common_support 1

Name:           avidemux
Version:        2.7.8
Release:        7%{?gver}%{?dist}
Summary:        Graphical video editing and transcoding tool

License:        GPLv2+
URL:            http://www.avidemux.org
Source0:	https://github.com/mean00/avidemux2/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Source1:	https://github.com/mean00/avidemux2_i18n/archive/%{commit1}.zip#/avidemux2_i18n-%{shortcommit1}.tar.gz


Patch:		qt-5.15.diff
Patch1:		log.diff
Patch2:		file.patch
Patch3:		fix_verbose.patch
Patch4:		add_settings_pluginui_message_error.patch
# qt
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5OpenGL)
BuildRequires:	pkgconfig(Qt5Script)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	qt5-qtbase-devel
BuildRequires:  cmake(Qt5LinguistTools)

# Utilities
BuildRequires:	make
BuildRequires:  cmake
BuildRequires:  gettext intltool
BuildRequires:  libxslt
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig
BuildRequires:  sqlite-devel
BuildRequires:	fakeroot
BuildRequires:	chrpath
BuildRequires:	ImageMagick-devel
BuildRequires:	libxslt-devel
BuildRequires:	dos2unix
%if 0%{?fedora} >= 29
Recommends:	python-unversioned-command
%endif

# Libraries
BuildRequires:  yasm-devel
BuildRequires:  libxml2-devel >= 2.6.8
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  libXv-devel
BuildRequires:  libXmu-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  libass-devel
BuildRequires:	pkgconfig(zlib)

# Sound out
BuildRequires:  alsa-lib-devel >= 1.0.3
BuildRequires:  pulseaudio-libs-devel

# Video out
BuildRequires:  SDL-devel >= 1.2.7
BuildRequires:  mesa-libGL-devel mesa-libGLU-devel
BuildRequires:  libvdpau-devel
BuildRequires:	libva-devel

# Audio Codecs
BuildRequires:  a52dec-devel >= 0.7.4
%{?_with_faac:BuildRequires:  faac-devel >= 1.24}
BuildRequires:  faad2-devel >= 2.9.1
BuildRequires:  lame-devel >= 3.96.1
BuildRequires:  libmad-devel >= 0.15.1
BuildRequires:  libogg-devel >= 1.1
BuildRequires:  libvorbis-devel >= 1.0.1
BuildRequires:  libdca-devel
BuildRequires:  opencore-amr-devel
BuildRequires:  libvpx-devel
BuildRequires:  twolame-devel
%if %{with aften}
BuildRequires:	aften-devel
%endif

# Video Codecs
BuildRequires:  xvidcore-devel >= 1.0.2
BuildRequires:  x264-devel >= 1:0.161
BuildRequires:  x265-devel >= 3.4 

# Main package is a metapackage, bring in something useful.
Requires:       %{name}-gui = %{version}-%{release}



%description
Avidemux is a free video editor designed for simple cutting, filtering and
encoding tasks. It supports many file types, including AVI, DVD compatible
MPEG files, MP4 and ASF, using a variety of codecs. Tasks can be automated
using projects, job queue and powerful scripting capabilities.

This is a meta package that brings in all interfaces: QT and CLI.



%package cli
Summary:        CLI for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description cli
This package provides a command-line interface to editing videos with %{name}.

%package libs
Summary:        Libraries for %{name}

%description libs
This package contains the runtime libraries for %{name}.


%package qt
Summary:        Qt interface for %{name}
BuildRequires:  libxslt
Provides:       %{name}-gui = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes:      %{name}-gtk < 2.6.10

%description qt
This package contains the Qt graphical interface for %{name}.


%package i18n
Summary:        Translations for %{name}
Requires:       %{name}    = %{version}-%{release}
Requires:       %{name}-qt = %{version}-%{release}
BuildArch:      noarch

%description i18n
This package contains translation files for %{name}.

%package	devel
Summary:	Header files for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description	devel
Header files for %{name}.


%prep
%autosetup -n %{name}2-%{commit0} -a1 -p1
mv -f avidemux2_i18n-%{commit1} avidemux2_i18n-%{version}

for i in bash cmake cpp sh sql txt; do
  find . -name \*.$i -print0 | xargs -0 dos2unix -q
done

rm -rf $PWD/avidemux/qt4/i18n/ && mv -f avidemux2_i18n-%{version} $PWD/avidemux/qt4/i18n


sed -i 's|../avidemux/qt4|../avidemux/qt4 -DLRELEASE_EXECUTABLE=/usr/bin/lrelease-qt5|' bootStrap.bash

%build
export CXXFLAGS="%optflags -D__STDC_CONSTANT_MACROS -fno-strict-aliasing"
chmod 755 bootStrap.bash


bash bootStrap.bash \
     --with-core \
     --with-cli  \
     --with-plugins

%install
cp -a install/* %{buildroot}
mkdir -p %{buildroot}%{_datadir}/applications

mkdir -p %{buildroot}%{_mandir}/man1
install -m 644 man/avidemux.1 %{buildroot}%{_mandir}/man1
chrpath --delete %{buildroot}%{_libdir}/*.so*
chrpath --delete %{buildroot}%{_libdir}/ADM_plugins6/*/*.so
chrpath --delete %{buildroot}%{_bindir}/*
rm -rf %{buildroot}%{_datadir}/ADM6_addons

# Fix library permissions
find %{buildroot}%{_libdir} -type f -name "*.so.*" -exec chmod 0755 {} \;


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%doc AUTHORS README

%files libs -f buildPluginsCommon/install_manifest.txt
%license COPYING
%dir %{_datadir}/avidemux6
%{_libdir}/libADM*
%exclude %{_libdir}/libADM_render*
%exclude %{_libdir}/libADM_UI*
# Catch the stuff missed using install_manifest.txt
%if 0%{?fedora} <= 29
%{_libdir}/ADM_plugins6/autoScripts/
%endif

%files cli -f buildPluginsCLI/install_manifest.txt
%{_bindir}/avidemux3_cli
%{_libdir}/libADM_UI_Cli*.so
%{_libdir}/libADM_render6_cli.so

%files qt 
%{_bindir}/avidemux3_qt5
%{_bindir}/avidemux3_jobs_qt5
%{_libdir}/libADM_UIQT*.so
%{_libdir}/libADM_render6_QT5.so
%{_datadir}/applications/org.avidemux.Avidemux.desktop
%{_datadir}/icons/hicolor/128x128/apps/org.avidemux.Avidemux.png
%{_mandir}/man1/avidemux.1.gz
%{_datadir}/metainfo/org.avidemux.Avidemux.appdata.xml
# QT plugins
%{_libdir}/ADM_plugins6/videoEncoders/
%{_libdir}/ADM_plugins6/videoFilters/qt5/
%{_libdir}/ADM_plugins6/scriptEngines/
%{_libdir}/ADM_plugins6/pluginSettings/
%{_libdir}/ADM_plugins6/shaderDemo/

%files i18n
%{_datadir}/avidemux6/qt5/i18n/

%files devel
%{_includedir}/%{name}/


%changelog

* Mon Mar 15 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.8-7.git0298788
- Updated to 2.7.8

* Sat Jan 23 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.7-7.git37c73c4
- Updated to 2.7.7

* Thu Jan 21 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.6-8.git32dfeff 
- Rebuilt and updated to current commit

* Mon Jul 13 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.6-7.gitd48b500 
- Updated to 2.7.6

* Sat Jul 04 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-13.gitd48b500 
- Rebuilt for x264

* Sat May 30 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-12.gitd48b500 
- Rebuilt for x265

* Mon Feb 24 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-11.gitd48b500 
- Rebuilt for x265

* Mon Dec 16 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-10.gitd48b500 
- Rebuilt for x265

* Sat Nov 09 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-9.gitd48b500 
- Rebuilt for faad2

* Thu Sep 05 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-8.gitd48b500 
- Rebuilt

* Thu Aug 15 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.4-7.gitd48b500 
- Updated to 2.7.4-7.gitd48b500 

* Sat Aug 03 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.3-9.git176aa02 
- Rebuilt for x265

* Sat Jun 22 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.3-8.git176aa02 
- Rebuilt for x265

* Wed Apr 10 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.3-7.git176aa02 
- Updated 2.7.3-7.git176aa02

* Fri Mar 22 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-13.gitd667da3  
- Rebuilt for x264

* Fri Feb 08 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-12.gitd667da3  
- Rebuilt for x265

* Fri Oct 12 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-11.gitd667da3  
- Automatic Mass Rebuild

* Fri Oct 05 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-10.gitd667da3  
- Automatic Mass Rebuild

* Mon Jun 18 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-9.gitd667da3  
- Rebuild for libass

* Wed Jun 06 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.1-8.gitd667da3  
- Updated to 2.7.1-8.gitd667da3

* Sun May 27 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-8.gitca14f0b  
- Automatic Mass Rebuild

* Mon Jan 29 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-7.gitca14f0b
- Updated to current commit

* Tue Jan 16 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-6.git4865a8a  
- Rebuilt for libva 2.0

* Wed Dec 06 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-5.git4865a8a  
- Automatic Mass Rebuild

* Thu Oct 05 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-4.git4865a8a  
- Automatic Mass Rebuild

* Sat Sep 30 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-3.git4865a8a  
- Automatic Mass Rebuild

* Thu Sep 28 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 2.7.0-2.git4865a8a  
- Automatic Mass Rebuild

* Sat Sep 23 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.7.0-1.git4865a8a
- Updated to 2.7.0-1.git4865a8a

* Thu May 25 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.20-3.git46b6b02
- Updated to 2.6.20-3.git46b6b02
- Fix build with cmake 3.9.0

* Thu May 25 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.20-2.git91b8d8e
- Updated to 2.6.20-2.git91b8d8e

* Tue Apr 04 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.19-2
- Updated to 2.6.19-2

* Fri Mar 17 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.18-2
- Included missed files

* Mon Jan 09 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.18-1
- Updated to 2.6.18

* Sat Jan 07 2017 Pavlo Rudyi <paulcarroty at riseup.net> - 2.6.16-1
- Updated to 2.6.16

* Tue Aug 30 2016 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6.13-1
- Updated to 2.6.13

* Tue Aug 16 2016 Leigh Scott <leigh123linux@googlemail.com> - 2.6.12-5
- Add hardening to LDFLAGS

* Mon Jul 25 2016 Richard Shaw <hobbes1069@gmail.com> - 2.6.12-4
- Add patch to fix qt gui issues, fixes BZ#4035.

* Mon Jul 11 2016 Hans de Goede <j.w.r.degoede@gmail.com> - 2.6.12-3
- Really fix building with GCC6, patch provided by Dan Horák <dan@danny.cz>

* Sat Jun 25 2016 Richard Shaw <hobbes1069@gmail.com> - 2.6.12-2
- Bump for rebuild in new infra.
- Add patch for GCC 6 narrowing conversion and other GCC 6 errors.

* Mon Apr  4 2016 Richard Shaw <hobbes1069@gmail.com> - 2.6.12-1
- Fix library file permissions, BZ#3923.

* Mon Nov 30 2015 Richard Shaw <hobbes1069@gmail.com> - 2.6.10-4
- Fix un-owned dir, BZ#3881.
- Fix broken scriptlet, BZ#3880.

* Sat Nov 28 2015 Richard Shaw <hobbes1069@gmail.com> - 2.6.10-3
- Revert back to QT4.

* Mon Nov  9 2015 Richard Shaw <hobbes1069@gmail.com> - 2.6.10-2
- Fix bug introduced while debugging FTBFS problem. Fixes RFBZ#3830.

* Tue Jun 16 2015 Richard Shaw <hobbes1069@gmail.com> - 2.6.10-1
- Update to latest upstream release.
- Disable GTK interface as it is unmaintained and does not build.

* Wed Jan 21 2015 Richard Shaw <hobbes1069@gmail.com> - 2.6.8-3
- Fix directory ownership.

* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 2.6.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun May 11 2014 Richard Shaw <hobbes1069@gmail.com> - 2.6.8-1
- Update to latest upstream release.

* Sat Mar 22 2014 Sérgio Basto <sergio@serjux.com> - 2.6.7-4
- Rebuilt for x264

* Thu Mar 06 2014 Nicolas Chauvet <kwizart@gmail.com> - 2.6.7-3
- Rebuilt for x264

* Thu Mar 06 2014 Nicolas Chauvet <kwizart@gmail.com> - 2.6.7-2
- Rebuilt

* Mon Jan 27 2014 Richard Shaw <hobbes1069@gmail.com> - 2.6.7-1
- Update to latest upstream release.
- Obsolete unneeded devel subpackage.

* Tue Nov 05 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.6.4-8
- Rebuilt for x264/FFmpeg

* Tue Oct 22 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.6.4-7
- Rebuilt for x264

* Sat Jul 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.6.4-6
- Rebuilt for x264

* Mon Jun 24 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.4-5
- Can't have arch requirement on noarch package, fixes BZ#2840.

* Sun Jun 16 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.4-3
- Move translations to their own subpackage to make use optional, fixes BZ#2825.

* Mon Jun  3 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.4-2
- Fix packaging of translations (qt package only).

* Wed May 15 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.4-1
- Update to latest upstream release.

* Sun May 05 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.3-2
- Rebuild for updated x264.

* Wed Mar 20 2013 Richard Shaw <hobbes1069@gmail.com> - 2.6.3-1
- Update to latest bugfix release.

* Sun Jan 20 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.6.1-2
- Rebuilt for ffmpeg/x264

* Sat Dec 22 2012 Richard Shaw <hobbes1069@gmail.com> - 2.6.1-1
- Update to latest upstream release.

* Sun Dec 16 2012 Richard Shaw <hobbes1069@gmail.com> - 2.6.0-4
- Make sure we're building all available plugins. (#2575)
- Don't install the gtk interface when all you want is the qt one. (#2574)
- Exclude arm as a build target. (#2466)

* Fri Nov 23 2012 Nicolas Chauvet <kwizart@gmail.com> - 2.6.0-2
- Rebuilt for x264

* Sun Oct 14 2012 Richard Shaw <hobbes1069@gmail.com> - 2.6.0-1
- Update to new upstream release.
