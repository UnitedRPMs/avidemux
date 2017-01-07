%global _pkgbuilddir %{_builddir}/%{name}_%{version}
%global _iconsdir %{_datadir}/icons
%bcond_without aften

Name:           avidemux
Version:        2.6.13
Release:        1%{?dist}
Summary:        Graphical video editing and transcoding tool

License:        GPLv2+
URL:            http://www.avidemux.org
Source0:        http://downloads.sourceforge.net/%{name}/%{name}_%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/UnitedRPMs/avidemux/master/avidemux-qt.desktop
Patch0:         https://raw.githubusercontent.com/UnitedRPMs/avidemux/master/avidemux-2.6.15-disable-vpx-decoder-plugin.patch


# Utilities
BuildRequires:  cmake
BuildRequires:  gettext intltool
BuildRequires:  libxslt
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig
BuildRequires:  sqlite-devel
BuildRequires:  bzip2

# Libraries
BuildRequires:  yasm-devel
BuildRequires:  libxml2-devel >= 2.6.8
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  fribidi-devel
BuildRequires:  libXv-devel
BuildRequires:  libXmu-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  libass-devel

# Sound out
BuildRequires:  alsa-lib-devel >= 1.0.3
BuildRequires:  pulseaudio-libs-devel

# Video out
BuildRequires:  mesa-libGL-devel mesa-libGLU-devel
BuildRequires:  libvdpau-devel
BuildRequires:  libva-devel

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
BuildRequires:  opus-devel

# Video Codecs
BuildRequires:  xvidcore-devel >= 1.0.2
BuildRequires:  x264-devel
BuildRequires:  x265-devel
BuildRequires:  nvenc-devel

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
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-linguist
BuildRequires:  libxslt
Provides:       %{name}-gui = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes:      %{name}-gtk < 2.6.10
Obsoletes:      %{name}-help

%description qt
This package contains the Qt graphical interface for %{name}.

%package i18n
Summary:        Translations for %{name}
Requires:       %{name}    = %{version}-%{release}
Requires:       %{name}-qt = %{version}-%{release}
BuildArch:      noarch

%description i18n
This package contains translation files for %{name}.


%prep
%setup -q -n %{name}_%{version}
%patch0 -p1

# Remove sources of bundled libraries.
rm -rf avidemux_plugins/ADM_audioDecoders/ADM_ad_ac3/ADM_liba52 \
       avidemux_plugins/ADM_audioDecoders/ADM_ad_mad/ADM_libMad \
       avidemux_plugins/ADM_audioEncoders/twolame/ADM_libtwolame \
       avidemux_plugins/ADM_videoFilters6/ass/ADM_libass

%build
# Build avidemux_core
export LDFLAGS="-lc -Wl,--as-needed"
rm -rf build_core && mkdir build_core && pushd build_core
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       ../avidemux_core
make 

# We have to do a fake install so header files are avaialble for the other
# packages.
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd

# Build cli interface
rm -rf build_cli && mkdir build_cli && pushd build_cli
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DFAKEROOT=%{_pkgbuilddir}/fakeRoot \
       ../avidemux/cli
make %{?_smp_mflags}
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd

# Build QT5 gui
rm -rf build_qt5 && mkdir build_qt5 && pushd build_qt5
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DFAKEROOT=%{_pkgbuilddir}/fakeRoot \
       -DENABLE_QT5=TRUE \
       ../avidemux/qt4
make %{?_smp_mflags}
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd

# Build avidemux_plugins_common
rm -rf build_plugins_common && mkdir build_plugins_common && pushd build_plugins_common
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DFAKEROOT=%{_pkgbuilddir}/fakeRoot \
       -DAVIDEMUX_SOURCE_DIR=%{_builddir}/%{name}_%{version} \
       -DENABLE_QT5=TRUE \
       -DPLUGIN_UI=COMMON \
       -DUSE_EXTERNAL_LIBASS=TRUE \
       -DUSE_EXTERNAL_LIBMAD=TRUE \
       -DUSE_EXTERNAL_LIBA52=TRUE \
       -DUSE_EXTERNAL_TWOLAME=TRUE \
       ../avidemux_plugins
make %{?_smp_mflags}
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd

