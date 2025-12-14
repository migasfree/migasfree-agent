# Migasfree Agent

A multi-protocol TCP tunnel agent designed to facilitate remote access via SSH, VNC, RDP, and other protocols through a WebSocket tunnel. This agent connects to a Migasfree Manager and establishes secure tunnels for remote management.

## Features

- **Multi-protocol Support**: Handles SSH, VNC, RDP, and generic TCP connections.
- **WebSocket Tunneling**: Uses WebSockets for traversing firewalls and proxies.
- **Secure**: Supports mTLS for secure communication with the Manager and Relay.
- **Lightweight**: Minimal dependencies, primarily Python-based.

## Requirements

- Python 3.8+
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

## Build Instructions

To build the packages from source, run the `build.sh` script:

```bash
./build.sh
```

This will generate `.deb` packages in the `dist/` directory.

## Usage

The agent is managed via systemd:

```bash
sudo systemctl start migasfree-agent
sudo systemctl enable migasfree-agent
sudo systemctl status migasfree-agent
```


To view the agent logs in real-time:

```bash
sudo journalctl -u migasfree-agent -f
```
