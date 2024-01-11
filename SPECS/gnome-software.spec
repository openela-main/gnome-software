%global glib2_version 2.56.0
%global gtk3_version 3.22.4
%global json_glib_version 1.2.0
%global packagekit_version 1.1.1
%global appstream_glib_version 0.7.14-3
%global libsoup_version 2.52.0
%global gsettings_desktop_schemas_version 3.12.0
%global gnome_desktop_version 3.18.0
%global fwupd_version 1.0.7
%global flatpak_version 0.9.4
%global libxmlb_version 0.1.7

%global fwupd_arches aarch64 ppc64le s390x x86_64

Name:      gnome-software
Version:   3.36.1
Release:   11%{?dist}
Summary:   A software center for GNOME

License:   GPLv2+
URL:       https://wiki.gnome.org/Apps/Software
Source0:   https://download.gnome.org/sources/gnome-software/3.36/%{name}-%{version}.tar.xz

# Add support for basic auth and webflow auth in flatpak plugin
# https://gitlab.gnome.org/GNOME/gnome-software/-/merge_requests/467
Patch0:    0001-Add-basic-auth-support-to-flatpak-plugin.patch
Patch1:    0002-Add-webflow-auth-support-to-flatpak-plugin.patch
# Add back shell extensions support as we don't have the extensions app in RHEL 8.3
# https://bugzilla.redhat.com/show_bug.cgi?id=1839774
Patch2:    add-back-shell-extensions-support.patch
# Fix hardcoded desktop and appdata names to match what's in RHEL 8.3
Patch3:    0001-Fix-hardcoded-desktop-and-appdata-names-to-match-wha.patch
# Fix 'Show Details' to correctly work for rpm-installed firefox
Patch4:    0001-Improve-the-heuristic-for-detecting-old-style-AppStr.patch
# Fix flatpak updates and removals when same ref occurs in multiple remotes
Patch5:    gnome-software-3.36.1-unrelated-refs.patch

Patch6:    be-able-to-disable-odrs.patch
Patch7:    crash-when-run-as-root.patch
Patch8:    gs-updates-page-keep-showing-installing-apps.patch
Patch9:    flatpak-same-runtime-origin.patch
Patch10:   devel-install-headers.patch
Patch11:   0003-hide-some-errors.patch

BuildRequires: gcc
BuildRequires: gettext
BuildRequires: libxslt
BuildRequires: docbook-style-xsl
BuildRequires: desktop-file-utils
%ifarch %{fwupd_arches}
BuildRequires: fwupd-devel >= %{fwupd_version}
%endif
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gnome-desktop3-devel
BuildRequires: gnome-online-accounts-devel
BuildRequires: gsettings-desktop-schemas-devel >= %{gsettings_desktop_schemas_version}
BuildRequires: gspell-devel
BuildRequires: gtk3-devel >= %{gtk3_version}
BuildRequires: gtk-doc
BuildRequires: json-glib-devel >= %{json_glib_version}
BuildRequires: libappstream-glib-devel >= %{appstream_glib_version}
BuildRequires: libsoup-devel
BuildRequires: libxmlb-devel >= %{libxmlb_version}
BuildRequires: meson
BuildRequires: PackageKit-glib-devel >= %{packagekit_version}
BuildRequires: polkit-devel
BuildRequires: flatpak-devel >= %{flatpak_version}
%if 0%{?fedora}
BuildRequires: libdnf-devel
BuildRequires: ostree-devel
BuildRequires: rpm-devel
BuildRequires: rpm-ostree-devel
%endif
BuildRequires: libgudev1-devel
%ifarch %{valgrind_arches}
BuildRequires: valgrind-devel
%endif

