# API Reference

This document provides a complete reference for the Migasfree Agent's internal APIs and WebSocket protocol.

## Table of Contents

- [Python API](#python-api)
  - [MultiProtocolAgent](#multiprotocolagent)
  - [SSLConfig](#sslconfig)
  - [TunnelInfo](#tunnelinfo)
- [WebSocket Protocol](#websocket-protocol)
  - [Agent Messages](#agent-to-relay-messages)
  - [Relay Messages](#relay-to-agent-messages)
- [Manager HTTP API](#manager-http-api)
- [Constants](#constants)

---

## Python API

### MultiProtocolAgent

The main class that manages WebSocket connections and TCP tunnels.

```python
class MultiProtocolAgent:
    def __init__(
        self,
        manager_url: str,
        ssl_config: SSLConfig,
        agent_id: Optional[int] = None,
        project: Optional[str] = None,
        services: Optional[Dict[str, int]] = None,
    ):
        """Initialize the agent.
        
        Args:
            manager_url: Base URL of the Migasfree Manager
            ssl_config: SSL/mTLS configuration
            agent_id: Unique agent identifier (CID)
            project: Project name
            services: Dict mapping service names to ports
        """
```

#### Public Methods

##### `connect() -> None`

Main connection loop with automatic reconnection.

```python
async def connect(self) -> None:
    """Main connection loop with automatic reconnection.
    
    This method runs indefinitely, handling:
    - Initial relay assignment from Manager
    - WebSocket connection to Relay
    - Message processing
    - Automatic reconnection on disconnection
    
    Raises:
        Never raises - catches all exceptions and reconnects
    """
```

**Example:**

```python
agent = MultiProtocolAgent(
    manager_url="https://server.example.com/manager/v1/private/tunnel",
    ssl_config=ssl_config,
    agent_id=12345,
    project="MyProject",
)
await agent.connect()
```

---

### SSLConfig

Dataclass for SSL/mTLS configuration.

```python
@dataclass
class SSLConfig:
    """SSL/mTLS configuration.
    
    Attributes:
        fqdn: Fully qualified domain name of the server
        key_file: Path to client private key (auto-set)
        cert_file: Path to client certificate (auto-set)
        ca_file: Path to CA certificate (auto-set)
        context: Configured SSL context (auto-set)
    """
    fqdn: str
    key_file: str = field(init=False)
    cert_file: str = field(init=False)
    ca_file: str = field(init=False)
    context: ssl.SSLContext = field(init=False)
```

**Example:**

```python
ssl_config = SSLConfig(fqdn="server.example.com")
# Automatically loads:
# - /etc/migasfree-client/ssl/server.example.com/client.key
# - /etc/migasfree-client/ssl/server.example.com/client.crt
# - /etc/migasfree-client/ssl/server.example.com/ca.crt
```

---

### TunnelInfo

Dataclass storing information about an active tunnel.

```python
@dataclass
class TunnelInfo:
    """Stores information about an active tunnel.
    
    Attributes:
        reader: Async stream reader for local connection
        writer: Async stream writer for local connection
        service: Service name (ssh, vnc, rdp, exec)
        port: Local port number
        start_time: Unix timestamp when tunnel was created
        client_cn: Common Name from client certificate
    """
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    service: str
    port: int
    start_time: float
    client_cn: Optional[str] = None
```

---

## WebSocket Protocol

All messages are JSON-encoded strings sent over WebSocket.

### Agent to Relay Messages

#### `register_agent`

Sent immediately after WebSocket connection is established.

```json
{
    "type": "register_agent",
    "id": "12345",
    "name": "workstation [CID-12345]",
    "services": ["ssh", "vnc", "rdp"],
    "mode": "tcp_tunnel"
}
```

| Field      | Type       | Description                       |
|------------|------------|-----------------------------------|
| `type`     | string     | Always `"register_agent"`         |
| `id`       | string/int | Agent's unique identifier (CID)   |
| `name`     | string     | Human-readable agent name         |
| `services` | string[]   | List of available local services  |
| `mode`     | string     | Always `"tcp_tunnel"`             |

---

#### `tunnel_data` (Agent to Relay)

Forwards data from local service to remote client.

```json
{
    "type": "tunnel_data",
    "tunnel_id": "abc123-def456",
    "origin": "agent",
    "data": "1b5b313b33326d"
}
```

| Field       | Type   | Description                |
|-------------|--------|----------------------------|
| `type`      | string | Always `"tunnel_data"`     |
| `tunnel_id` | string | Unique tunnel identifier   |
| `origin`    | string | Always `"agent"`           |
| `data`      | string | Hex-encoded binary data    |

---

#### `tunnel_closed`

Notifies that a tunnel has been closed by the agent.

```json
{
    "type": "tunnel_closed",
    "tunnel_id": "abc123-def456"
}
```

| Field       | Type   | Description                |
|-------------|--------|----------------------------|
| `type`      | string | Always `"tunnel_closed"`   |
| `tunnel_id` | string | Unique tunnel identifier   |

---

#### `exec_output`

Streams command execution output in real-time.

```json
{
    "type": "exec_output",
    "exec_id": "exec-789xyz",
    "stream": "stdout",
    "data": "Processing...\n"
}
```

| Field     | Type   | Description                    |
|-----------|--------|--------------------------------|
| `type`    | string | Always `"exec_output"`         |
| `exec_id` | string | Execution request identifier   |
| `stream`  | string | `"stdout"` or `"stderr"`       |
| `data`    | string | Output line (UTF-8 decoded)    |

---

#### `exec_complete`

Indicates command execution has finished.

```json
{
    "type": "exec_complete",
    "exec_id": "exec-789xyz",
    "exit_code": 0
}
```

| Field       | Type   | Description                    |
|-------------|--------|--------------------------------|
| `type`      | string | Always `"exec_complete"`       |
| `exec_id`   | string | Execution request identifier   |
| `exit_code` | int    | Process exit code              |

---

#### `exec_error`

Reports an error during command execution.

```json
{
    "type": "exec_error",
    "exec_id": "exec-789xyz",
    "error": "Command \"rm\" not allowed. Allowed: migasfree"
}
```

| Field     | Type   | Description                    |
|-----------|--------|--------------------------------|
| `type`    | string | Always `"exec_error"`          |
| `exec_id` | string | Execution request identifier   |
| `error`   | string | Error message                  |

---

### Relay to Agent Messages

#### `start_tcp_tunnel`

Requests the agent to open a tunnel to a local service.

```json
{
    "type": "start_tcp_tunnel",
    "tunnel_id": "abc123-def456",
    "service": "ssh",
    "client_cn": "admin@example.com"
}
```

| Field       | Type   | Description                                  |
|-------------|--------|----------------------------------------------|
| `type`      | string | Always `"start_tcp_tunnel"`                  |
| `tunnel_id` | string | Unique tunnel identifier                     |
| `service`   | string | Service name: `ssh`, `vnc`, `rdp`, `exec`    |
| `client_cn` | string | Client's certificate Common Name             |

---

#### `tunnel_data` (Relay to Agent)

Forwards data from remote client to local service.

```json
{
    "type": "tunnel_data",
    "tunnel_id": "abc123-def456",
    "data": "5353482d322e30"
}
```

| Field       | Type   | Description                |
|-------------|--------|----------------------------|
| `type`      | string | Always `"tunnel_data"`     |
| `tunnel_id` | string | Unique tunnel identifier   |
| `data`      | string | Hex-encoded binary data    |

---

#### `close_tcp_tunnel`

Requests the agent to close a tunnel.

```json
{
    "type": "close_tcp_tunnel",
    "tunnel_id": "abc123-def456"
}
```

| Field       | Type   | Description                  |
|-------------|--------|------------------------------|
| `type`      | string | Always `"close_tcp_tunnel"`  |
| `tunnel_id` | string | Unique tunnel identifier     |

---

#### `execute_command`

Requests remote command execution.

```json
{
    "type": "execute_command",
    "command": "migasfree sync",
    "exec_id": "exec-789xyz",
    "client_cn": "admin@example.com"
}
```

| Field       | Type   | Description                           |
|-------------|--------|---------------------------------------|
| `type`      | string | Always `"execute_command"`            |
| `command`   | string | Full command line to execute          |
| `exec_id`   | string | Unique execution identifier           |
| `client_cn` | string | Requesting client's certificate CN    |

**Security Note:** Only commands whose base command is in `ALLOWED_COMMANDS` will be executed.

---

## Manager HTTP API

### POST `/manager/v1/private/tunnel/register`

Registers the agent and receives relay server assignment.

**Request:**

```http
POST /manager/v1/private/tunnel/register HTTP/1.1
Host: server.example.com
Content-Type: application/json

{
    "id": 12345,
    "name": "workstation",
    "services": ["ssh", "vnc", "rdp"]
}
```

**Headers:**

- Uses mTLS client certificate for authentication

**Response:**

```json
{
    "relay": "wss://relay.example.com/agent"
}
```

| Field   | Type   | Description                          |
|---------|--------|--------------------------------------|
| `relay` | string | WebSocket URL for relay connection   |

**Error Responses:**

| Status | Description                        |
|--------|------------------------------------|
| 401    | Invalid/missing client certificate |
| 403    | Agent not authorized               |
| 503    | No relay servers available         |

---

## Constants

### Default Services

```python
DEFAULT_SERVICES = {
    'ssh': 22,
    'vnc': 5900,
    'rdp': 3389,
    'exec': 0,  # exec doesn't need a port
}
```

### Allowed Commands

```python
ALLOWED_COMMANDS = ['migasfree']
```

### Timing Constants

| Constant             | Value | Description                          |
|----------------------|-------|--------------------------------------|
| `RECONNECT_DELAY`    | 5     | Seconds between reconnection attempts|
| `PORT_CHECK_TIMEOUT` | 0.5   | Seconds for port availability check  |

### Buffer Sizes

| Constant      | Value | Description                    |
|---------------|-------|--------------------------------|
| `BUFFER_SIZE` | 8192  | TCP read buffer size in bytes  |

### WebSocket Configuration

```python
WEBSOCKET_CONFIG = {
    'ping_interval': 20,    # Seconds between pings
    'ping_timeout': 60,     # Seconds to wait for pong
    'close_timeout': 10,    # Seconds for graceful close
    'max_size': 10**7,      # Maximum message size (10 MB)
}
```

---

## Usage Examples

### Creating a Custom Agent

```python
import asyncio
from my_agent import MultiProtocolAgent, SSLConfig

async def main():
    # Configure SSL
    ssl_config = SSLConfig(fqdn="server.migasfree.org")
    
    # Create agent with custom services
    agent = MultiProtocolAgent(
        manager_url="https://server.migasfree.org/manager/v1/private/tunnel",
        ssl_config=ssl_config,
        agent_id=12345,
        project="Production",
        services={
            'ssh': 22,
            'vnc': 5900,
            'rdp': 3389,
            'custom_service': 8080,
        }
    )
    
    # Start the agent
    await agent.connect()

if __name__ == '__main__':
    asyncio.run(main())
```

### Monitoring Active Tunnels

```python
# Inside MultiProtocolAgent
def get_active_tunnels(self) -> list:
    """Get information about active tunnels."""
    return [
        {
            'id': tunnel_id,
            'service': info.service,
            'port': info.port,
            'duration': time.time() - info.start_time,
            'client': info.client_cn,
        }
        for tunnel_id, info in self.tcp_tunnels.items()
    ]
```
