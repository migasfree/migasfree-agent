# Migasfree Agent Architecture

This document provides an in-depth look at the internal architecture of the Migasfree Agent.

## Overview

The Migasfree Agent is an asynchronous Python application that creates secure TCP tunnels through WebSocket connections. It enables remote access to local services (SSH, VNC, RDP) from a central management console.

## System Context

```text
                                    ┌──────────────────────────────────────┐
                                    │           Migasfree Server           │
                                    │  ┌─────────────┐  ┌───────────────┐  │
                                    │  │   Manager   │  │    Relay      │  │
                                    │  │   Service   │  │   Service     │  │
                                    │  └──────┬──────┘  └───────┬───────┘  │
                                    └─────────┼─────────────────┼──────────┘
                                              │                 │
                                         HTTPS/mTLS        WSS/mTLS
                                              │                 │
┌─────────────────────────────────────────────┼─────────────────┼────────────────┐
│                           Corporate Network │                 │                │
│                                             │                 │                │
│   ┌─────────────────┐                       │                 │                │
│   │   Workstation   │                       │                 │                │
│   │ ┌─────────────┐ │    ┌─────────────────┴─────────────────┴───────────┐    │
│   │ │    SSH      │◀├────┤              Migasfree Agent                  │    │
│   │ │   Port 22   │ │    │  ┌───────────────────────────────────────┐    │    │
│   │ └─────────────┘ │    │  │         MultiProtocolAgent            │    │    │
│   │ ┌─────────────┐ │    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │    │    │
│   │ │    VNC      │◀├────┤  │  │ TCP     │ │ WebSocket│ │ Command │  │    │    │
│   │ │  Port 5900  │ │    │  │  │ Tunnels │ │ Handler  │ │ Executor│  │    │    │
│   │ └─────────────┘ │    │  │  └─────────┘ └─────────┘ └─────────┘  │    │    │
│   │ ┌─────────────┐ │    │  └───────────────────────────────────────┘    │    │
│   │ │    RDP      │◀├────┤                                               │    │
│   │ │  Port 3389  │ │    └───────────────────────────────────────────────┘    │
│   │ └─────────────┘ │                                                          │
│   └─────────────────┘                                                          │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Class Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                      MultiProtocolAgent                          │
├─────────────────────────────────────────────────────────────────┤
│ - manager_url: str                                               │
│ - ssl_config: SSLConfig                                          │
│ - server_url: Optional[str]                                      │
│ - agent_id: str | int                                            │
│ - project: str                                                   │
│ - hostname: str                                                  │
│ - services: Dict[str, int]                                       │
│ - tcp_tunnels: Dict[str, TunnelInfo]                             │
│ - websocket: Optional[WebSocketClientProtocol]                   │
├─────────────────────────────────────────────────────────────────┤
│ + connect() -> None                                              │
│ - _register() -> None                                            │
│ - _fetch_relay_assignment() -> Optional[str]                     │
│ - _handle_messages() -> None                                     │
│ - _handle_tcp_tunnel(tunnel_id, service, client_cn) -> None      │
│ - _forward_service_to_ws(tunnel_id, reader, service) -> None     │
│ - _write_tcp_tunnel(tunnel_id, data_hex) -> None                 │
│ - _close_tcp_tunnel(tunnel_id) -> None                           │
│ - _handle_execute_command(message) -> None                       │
│ - _is_port_open(port) -> bool                                    │
│ - _get_system_info() -> dict                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SSLConfig                                │
├─────────────────────────────────────────────────────────────────┤
│ + fqdn: str                                                      │
│ + key_file: str                                                  │
│ + cert_file: str                                                 │
│ + ca_file: str                                                   │
│ + context: ssl.SSLContext                                        │
├─────────────────────────────────────────────────────────────────┤
│ - _create_context() -> ssl.SSLContext                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         TunnelInfo                               │
├─────────────────────────────────────────────────────────────────┤
│ + reader: asyncio.StreamReader                                   │
│ + writer: asyncio.StreamWriter                                   │
│ + service: str                                                   │
│ + port: int                                                      │
│ + start_time: float                                              │
│ + client_cn: Optional[str]                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Connection Lifecycle

### Phase 1: Initialization

```text
┌────────┐          ┌─────────────┐          ┌──────────────┐
│  Main  │          │   Agent     │          │  SSLConfig   │
└───┬────┘          └──────┬──────┘          └──────┬───────┘
    │                      │                        │
    │ load_agent_config()  │                        │
    │─────────────────────▶│                        │
    │                      │                        │
    │                      │ create(fqdn)           │
    │                      │───────────────────────▶│
    │                      │                        │
    │                      │      SSLConfig         │
    │                      │◀───────────────────────│
    │                      │                        │
    │ create(config)       │                        │
    │─────────────────────▶│                        │
    │                      │                        │
    │ connect()            │                        │
    │─────────────────────▶│                        │
    │                      │                        │
```

### Phase 2: Registration

```text
┌──────────────┐          ┌───────────────┐          ┌──────────────┐
│    Agent     │          │    Manager    │          │    Relay     │
└──────┬───────┘          └───────┬───────┘          └──────┬───────┘
       │                          │                         │
       │ POST /register           │                         │
       │ {id, name, services}     │                         │
       │─────────────────────────▶│                         │
       │                          │                         │
       │      {relay: "wss://..."}│                         │
       │◀─────────────────────────│                         │
       │                          │                         │
       │ WebSocket connect(wss)   │                         │
       │────────────────────────────────────────────────────▶
       │                          │                         │
       │ register_agent message   │                         │
       │────────────────────────────────────────────────────▶
       │                          │                         │
       │        connection ack    │                         │
       │◀────────────────────────────────────────────────────
       │                          │                         │
