%{!?version: %define version 1.0.0}
Name:           migasfree-agent
Version:        %{version}
Release:        1%{?dist}
Summary:        Multi-protocol TCP Tunnel Agent

License:        GPLv3
URL:            https://github.com/migasfree/migasfree-agent

Source0:        migasfree-agent
Source1:        migasfree-agent.service

BuildArch:      noarch
Requires:       python3, python3-requests, python3-websockets, migasfree-client

%description
Agent to facilitate remote access via SSH, VNC, RDP through a WebSocket tunnel.

%prep
# No prep needed as we are using direct sources

%build
# No build steps for python script

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system

install -m 755 %{SOURCE0} $RPM_BUILD_ROOT/usr/bin/migasfree-agent
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/lib/systemd/system/migasfree-agent.service

%files
/usr/bin/migasfree-agent
/lib/systemd/system/migasfree-agent.service

%post
%systemd_post migasfree-agent.service

%preun
%systemd_preun migasfree-agent.service

%postun
%systemd_postun_with_restart migasfree-agent.service

%changelog
* Sat Dec 14 2024 Your Name <your.email@example.com> - 1.0.0-1
- Initial package