Requires: appstream-data
Requires: flatpak%{?_isa} >= %{flatpak_version}
Requires: flatpak-libs%{?_isa} >= %{flatpak_version}
%ifarch %{fwupd_arches}
Requires: fwupd%{?_isa} >= %{fwupd_version}
%endif
Requires: glib2%{?_isa} >= %{glib2_version}
Requires: gnome-desktop3%{?_isa} >= %{gnome_desktop_version}
# gnome-menus is needed for app folder .directory entries
Requires: gnome-menus%{?_isa}
Requires: gsettings-desktop-schemas%{?_isa} >= %{gsettings_desktop_schemas_version}
Requires: gtk3%{?_isa} >= %{gtk3_version}
Requires: json-glib%{?_isa} >= %{json_glib_version}
Requires: iso-codes
Requires: libappstream-glib%{?_isa} >= %{appstream_glib_version}
# librsvg2 is needed for gdk-pixbuf svg loader
Requires: librsvg2%{?_isa}
Requires: libsoup%{?_isa} >= %{libsoup_version}
Requires: PackageKit%{?_isa} >= %{packagekit_version}
Requires: libxmlb%{?_isa} >= %{libxmlb_version}

Obsoletes: gnome-software-editor < 3.35.1

# this is not a library version
%define gs_plugin_version               13

%description
gnome-software is an application that makes it easy to add, remove
and update software in the GNOME desktop.

%package devel
Summary: Headers for building external gnome-software plugins
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
These development files are for building gnome-software plugins outside
the source tree. Most users do not need this subpackage installed.

%prep
%autosetup -p1 -S gendiff

%build
%meson \
    -Dsnap=false \
%ifnarch %{valgrind_arches}
    -Dvalgrind=false \
%endif
%ifnarch %{fwupd_arches}
    -Dfwupd=false \
%endif
    -Dgudev=true \
    -Dpackagekit=true \
    -Dexternal_appstream=false \
    -Dmalcontent=false \
    -Drpm_ostree=false \
    -Dtests=false
%meson_build

%install
%meson_install

# remove unneeded dpkg plugin
rm %{buildroot}%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_dpkg.so

# make the software center load faster
desktop-file-edit %{buildroot}%{_datadir}/applications/org.gnome.Software.desktop \
    --set-key=X-AppInstall-Package --set-value=%{name}

# set up for Fedora
cat >> %{buildroot}%{_datadir}/glib-2.0/schemas/org.gnome.software-fedora.gschema.override << FOE
[org.gnome.software]
official-repos = [ 'rhel-7' ]
FOE

%find_lang %name --with-gnome

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files -f %{name}.lang
%doc AUTHORS README.md
%license COPYING
%{_bindir}/gnome-software
%{_datadir}/applications/gnome-software-local-file.desktop
%{_datadir}/applications/org.gnome.Software.desktop
%dir %{_datadir}/gnome-software
%{_datadir}/gnome-software/*.png
%{_mandir}/man1/gnome-software.1.gz
%{_datadir}/icons/hicolor/*/apps/org.gnome.Software.svg
%{_datadir}/icons/hicolor/symbolic/apps/org.gnome.Software-symbolic.svg
%{_datadir}/icons/hicolor/scalable/status/software-installed-symbolic.svg
%{_datadir}/gnome-software/featured-*.svg
%{_datadir}/gnome-software/featured-*.jpg
%{_datadir}/metainfo/org.gnome.Software.appdata.xml
%{_datadir}/metainfo/org.gnome.Software.Plugin.Flatpak.metainfo.xml
%ifarch %{fwupd_arches}
%{_datadir}/metainfo/org.gnome.Software.Plugin.Fwupd.metainfo.xml
%endif
%{_datadir}/metainfo/org.gnome.Software.Plugin.Odrs.metainfo.xml
%dir %{_libdir}/gs-plugins-%{gs_plugin_version}
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_appstream.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_desktop-categories.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_desktop-menu-path.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_dummy.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_fedora-langpacks.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_fedora-pkgdb-collections.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_flatpak.so
%ifarch %{fwupd_arches}
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_fwupd.so
%endif
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_generic-updates.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_hardcoded-blacklist.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_hardcoded-popular.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_icons.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_key-colors-metadata.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_key-colors.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_modalias.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_odrs.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_os-release.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-history.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-local.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-offline.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-proxy.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-refine-repos.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-refine.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-refresh.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-upgrade.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit-url-to-app.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_packagekit.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_provenance-license.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_provenance.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_repos.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_rewrite-resource.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_shell-extensions.so
%{_libdir}/gs-plugins-%{gs_plugin_version}/libgs_plugin_systemd-updates.so
%{_sysconfdir}/xdg/autostart/gnome-software-service.desktop
%{_datadir}/app-info/xmls/org.gnome.Software.Featured.xml
%{_datadir}/dbus-1/services/org.freedesktop.PackageKit.service
%{_datadir}/dbus-1/services/org.gnome.Software.service
%{_datadir}/gnome-shell/search-providers/org.gnome.Software-search-provider.ini
%{_datadir}/glib-2.0/schemas/org.gnome.software.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnome.software-fedora.gschema.override
%{_libexecdir}/gnome-software-cmd
%{_libexecdir}/gnome-software-restarter