# Build avidemux_plugins_cli
rm -rf build_plugins_cli && mkdir build_plugins_cli && pushd build_plugins_cli
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DFAKEROOT=%{_pkgbuilddir}/fakeRoot \
       -DAVIDEMUX_SOURCE_DIR=%{_builddir}/%{name}_%{version} \
       -DENABLE_QT5=TRUE \
       -DPLUGIN_UI=CLI \
       -DUSE_EXTERNAL_LIBASS=TRUE \
       -DUSE_EXTERNAL_LIBMAD=TRUE \
       -DUSE_EXTERNAL_LIBA52=TRUE \
       -DUSE_EXTERNAL_TWOLAME=TRUE \
       ../avidemux_plugins
make %{?_smp_mflags}
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd

# Build avidemux_plugins_qt5
rm -rf build_plugins_qt5 && mkdir build_plugins_qt5 && pushd build_plugins_qt5
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DFAKEROOT=%{_pkgbuilddir}/fakeRoot \
       -DAVIDEMUX_SOURCE_DIR=%{_builddir}/%{name}_%{version} \
       -DENABLE_QT5=TRUE \
       -DPLUGIN_UI=QT4 \
       -DUSE_EXTERNAL_LIBASS=TRUE \
       -DUSE_EXTERNAL_LIBMAD=TRUE \
       -DUSE_EXTERNAL_LIBA52=TRUE \
       -DUSE_EXTERNAL_TWOLAME=TRUE \
       ../avidemux_plugins
make %{?_smp_mflags}
make install DESTDIR=%{_pkgbuilddir}/fakeRoot
popd


%install
make -C build_core install DESTDIR=%{buildroot}
make -C build_cli install DESTDIR=%{buildroot}
make -C build_qt5 install DESTDIR=%{buildroot}
make -C build_plugins_common install DESTDIR=%{buildroot}
make -C build_plugins_cli install DESTDIR=%{buildroot}
make -C build_plugins_qt5 install DESTDIR=%{buildroot}

# Remove useless devel files
rm -rf %{buildroot}%{_includedir}/%{name}

# FFMpeg libraries are not being installed as executable.
chmod +x %{buildroot}%{_libdir}/libADM6*.so.*

# Install desktop files
desktop-file-install --vendor rpmfusion \
    --dir %{buildroot}%{_datadir}/applications \
    %{SOURCE1}

# Install icons
install -pDm 0644 avidemux/gtk/ADM_userInterfaces/glade/main/avidemux_icon_small.png \
        %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/avidemux.png
install -pDm 0644 avidemux_icon.png \
	%{buildroot}%{_datadir}/icons/hicolor/64x64/apps/avidemux.png

# Fix library permissions
find %{buildroot}%{_libdir} -type f -name "*.so.*" -exec chmod 0755 {} \;


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post qt
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &> /dev/null || :

%postun qt
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%posttrans qt
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%doc AUTHORS README

%files libs -f build_plugins_common/install_manifest.txt
%license COPYING
%dir %{_datadir}/avidemux6
%{_datadir}/icons/hicolor/*/apps/avidemux.png
%{_libdir}/libADM*
%exclude %{_libdir}/libADM_render*
%exclude %{_libdir}/libADM_UI*
# Catch the stuff missed using install_manifest.txt
%dir %{_libdir}/ADM_plugins6
%dir %{_libdir}/ADM_plugins6/*
%dir %{_libdir}/ADM_plugins6/autoScripts/lib

%files cli -f build_plugins_cli/install_manifest.txt
%{_bindir}/avidemux3_cli
%{_libdir}/libADM_UI_Cli*.so
%{_libdir}/libADM_render6_cli.so

#%files gtk -f build_plugins_gtk/install_manifest.txt
#%{_bindir}/avidemux3_gtk
#%{_libdir}/libADM_UIGtk*.so
#%{_libdir}/libADM_render6_gtk.so
#%{_libdir}/ADM_glade/
#%{_datadir}/applications/rpmfusion-avidemux-gtk.desktop

%files qt 
%{_bindir}/avidemux3_qt5
%{_bindir}/avidemux3_jobs_qt5
%{_libdir}/libADM_openGLQT*.so
%{_libdir}/libADM_UIQT*.so
%{_libdir}/libADM_render6_QT5.so
%{_datadir}/applications/rpmfusion-avidemux-qt.desktop
# QT plugins
%{_libdir}/ADM_plugins6/videoEncoders/qt5/
%{_libdir}/ADM_plugins6/videoFilters/qt5/
%{_libdir}/ADM_plugins6/shaderDemo/

%files i18n
%{_datadir}/avidemux6/qt5/i18n/


%changelog
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
