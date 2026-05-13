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
# Environment check: Skip if systemd is not active (e.g., during docker build)
if [ ! -d /run/systemd/system ]; then
    systemctl enable migasfree-agent >/dev/null 2>&1 || :
    echo "Container environment detected: skipping"
else
    systemctl daemon-reload >/dev/null 2>&1 || :
    if systemctl is-enabled migasfree-agent >/dev/null 2>&1; then
        systemctl restart migasfree-agent >/dev/null 2>&1 || :
    else
        systemctl start migasfree-agent >/dev/null 2>&1 || :
    fi
fi

%preun
if [ $1 -eq 0 ] && [ -d /run/systemd/system ]; then
    # Package removal, not upgrade
    systemctl stop migasfree-agent >/dev/null 2>&1 || :
    systemctl disable migasfree-agent >/dev/null 2>&1 || :
fi

%postun
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload >/dev/null 2>&1 || :
fi

%changelog
* Sat Dec 14 2024 Your Name <your.email@example.com> - 1.0.0-1
- Initial package