```

### Phase 3: Tunnel Operation

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Client    │     │    Relay     │     │    Agent     │     │ Local Service│
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │                    │
       │ Request tunnel     │                    │                    │
       │───────────────────▶│                    │                    │
       │                    │ start_tcp_tunnel   │                    │
       │                    │───────────────────▶│                    │
       │                    │                    │                    │
       │                    │                    │ TCP connect        │
       │                    │                    │───────────────────▶│
       │                    │                    │                    │
       │ Data               │                    │                    │
       │───────────────────▶│ tunnel_data        │                    │
       │                    │───────────────────▶│ write              │
       │                    │                    │───────────────────▶│
       │                    │                    │                    │
       │                    │                    │       response     │
       │                    │       tunnel_data  │◀───────────────────│
       │        Data        │◀───────────────────│                    │
       │◀───────────────────│                    │                    │
       │                    │                    │                    │
       │ Close              │                    │                    │
       │───────────────────▶│ close_tcp_tunnel   │                    │
       │                    │───────────────────▶│ close              │
       │                    │                    │───────────────────▶│
       │                    │                    │                    │
```

## Data Flow

### Tunnel Data Encoding

All binary data transmitted through the WebSocket tunnel is encoded as hexadecimal strings:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Data Encoding Flow                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Local Service                Agent                    Relay                 │
│       │                         │                        │                   │
│       │   Binary data           │                        │                   │
│       │   b'\x00\x01\x02'       │                        │                   │
│       │────────────────────────▶│                        │                   │
│       │                         │                        │                   │
│       │                         │   JSON message         │                   │
│       │                         │   {"type": "tunnel_data",                  │
│       │                         │    "data": "000102"}   │                   │
│       │                         │───────────────────────▶│                   │
│       │                         │                        │                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Message Processing Pipeline

```python
# Incoming message handler dispatch
handlers = {
    'start_tcp_tunnel': self._handle_start_tunnel,    # Create new tunnel
    'tunnel_data': self._handle_tunnel_data,           # Forward data to service
    'close_tcp_tunnel': self._handle_close_tunnel,     # Close tunnel
    'execute_command': self._handle_execute_command,   # Run command
}

# Background handlers (non-blocking)
background_handlers = {'execute_command'}
```

## Security Architecture

### Certificate Chain

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Certificate Authority                         │
│                    (ca.pem on server)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Server Cert    │  │   Agent Cert    │  │  Client Cert    │
│  (server.pem)   │  │  (client.pem)   │  │  (client.pem)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### mTLS Handshake

```text
Agent                                          Relay
  │                                              │
  │ ──────────── Client Hello ─────────────────▶│
  │                                              │
  │ ◀─────────── Server Hello ──────────────────│
  │              + Server Certificate           │
  │              + Certificate Request          │
  │                                              │
  │ ──────────── Client Certificate ───────────▶│
  │              + Certificate Verify           │
  │              + Finished                     │
  │                                              │
  │ ◀─────────── Finished ──────────────────────│
  │                                              │
  │ ═══════════ Encrypted Channel ═════════════│
  │                                              │
```

## Error Handling

### Reconnection Strategy

```python
while True:
    try:
        # Attempt connection
        await connect_to_relay()
    except ConnectionError:
        # Reset server URL to force re-registration
        self.server_url = None
        # Wait before retry
        await asyncio.sleep(RECONNECT_DELAY)  # 5 seconds
```

### Tunnel Cleanup

When a tunnel is closed (normally or due to error):

1. Remove from `tcp_tunnels` dictionary
2. Close the StreamWriter
3. Wait for writer to close completely
4. Log duration and client info
5. Send `tunnel_closed` message to Relay

## Performance Considerations

### Buffer Management

| Parameter     | Value | Purpose                     |
|---------------|-------|-----------------------------|
| `BUFFER_SIZE` | 8192  | Optimal TCP read size       |
| `max_size`    | 10MB  | Maximum WebSocket message   |

### Concurrency Model

- **Single WebSocket**: One persistent connection to Relay
- **Multiple Tunnels**: Each tunnel has dedicated asyncio tasks
- **Non-blocking Commands**: Long-running commands execute in background

### Memory Efficiency

- Tunnels stored in dictionary for O(1) lookup
- Binary data hex-encoded (2x size increase acceptable for text protocol)
- No persistent storage of tunnel data

## Testing Considerations

### Unit Test Structure

```text
tests/
├── test_agent.py           # MultiProtocolAgent tests
├── test_ssl_config.py      # SSLConfig tests
├── test_tunnel.py          # Tunnel operations tests
└── conftest.py             # Pytest fixtures
```

### Mock Points

- `requests.post()` - Manager API calls
- `websockets.connect()` - Relay connections
- `asyncio.open_connection()` - Local service connections
- `migasfree_client` - Certificate file paths

## Future Architecture Considerations

### Potential Improvements

1. **Connection Pooling**: Multiple WebSocket connections for high-volume scenarios
2. **Compression**: Optional payload compression for bandwidth optimization
3. **Metrics**: Prometheus-compatible metrics endpoint
4. **Health Checks**: HTTP endpoint for monitoring systems
5. **Plugin System**: Extensible service handlers
