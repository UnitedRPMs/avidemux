%global _iconsdir %{_datadir}/icons
%bcond_without aften
%global gitdate 20170923
%global commit0 4865a8aaa1a31902736d151d4ce0b0e2131bc425
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

Name:           avidemux
Version:        2.7.0
Release:        2%{?gver}%{?dist}
Summary:        Graphical video editing and transcoding tool

License:        GPLv2+
URL:            http://www.avidemux.org
Source0:	https://github.com/mean00/avidemux2/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Patch:          desktop-avidemux.patch

# qt
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5OpenGL)
BuildRequires:	pkgconfig(Qt5Script)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	qt5-qtbase-devel
BuildRequires:  cmake(Qt5LinguistTools)

# Utilities
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

# Libraries
BuildRequires:  yasm-devel
BuildRequires:  libxml2-devel >= 2.6.8
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  js-devel
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
BuildRequires:  faad2-devel >= 2.0
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
BuildRequires:  x264-devel
BuildRequires:  x265-devel

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
%autosetup -n %{name}2-%{commit0} -p0

for i in bash cmake cpp sh sql txt; do
  find . -name \*.$i -print0 | xargs -0 dos2unix -q
done

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
install -D avidemux2.desktop %{buildroot}%{_datadir}/applications/%{name}-qt.desktop
mkdir -p %{buildroot}%{_iconsdir}
convert avidemux_icon.png -resize 32x32 %{buildroot}%{_iconsdir}/%{name}-qt.png

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
%{_libdir}/ADM_plugins6/autoScripts/

%files cli -f buildPluginsCLI/install_manifest.txt
%{_bindir}/avidemux3_cli
%{_libdir}/libADM_UI_Cli*.so
%{_libdir}/libADM_render6_cli.so

%files qt 
%{_bindir}/avidemux3_qt5
%{_bindir}/avidemux3_jobs_qt5
%{_libdir}/libADM_UIQT*.so
%{_libdir}/libADM_render6_QT5.so
%{_datadir}/applications/avidemux-qt.desktop
%{_datadir}/icons/avidemux-qt.png
%{_mandir}/man1/avidemux.1.gz
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
