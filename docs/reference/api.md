# Reference: Python API & Protocol

Detailed technical reference for the Migasfree Agent's internal APIs and WebSocket communication protocol.

## 🐍 Python Logic (Agent Core)

### MultiProtocolAgent

The central class managing connections and tunnels.

#### Initialization

```python
class MultiProtocolAgent:
    def __init__(self, manager_url: str, ssl_config: SSLConfig, agent_id: Optional[int] = None, services: Optional[Dict[str, int]] = None):
        """Initialize the agent with discovery URL and security context."""
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `manager_url` | `str` | Yes | Migasfree Manager discovery URL |
| `ssl_config` | `SSLConfig` | Yes | Security context (mTLS certs) |
| `agent_id` | `int` | No | Unique CID (system identifier) |
| `services` | `dict` | No | Map of service names to TCP ports |

#### Key Methods

| Method | Return Type | Description |
| :--- | :--- | :--- |
| `connect()` | `None` | Starts the main connection loop, manages the WebSocket handshake, registers the agent, and launches the heartbeat task. |
| `_heartbeat_loop()` | `None` | Asynchronous loop running in background while connected. Re-sends `register_agent` frames every 60 seconds to maintain the connection status in Redis and dynamically update service availability. |

---

### Data Models (Internal State)

The agent uses several dataclasses (with backports where necessary for Python 3.6 compatibility) to track state.

#### `TunnelInfo`

Information for an active, persistent TCP-to-WebSocket bridge.

```python
@dataclass
class TunnelInfo:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    service: str
    port: int
    start_time: float
    client_cn: Optional[str] = None
```

#### `SSLConfig`

Security context and mTLS credential management.

```python
@dataclass
class SSLConfig:
    fqdn: str
    key_file: str
    cert_file: str
    ca_file: str
    context: ssl.SSLContext
```

---

## 🌐 WebSocket Protocol Reference

All messages are JSON-encoded strings. Binary traffic is hex-encoded for compatibility with standard text-based WebSocket relays.

### Agent -> Relay (Outgoing)

Messages the agent sends to announce itself and forward traffic.

| Type | Description | Mandatory Fields |
| :--- | :--- | :--- |
| `register_agent` | Hello message | `id`, `name`, `services`, `mode` |
| `tunnel_data` | Forwarded binary data | `tunnel_id`, `data` (hex) |
| `tunnel_closed` | Bridge was terminated | `tunnel_id` |
| `exec_output` | CLI stdout/stderr | `exec_id`, `stream`, `data` |
| `exec_complete` | Process finished | `exec_id`, `exit_code` |

### Relay -> Agent (Incoming)

Commands and traffic arriving from the controller.

| Type | Description | Resulting Action |
| :--- | :--- | :--- |
| `start_tcp_tunnel` | Controller request | Bridge to local TCP port |
| `tunnel_data` | Controller traffic | Write to local TCP socket |
| `close_tcp_tunnel` | Controller disconnect | Close TCP socket & cleanup |
| `execute_command` | Remote CLI request | Execute after whitelist check |

---

## 📍 Network Endpoints

### Manager API

The "discovery" endpoint that assigns agents to relays.

- **URL**: `/manager/v1/private/tunnel/register`
- **Method**: `POST`
- **Auth**: mTLS (Client Certificate)

---

## ⚙️ Static Configuration (Constants)

The following constants govern the agent's behavior:

| Constant | Default | Description |
| :--- | :--- | :--- |
| `RECONNECT_DELAY` | 5s | Interval between retries |
| `PORT_CHECK_TIMEOUT` | 0.5s | Timeout to check local port status |
| `BUFFER_SIZE` | 8192 | Size of TCP read buffer |
| `ALLOWED_COMMANDS` | `['migasfree']` | Whitelist for remote execution |
| `PING_INTERVAL` | 20s | WebSocket keepalive ping |