%files devel
%{_libdir}/pkgconfig/gnome-software.pc
%dir %{_includedir}/gnome-software
%{_includedir}/gnome-software/*.h
%{_datadir}/gtk-doc/html/gnome-software

%changelog
* Thu Sep 22 2022 Milan Crha <mcrha@redhat.com> - 3.36.1-11
- Resolves: #2124772 (Hide some errors in non-debug builds)

* Thu Jul 08 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-10
- Resolves: #1978505 (Development package is missing important header files)

* Mon Jun 21 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-9
- Resolves: #1972545 (flatpak: Prefer runtime from the same origin as the application)

* Mon May 24 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-8
- Resolves: #1888404 (Updates page hides ongoing updates on refresh)

* Mon May 24 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-7
- Resolves: #1873297 (Crash when run as root)

* Mon May 24 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-6
- Resolves: #1791478 (Cannot completely disable ODRS (GNOME Ratings))

* Wed Feb 17 2021 Milan Crha <mcrha@redhat.com> - 3.36.1-5
- Fix flatpak updates and removals when same ref occurs in multiple remotes
- Resolves: #1888407

* Thu Jun 11 2020 Kalev Lember <klember@redhat.com> - 3.36.1-4
- Fix 'Show Details' to correctly work for rpm-installed firefox
- Resolves: #1845714

* Wed Jun 03 2020 Kalev Lember <klember@redhat.com> - 3.36.1-3
- Upload correct 3.36.1 tarball
- Fix hardcoded desktop and appdata names to match what's in RHEL 8.3
- Add back shell extensions support
- Resolves: #1839774

* Tue Jun 02 2020 Kalev Lember <klember@redhat.com> - 3.36.1-2
- Add support for basic auth and webflow auth in flatpak plugin
- Resolves: #1815502

* Fri May 22 2020 Richard Hughes <rhughes@redhat.com> - 3.36.1-1
- Update to 3.36.1
- Resolves: #1797932

* Wed Jan 29 2020 Kalev Lember <klember@redhat.com> - 3.30.6-3
- Fix issues with installing Cockpit
- Resolves: #1759913

* Fri Jul 12 2019 Kalev Lember <klember@redhat.com> - 3.30.6-2
- Hide addons that are not available in repos
- Resolves: #1719779

* Tue Dec 18 2018 Kalev Lember <klember@redhat.com> - 3.30.6-1
- Update to 3.30.6

* Fri Aug  3 2018 Florian Weimer <fweimer@redhat.com> - 3.28.2-3
- Honor %%{valgrind_arches}

* Wed Jul 18 2018 Richard Hughes <rhughes@redhat.com> - 3.28.2-2
- Do not build the snapd plugin on RHEL.

* Thu Jul 12 2018 Richard Hughes <rhughes@redhat.com> - 3.28.2-1
- Update to 3.28.2

* Mon Apr 09 2018 Kalev Lember <klember@redhat.com> - 3.28.1-1
- Update to 3.28.1

* Thu Mar 29 2018 Kalev Lember <klember@redhat.com> - 3.28.0-5
- Fix empty OS Updates showing up
- Make rpm-ostree update triggering work

* Thu Mar 15 2018 Kalev Lember <klember@redhat.com> - 3.28.0-4
- Fix opening results from gnome-shell search provider

* Wed Mar 14 2018 Kalev Lember <klember@redhat.com> - 3.28.0-3
- Fix crash on initial run with no network (#1554986)

* Tue Mar 13 2018 Kalev Lember <klember@redhat.com> - 3.28.0-2
- Backport an upstream patch to fix shell extensions app ID

* Mon Mar 12 2018 Kalev Lember <klember@redhat.com> - 3.28.0-1
- Update to 3.28.0

* Sun Mar 11 2018 Kalev Lember <klember@redhat.com> - 3.27.92-3
- Rebuilt for gspell 1.8

* Wed Mar 07 2018 Kalev Lember <klember@redhat.com> - 3.27.92-2
- Move org.gnome.Software.Featured.xml from -editor to main package

* Mon Mar 05 2018 Kalev Lember <klember@redhat.com> - 3.27.92-1
- Update to 3.27.92

* Sun Mar 04 2018 Neal Gompa <ngompa13@gmail.com> - 3.27.90-4
- Drop obsolete snapd-login-service requirement for snap plugin subpackage

* Mon Feb 19 2018 Adam Williamson <awilliam@redhat.com> - 3.27.90-3
- Backport fix for RHBZ #1546893 from upstream git

* Mon Feb 19 2018 Kalev Lember <klember@redhat.com> - 3.27.90-2
- Re-enable rpm-ostree plugin

* Thu Feb 15 2018 Kalev Lember <klember@redhat.com> - 3.27.90-1
- Update to 3.27.90
- Temporarily disable the rpm-ostree plugin

* Tue Feb 13 2018 Björn Esser <besser82@fedoraproject.org> - 3.27.4-4
- Rebuild against newer gnome-desktop3 package

* Thu Feb 08 2018 Kalev Lember <klember@redhat.com> - 3.27.4-3
- Add fedora-workstation-repositories to nonfree-sources schema defaults

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 08 2018 Kalev Lember <klember@redhat.com> - 3.27.4-1
- Update to 3.27.4
- Drop unused --without packagekit option

* Fri Jan 05 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.27.3-2
- Remove obsolete scriptlets

* Sat Dec 16 2017 Kalev Lember <klember@redhat.com> - 3.27.3-1
- Update to 3.27.3

* Mon Nov 13 2017 Kalev Lember <klember@redhat.com> - 3.27.2-1
- Update to 3.27.2

* Thu Nov 09 2017 Kalev Lember <klember@redhat.com> - 3.26.2-1
- Update to 3.26.2
- Re-enable fwupd support

* Tue Oct 31 2017 Kalev Lember <klember@redhat.com> - 3.26.1-5
- Enable the rpm-ostree plugin

* Wed Oct 25 2017 Kalev Lember <klember@redhat.com> - 3.26.1-4
- Fix "too many results returned" error after distro upgrades (#1496489)

* Tue Oct 10 2017 Kalev Lember <klember@redhat.com> - 3.26.1-3
- Backport a flatpakref installation fix

* Mon Oct 09 2017 Richard Hughes <rhughes@redhat.com> - 3.26.1-2
- Disable fwupd support until we get a 3.27.1 tarball

* Sun Oct 08 2017 Kalev Lember <klember@redhat.com> - 3.26.1-1
- Update to 3.26.1

* Mon Sep 11 2017 Kalev Lember <klember@redhat.com> - 3.26.0-1
- Update to 3.26.0

* Sun Aug 27 2017 Kalev Lember <klember@redhat.com> - 3.25.91-1
- Update to 3.25.91

* Tue Aug 15 2017 Kalev Lember <klember@redhat.com> - 3.25.90-1
- Update to 3.25.90

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.25.4-6
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.25.4-5
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.25.4-4
- Rebuilt for RPM soname bump

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.25.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.25.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Kalev Lember <klember@redhat.com> - 3.25.4-1
- Update to 3.25.4

* Tue Jul 18 2017 Kalev Lember <klember@redhat.com> - 3.25.3-6
- Drop a meson workaround now that meson is fixed

* Wed Jun 28 2017 Neal Gompa <ngompa13@gmail.com> - 3.25.3-5
- Actually properly enable snap subpackage after removing conditional

* Wed Jun 28 2017 Neal Gompa <ngompa13@gmail.com> - 3.25.3-4
- Remove unnecessary arch-specific conditional for snap subpackage

* Tue Jun 27 2017 Neal Gompa <ngompa13@gmail.com> - 3.25.3-3
- Ensure snap subpackage is installed if snapd is installed

* Fri Jun 23 2017 Richard Hughes <rhughes@redhat.com> - 3.24.3-2
- Enable the snap subpackage

* Fri Jun 23 2017 Kalev Lember <klember@redhat.com> - 3.25.3-1
- Update to 3.25.3
- Switch to the meson build system
- Add an -editor subpackage with new banner editor

* Mon May 15 2017 Richard Hughes <rhughes@redhat.com> - 3.24.3-1
- Update to 3.23.3
- Fix a common crash when installing flatpakrepo files
- Ensure we show the banner when upgrades are available

* Tue May 09 2017 Kalev Lember <klember@redhat.com> - 3.24.2-1
- Update to 3.24.2

* Tue Apr 25 2017 Adam Williamson <awilliam@redhat.com> - 3.24.1-2
- Backport crasher fix from upstream (RHBZ #1444669 / BGO #781217)

* Tue Apr 11 2017 Kalev Lember <klember@redhat.com> - 3.24.1-1
- Update to 3.24.1

* Tue Mar 21 2017 Kalev Lember <klember@redhat.com> - 3.24.0-1
- Update to 3.24.0

* Thu Mar 16 2017 Kalev Lember <klember@redhat.com> - 3.23.92-1
- Update to 3.23.92

* Mon Feb 27 2017 Richard Hughes <rhughes@redhat.com> - 3.23.91-1
- Update to 3.23.91

* Mon Feb 13 2017 Richard Hughes <rhughes@redhat.com> - 3.23.90-1
- Update to 3.23.90

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.23.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Dec 15 2016 Richard Hughes <rhughes@redhat.com> - 3.23.3-1
- Update to 3.23.3

* Wed Nov 23 2016 Kalev Lember <klember@redhat.com> - 3.23.2-1
- Update to 3.23.2

* Tue Nov 08 2016 Kalev Lember <klember@redhat.com> - 3.22.2-1
- Update to 3.22.2

* Wed Oct 12 2016 Kalev Lember <klember@redhat.com> - 3.22.1-1
- Update to 3.22.1

* Mon Sep 19 2016 Kalev Lember <klember@redhat.com> - 3.22.0-1
- Update to 3.22.0

* Wed Sep 14 2016 Kalev Lember <klember@redhat.com> - 3.21.92-1
- Update to 3.21.92
- Don't set group tags

* Thu Sep 01 2016 Kalev Lember <klember@redhat.com> - 3.21.91-1
- Update to 3.21.91

* Wed Aug 17 2016 Kalev Lember <klember@redhat.com> - 3.21.90-2
- Rebuilt for fixed libappstream-glib headers

* Wed Aug 17 2016 Kalev Lember <klember@redhat.com> - 3.21.90-1
- Update to 3.21.90
- Tighten -devel subpackage dependencies

* Thu Jul 28 2016 Richard Hughes <rhughes@redhat.com> - 3.21.4-2
- Allow building without PackageKit for the atomic workstation.

* Mon Jul 18 2016 Richard Hughes <rhughes@redhat.com> - 3.21.4-1
- Update to 3.21.4

* Thu May 26 2016 Kalev Lember <klember@redhat.com> - 3.21.2-2
- Build with flatpak support

* Mon May 23 2016 Richard Hughes <rhughes@redhat.com> - 3.21.2-1
- Update to 3.21.2

* Tue May 10 2016 Kalev Lember <klember@redhat.com> - 3.21.1-2
- Require PackageKit 1.1.1 for system upgrade support

* Mon Apr 25 2016 Richard Hughes <rhughes@redhat.com> - 3.21.1-1
- Update to 3.21.1

* Mon Apr 25 2016 Richard Hughes <rhughes@redhat.com> - 3.20.2-1
- Update to 3.20.1
- Allow popular and featured apps to match any plugin
- Do not make the ODRS plugin depend on xdg-app
- Fix many of the os-upgrade issues and implement the latest mockups
- Make all the plugins more threadsafe
- Return all update descriptions newer than the installed version
- Show some non-fatal error messages if installing fails
- Use a background PackageKit transaction when downloading upgrades

* Wed Apr 13 2016 Kalev Lember <klember@redhat.com> - 3.20.1-1
- Update to 3.20.1

* Fri Apr 01 2016 Richard Hughes <rhughes@redhat.com> - 3.20.1-2
- Set the list of official sources
- Compile with xdg-app support

* Tue Mar 22 2016 Kalev Lember <klember@redhat.com> - 3.20.0-1
- Update to 3.20.0

* Mon Mar 14 2016 Richard Hughes <rhughes@redhat.com> - 3.19.92-1
- Update to 3.19.92

* Thu Mar 03 2016 Kalev Lember <klember@redhat.com> - 3.19.91-2
- Set minimum required json-glib version

* Mon Feb 29 2016 Richard Hughes <rhughes@redhat.com> - 3.19.91-1
- Update to 3.19.91

* Mon Feb 15 2016 Richard Hughes <rhughes@redhat.com> - 3.19.90-1
- Update to 3.19.90

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 15 2016 Richard Hughes <rhughes@redhat.com> - 3.19.4-1
- Update to 3.19.4

* Thu Dec 03 2015 Kalev Lember <klember@redhat.com> - 3.18.3-2
- Require librsvg2 for the gdk-pixbuf svg loader

* Thu Nov 05 2015 Richard Hughes <rhughes@redhat.com> - 3.18.3-1
- Update to 3.18.3
- Use the correct user agent string when downloading firmware
- Fix a crash in the limba plugin
- Fix installing web applications

* Mon Oct 26 2015 Kalev Lember <klember@redhat.com> - 3.18.2-2
- Fix apps reappearing as installed a few seconds after removal (#1275163)

* Thu Oct 15 2015 Kalev Lember <klember@redhat.com> - 3.18.2-1
- Update to 3.18.2

* Tue Oct 13 2015 Kalev Lember <klember@redhat.com> - 3.18.1-1
- Update to 3.18.1

* Wed Oct 07 2015 Kalev Lember <klember@redhat.com> - 3.18.0-2
- Backport two crasher fixes from upstream

* Mon Sep 21 2015 Kalev Lember <klember@redhat.com> - 3.18.0-1
- Update to 3.18.0

* Tue Sep 15 2015 Kalev Lember <klember@redhat.com> - 3.17.92-2
- Update dependency versions

* Tue Sep 15 2015 Richard Hughes <rhughes@redhat.com> - 3.17.92-1
- Update to 3.17.92

* Thu Sep 10 2015 Richard Hughes <rhughes@redhat.com> - 3.17.91-2
- Fix firmware updates

* Thu Sep 03 2015 Kalev Lember <klember@redhat.com> - 3.17.91-1
- Update to 3.17.91

* Wed Aug 19 2015 Kalev Lember <klember@redhat.com> - 3.17.90-1
- Update to 3.17.90

* Wed Aug 12 2015 Richard Hughes <rhughes@redhat.com> - 3.17.3-1
- Update to 3.17.3

* Wed Jul 22 2015 David King <amigadave@amigadave.com> - 3.17.2-3
- Bump for new gnome-desktop3

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.17.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 05 2015 Kalev Lember <kalevlember@gmail.com> - 3.17.2-1
- Update to 3.17.2

* Mon May 25 2015 Kalev Lember <kalevlember@gmail.com> - 3.17.1-1
- Update to 3.17.1

* Fri May 15 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.2-2
- Fix a crash under Wayland (#1221968)

* Mon May 11 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.2-1
- Update to 3.16.2

* Tue Apr 14 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.1-1
- Update to 3.16.1

* Mon Mar 23 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.0-1
- Update to 3.16.0

* Mon Mar 16 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.92-1
- Update to 3.15.92
- Use license macro for the COPYING file
- Add a patch to adapt to gnome-terminal desktop file rename

* Mon Mar 02 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.91-1
- Update to 3.15.91

* Sat Feb 21 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.90-3
- Export DisplayName property on the packagekit session service

* Thu Feb 19 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.90-2
- Backport a crash fix

* Tue Feb 17 2015 Richard Hughes <rhughes@redhat.com> - 3.15.90-1
- Update to 3.15.90

* Mon Jan 19 2015 Richard Hughes <rhughes@redhat.com> - 3.15.4-1
- Update to 3.15.4

* Tue Nov 25 2014 Kalev Lember <kalevlember@gmail.com> - 3.15.2-1
- Update to 3.15.2

* Thu Nov 13 2014 Richard Hughes <rhughes@redhat.com> - 3.14.2-3
- Fix non-Fedora build

* Tue Nov 11 2014 Richard Hughes <rhughes@redhat.com> - 3.14.2-2
- Backport a patch to fix compilation

* Mon Nov 10 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.2-1
- Update to 3.14.2

* Sat Nov 08 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1-3
- Update the list of system apps

* Sat Nov 01 2014 David King <amigadave@amigadave.com> - 3.14.1-2
- Rebuild for new libappstream-glib (#1156494)

* Mon Oct 13 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1-1
- Update to 3.14.1

* Thu Oct 09 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.0-2
- Depend on gnome-menus for app folder directory entries

* Mon Sep 22 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.0-1
- Update to 3.14.0

* Wed Sep 17 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.92-2
- Set minimum required dependency versions (#1136343)

* Tue Sep 16 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.92-1
- Update to 3.13.92
- Replace gnome-system-log with gnome-logs in the system apps list

* Tue Sep 02 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.91-1
- Update to 3.13.91

* Tue Aug 19 2014 Richard Hughes <rhughes@redhat.com> - 3.13.90-1
- Update to 3.13.90

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.13.5-0.2.git5c89189
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug 11 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.5-0.1.git5c89189
- Update to 3.13.5 git snapshot
- Ship HighContrast icons

* Sun Aug 03 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.4-2
- Replace Epiphany with Firefox in the system apps list

* Wed Jul 23 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.4-1
- Update to 3.13.4

* Wed Jun 25 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.3-1
- Update to 3.13.3

* Thu Jun 12 2014 Richard Hughes <rhughes@redhat.com> - 3.13.3-0.2.git7491627
- Depend on the newly-created appstream-data package and stop shipping
  the metadata here.

* Sat Jun 07 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.3-0.1.git7491627
- Update to 3.13.3 git snapshot

* Wed May 28 2014 Richard Hughes <rhughes@redhat.com> - 3.13.2-2
- Rebuild with new metadata.

* Wed May 28 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.2-1
- Update to 3.13.2

* Thu May 15 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.1-4
- Depend on gsettings-desktop-schemas

* Mon May 12 2014 Richard Hughes <rhughes@redhat.com> - 3.13.1-3
- Update the metadata and use appstream-util to install the metadata.

* Wed May 07 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.1-2
- Drop gnome-icon-theme dependency

* Mon Apr 28 2014 Richard Hughes <rhughes@redhat.com> - 3.13.1-1
- Update to 3.13.1

* Fri Apr 11 2014 Kalev Lember <kalevlember@gmail.com> - 3.12.1-2
- Rebuild with new metadata.

* Fri Apr 11 2014 Richard Hughes <rhughes@redhat.com> - 3.12.1-1
- Update to 3.12.1

* Mon Mar 24 2014 Richard Hughes <rhughes@redhat.com> - 3.12.0-1
- Update to 3.12.0

* Thu Mar 20 2014 Richard Hughes <rhughes@redhat.com> - 3.11.92-1
- Update to 3.11.92

* Tue Mar 18 2014 Richard Hughes <rhughes@redhat.com> - 3.11.91-2
- Rebuild with new metadata.

* Sat Mar 08 2014 Richard Hughes <rhughes@redhat.com> - 3.11.91-1
- Update to 3.11.91

* Tue Feb 18 2014 Richard Hughes <rhughes@redhat.com> - 3.11.90-1
- Update to 3.11.90

* Mon Feb 03 2014 Richard Hughes <rhughes@redhat.com> - 3.11.5-2
- Require epiphany-runtime rather than the full application

* Mon Feb 03 2014 Richard Hughes <rhughes@redhat.com> - 3.11.5-1
- Update to 3.11.5

* Thu Jan 30 2014 Richard Hughes <rhughes@redhat.com> - 3.11.4-3
- Rebuild for libpackagekit-glib soname bump

* Wed Jan 22 2014 Richard Hughes <rhughes@redhat.com> - 3.11.4-2
- Rebuild with metadata that has the correct screenshot url.

* Thu Jan 16 2014 Richard Hughes <rhughes@redhat.com> - 3.11.4-1
- Update to 3.11.4

* Tue Dec 17 2013 Richard Hughes <rhughes@redhat.com> - 3.11.3-1
- Update to 3.11.3

* Tue Nov 19 2013 Richard Hughes <rhughes@redhat.com> - 3.11.2-1
- Update to 3.11.2

* Tue Oct 29 2013 Richard Hughes <rhughes@redhat.com> - 3.11.1-1
- Update to 3.11.1
- Add a gnome shell search provider
- Add a module to submit the user rating to the fedora-tagger web service
- Add support for 'missing' codecs that we know exist but we can't install
- Add support for epiphany web applications
- Handle offline installation sensibly
- Save the user rating if the user clicks the rating stars
- Show a modal error message if install or remove actions failed
- Show a star rating on the application details page
- Show font screenshots
- Show more detailed version numbers when required
- Show screenshots to each application

* Wed Sep 25 2013 Richard Hughes <richard@hughsie.com> 3.10.0-1
- New upstream release.
- New metadata for fedora, updates and updates-testing
- Add a plugin to query the PackageKit prepared-update file directly
- Do not clear the offline-update trigger if rebooting succeeded
- Do not load incompatible projects when parsing AppStream data
- Lots of updated translations
- Show the window right away when starting

* Fri Sep 13 2013 Richard Hughes <richard@hughsie.com> 3.9.3-1
- New upstream release.
- Lots of new and fixed UI and updated metadata for Fedora 20

* Tue Sep 03 2013 Richard Hughes <richard@hughsie.com> 3.9.2-1
- New upstream release.
- Allow stock items in the AppStream XML
- Extract the AppStream URL and description from the XML
- Only present the window when the overview is complete
- Return the subcategories sorted by name

* Mon Sep 02 2013 Richard Hughes <richard@hughsie.com> 3.9.1-1
- New upstream release which is a technical preview for the alpha.

* Sun Sep 01 2013 Richard Hughes <richard@hughsie.com> 0.1-3
- Use buildroot not RPM_BUILD_ROOT
- Own all gnome-software directories
- Drop gtk-update-icon-cache requires and the mime database functionality

* Thu Aug 29 2013 Richard Hughes <richard@hughsie.com> 0.1-2
- Add call to desktop-file-validate and fix other review comments.

* Wed Aug 28 2013 Richard Hughes <richard@hughsie.com> 0.1-1
- First release for Fedora package review

