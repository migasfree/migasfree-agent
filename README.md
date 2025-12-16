# Migasfree Agent

A multi-protocol TCP tunnel agent designed to facilitate remote access via SSH, VNC, RDP, and other protocols through a WebSocket tunnel. This agent connects to a Migasfree Manager and establishes secure tunnels for remote management.

## Features

- **Multi-protocol Support**: Handles SSH, VNC, RDP, and generic TCP connections.
- **WebSocket Tunneling**: Uses WebSockets for traversing firewalls and proxies.
- **Secure**: Supports mTLS for secure communication with the Manager and Relay.
- **Lightweight**: Minimal dependencies, primarily Python-based.
- **Cross-Platform**: Supports Linux and Windows.

## Requirements

- Python 3.6+
- `migasfree-client`
- Python libraries: `requests`, `websockets`

## Installation

### Debian/Ubuntu

```bash
sudo dpkg -i migasfree-agent_*.deb
sudo apt-get install -f  # To install dependencies
```

### RPM-based systems

```bash
sudo rpm -ivh migasfree-agent-*.rpm
```

### Windows

#### Prerequisites

1. **Python 3.6+**: Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
2. **migasfree-client**: Must be installed and configured
3. **NSSM** (optional, recommended): Download from [nssm.cc](https://nssm.cc/download) for service management

#### Automatic Installation

Run the installer as Administrator:

```cmd
cd packaging\windows
install.bat
```

#### Manual Installation

1. Install dependencies:

```cmd
pip install requests websockets migasfree-client
```

2. Copy the agent script:

```cmd
mkdir "%PROGRAMDATA%\migasfree-agent"
copy agent\migasfree-agent "%PROGRAMDATA%\migasfree-agent\"
```

3. Create a Windows service using NSSM:

```cmd
nssm install migasfree-agent python "%PROGRAMDATA%\migasfree-agent\migasfree-agent"
nssm set migasfree-agent AppDirectory "%PROGRAMDATA%\migasfree-agent"
nssm set migasfree-agent DisplayName "Migasfree Agent"
nssm set migasfree-agent Start SERVICE_AUTO_START
nssm start migasfree-agent
```

#### Windows Uninstallation

Run the uninstaller as Administrator:

```cmd
cd packaging\windows
uninstall.bat
```

## Build Instructions

To build the packages from source, run the `build.sh` script:

```bash
./build.sh
```

This will generate `.deb` and `.rpm` packages in the `dist/` directory.

## Usage

### Linux (systemd)

```bash
sudo systemctl start migasfree-agent
sudo systemctl enable migasfree-agent
sudo systemctl status migasfree-agent
```

To view the agent logs in real-time:

```bash
sudo journalctl -u migasfree-agent -f
```

### Windows

Using NSSM:

```cmd
nssm start migasfree-agent
nssm stop migasfree-agent
nssm status migasfree-agent
```

Logs are stored in `%PROGRAMDATA%\migasfree-agent\agent.log`.

## Default Services

The agent monitors and tunnels the following services by default:

| Platform | Services                         |
| -------- | -------------------------------- |
| Linux    | SSH (22), VNC (5900), RDP (3389) |
| Windows  | RDP (3389), VNC (5900)           |
