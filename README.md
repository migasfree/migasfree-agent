# Migasfree Agent

[![Build Package](https://github.com/migasfree/migasfree-agent/actions/workflows/build.yml/badge.svg)](https://github.com/migasfree/migasfree-agent/actions/workflows/build.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

**Migasfree Agent** is a multi-protocol TCP tunnel agent designed to facilitate secure remote access via SSH, VNC, RDP, and other protocols through WebSocket tunnels. This agent connects to a Migasfree Manager and establishes secure mTLS-authenticated tunnels for remote management of endpoints.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Debian/Ubuntu](#debianubuntu)
  - [RPM-based Systems](#rpm-based-systems)
  - [Windows](#windows)
- [Configuration](#configuration)
- [Usage](#usage)
- [Protocol Reference](#protocol-reference)
- [Building from Source](#building-from-source)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature                        | Description                                                           |
|--------------------------------|-----------------------------------------------------------------------|
| 🔌 **Multi-Protocol Support**  | Handles SSH (22), VNC (5900), RDP (3389), and generic TCP connections |
| 🌐 **WebSocket Tunneling**     | Traverses firewalls and proxies using WebSocket protocol              |
| 🔐 **mTLS Security**           | Mutual TLS authentication for secure Manager and Relay communication  |
| ☀️ **Lightweight**             | Minimal dependencies with pure Python implementation                  |
| 🖥️ **Cross-Platform**          | Full support for Linux (systemd) and Windows (NSSM service)           |
| 🔄 **Auto-Reconnect**          | Automatic reconnection with configurable delays                       |
| 📝 **Remote Execution**        | Secure command execution with whitelist protection                    |

---

## Architecture

The Migasfree Agent operates within a three-tier architecture:

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Migasfree     │────▶│   Relay Server  │◀────│   Migasfree     │
│   Manager       │     │   (WebSocket)   │     │   Agent         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                       │
        │                        │                       │
        ▼                        ▼                       ▼
   Assignment             Tunnel Traffic           Local Services
   & Discovery            mTLS Encrypted          (SSH/VNC/RDP)
```

### Component Overview

| Component        | Responsibility                                              |
|------------------|-------------------------------------------------------------|
| **Manager**      | Assigns agents to relay servers, manages agent registry     |
| **Relay Server** | Routes WebSocket traffic between clients and agents         |
| **Agent**        | Establishes tunnels, forwards local service traffic         |

### Data Flow

1. **Registration**: Agent contacts Manager at `/manager/v1/private/tunnel/register`
2. **Assignment**: Manager responds with assigned Relay server URL
3. **Connection**: Agent establishes WebSocket connection to Relay
4. **Tunneling**: Traffic is forwarded between remote clients and local services

---

## Requirements

### System Requirements

| Platform | Requirement                                           |
|----------|-------------------------------------------------------|
| Python   | 3.6 or higher                                         |
| Linux    | systemd for service management                        |
| Windows  | NSSM (optional, recommended) for service management   |

### Dependencies

| Package            | Version          | Purpose                          |
|--------------------|------------------|----------------------------------|
| `requests`         | ≥2.28.0          | HTTP client for Manager API      |
| `websockets`       | ≥10.0            | WebSocket client for Relay       |
| `migasfree-client` | ≥5.0             | mTLS certificate management      |
| `dataclasses`      | (built-in 3.7+)  | Data structure definitions       |

---

## Installation

### Debian/Ubuntu

```bash
# Install the package
sudo dpkg -i migasfree-agent_*.deb

# Install any missing dependencies
sudo apt-get install -f

# Enable and start the service
sudo systemctl enable migasfree-agent
sudo systemctl start migasfree-agent
```

### RPM-based Systems

```bash
# Install the package
sudo rpm -ivh migasfree-agent-*.rpm

# Enable and start the service
sudo systemctl enable migasfree-agent
sudo systemctl start migasfree-agent
```

### Windows

#### Prerequisites

1. **Python 3.6+**: Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ During installation, check **"Add Python to PATH"**
2. **migasfree-client**: Must be installed and configured
3. **NSSM** (recommended): Download from [nssm.cc](https://nssm.cc/download)

#### Automatic Installation

Run the installer as **Administrator**:

```cmd
cd packaging\windows
install.bat
```

#### Manual Installation

1. **Install Python dependencies:**

   ```cmd
   pip install requests websockets migasfree-client
   ```

2. **Copy the agent script:**

   ```cmd
   mkdir "%PROGRAMDATA%\migasfree-agent"
   copy agent\migasfree-agent "%PROGRAMDATA%\migasfree-agent\"
   ```

3. **Create Windows service using NSSM:**

   ```cmd
   nssm install migasfree-agent python "%PROGRAMDATA%\migasfree-agent\migasfree-agent"
   nssm set migasfree-agent AppDirectory "%PROGRAMDATA%\migasfree-agent"
   nssm set migasfree-agent DisplayName "Migasfree Agent"
   nssm set migasfree-agent Start SERVICE_AUTO_START
   nssm start migasfree-agent
   ```

#### Windows Uninstallation

```cmd
cd packaging\windows
uninstall.bat
```

---

## Configuration

The agent reads its configuration from the **migasfree-client** configuration file and the traits JSON file.

### Configuration Files

| File                                             | Purpose                                   |
|--------------------------------------------------|-------------------------------------------|
| `/etc/migasfree-client/migasfree.conf`           | Server FQDN and client settings (Linux)   |
| `%PROGRAMDATA%\migasfree-client\migasfree.conf`  | Server settings (Windows)                 |
| `events.json`                                    | Agent ID (CID) and project information    |

### Default Services

| Platform | Services Monitored                |
|----------|-----------------------------------|
| Linux    | SSH (22), VNC (5900), RDP (3389)  |
| Windows  | RDP (3389), VNC (5900)            |

### Constants

These values can be modified in the agent source code:

| Constant                         | Default      | Description                            |
|----------------------------------|--------------|----------------------------------------|
| `RECONNECT_DELAY`                | 5 seconds    | Delay between reconnection attempts    |
| `PORT_CHECK_TIMEOUT`             | 0.5 seconds  | Timeout for local port check           |
| `BUFFER_SIZE`                    | 8192 bytes   | TCP read buffer size                   |
| `WEBSOCKET_CONFIG.ping_interval` | 20 seconds   | WebSocket keepalive ping interval      |
| `WEBSOCKET_CONFIG.ping_timeout`  | 60 seconds   | WebSocket ping response timeout        |
| `WEBSOCKET_CONFIG.close_timeout` | 10 seconds   | WebSocket graceful close timeout       |
| `WEBSOCKET_CONFIG.max_size`      | 10 MB        | Maximum WebSocket message size         |

---

## Usage

### Linux (systemd)

```bash
# Start the service
sudo systemctl start migasfree-agent

# Enable on boot
sudo systemctl enable migasfree-agent

# Check status
sudo systemctl status migasfree-agent

# View real-time logs
sudo journalctl -u migasfree-agent -f

# View recent logs
sudo journalctl -u migasfree-agent --since "1 hour ago"
```

### Windows (NSSM)

```cmd
:: Start service
nssm start migasfree-agent

:: Stop service
nssm stop migasfree-agent

:: Check status
nssm status migasfree-agent

:: Restart service
nssm restart migasfree-agent
```

**Log location:** `%PROGRAMDATA%\migasfree-agent\agent.log`

---

## Protocol Reference

### WebSocket Message Types

The agent communicates with the Relay server using JSON messages over WebSocket.

#### Agent to Relay

| Type             | Description                      | Fields                              |
|------------------|----------------------------------|-------------------------------------|
| `register_agent` | Initial registration             | `id`, `name`, `services`, `mode`    |
| `tunnel_data`    | Forwarded service data           | `tunnel_id`, `origin`, `data` (hex) |
| `tunnel_closed`  | Tunnel termination notification  | `tunnel_id`                         |
| `exec_output`    | Command execution output         | `exec_id`, `stream`, `data`         |
| `exec_complete`  | Command execution finished       | `exec_id`, `exit_code`              |
| `exec_error`     | Command execution error          | `exec_id`, `error`                  |

#### Relay to Agent

| Type               | Description                 | Fields                                  |
|--------------------|-----------------------------|-----------------------------------------|
| `start_tcp_tunnel` | Request to open tunnel      | `tunnel_id`, `service`, `client_cn`     |
| `tunnel_data`      | Client data for tunnel      | `tunnel_id`, `data` (hex)               |
| `close_tcp_tunnel` | Request to close tunnel     | `tunnel_id`                             |
| `execute_command`  | Remote command execution    | `command`, `exec_id`, `client_cn`       |

### Manager API

| Endpoint                              | Method | Description                                 |
|---------------------------------------|--------|---------------------------------------------|
| `/manager/v1/private/tunnel/register` | POST   | Register agent and get relay assignment     |

**Request payload:**

```json
{
  "id": "agent-uuid-or-cid",
  "name": "hostname",
  "services": ["ssh", "vnc", "rdp"]
}
```

**Response:**

```json
{
  "relay": "wss://relay.example.com/agent"
}
```

---

## Building from Source

### Linux Packages

Build `.deb` and `.rpm` packages:

```bash
# Make build script executable
chmod +x build.sh

# Build with default version (1.0.0)
./build.sh

# Build with specific version
./build.sh 2.0.0
```

**Output:** Packages are created in the `dist/` directory.

#### Build Requirements (Linux)

- `dpkg-deb` (for .deb packages)
- `rpmbuild` (for .rpm packages, optional)

### Windows Package

Build distributable ZIP package:

```cmd
:: Build with default version
build.bat

:: Build with specific version
build.bat 2.0.0
```

**Output:** `dist\migasfree-agent-VERSION-windows.zip`

### Development Setup

```bash
# Clone the repository
git clone https://github.com/migasfree/migasfree-agent.git
cd migasfree-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux
# or: venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Run linting
ruff check agent/

# Run type checking
mypy agent/
```

---

## Troubleshooting

### Common Issues

#### Agent not starting

```bash
# Check if migasfree-client is configured
cat /etc/migasfree-client/migasfree.conf

# Verify mTLS certificates exist
ls -la /etc/migasfree-client/ssl/

# Check for Python dependency issues
python3 -c "import requests, websockets, migasfree_client"
```

#### Connection failures

| Symptom                          | Possible Cause             | Solution                                 |
|----------------------------------|----------------------------|------------------------------------------|
| "Manager error"                  | Cannot reach Manager       | Verify network/firewall, check URL       |
| "Failed to load CA certificate"  | Missing CA cert            | Ensure migasfree-client is registered    |
| "Failed to load mTLS certificate"| Missing client cert        | Re-register client with server           |
| "WebSocket connection closed"    | Relay server issue         | Check relay server status                |

#### Tunnel not working

```bash
# Verify local service is running
ss -tlnp | grep -E '(22|5900|3389)'

# Check if port is reachable locally
nc -zv 127.0.0.1 22
```

### Debug Logging

For more verbose output, modify the logging level in the agent:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    ...
)
```

---

## Security

### Authentication

- **mTLS (Mutual TLS)**: Both agent and server authenticate using X.509 certificates
- **Certificate Management**: Handled by `migasfree-client` package
- **CA Verification**: All connections verify the server's CA certificate

### Command Execution Security

- **Whitelist Protection**: Only commands in `ALLOWED_COMMANDS` can be executed
- **Default Whitelist**: `['migasfree']`
- **Non-Interactive**: Commands run without TTY to prevent injection

### Network Security

| Layer          | Protection                                               |
|----------------|----------------------------------------------------------|
| Transport      | TLS 1.2+ encryption                                      |
| Authentication | Client certificate verification                          |
| Data           | Hexadecimal encoding for binary data                     |
| Firewall       | WebSocket protocol traverses standard HTTPS ports        |

### Security Best Practices

1. **Keep certificates rotated**: Regularly renew mTLS certificates
2. **Limit whitelist**: Only add necessary commands to `ALLOWED_COMMANDS`
3. **Monitor logs**: Watch for unauthorized connection attempts
4. **Update regularly**: Apply security patches promptly

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run linting: `ruff check agent/`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Document classes and public methods
- Keep line length ≤ 120 characters

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Homepage**: [https://migasfree.org/](https://migasfree.org/)
- **Documentation**: [Fun with Migasfree](https://github.com/migasfree/fun-with-migasfree)
- **Issues**: [GitHub Issues](https://github.com/migasfree/migasfree-agent/issues)
- **Repository**: [GitHub](https://github.com/migasfree/migasfree-agent/)

---

## Authors

- **Alberto Gacías** - *Lead Developer* - [alberto@migasfree.org](mailto:alberto@migasfree.org)
- **Jose Antonio Chavarría** - *Developer* - [jachavar@gmail.com](mailto:jachavar@gmail.com)

---

Made with ❤️ by the Migasfree Team
