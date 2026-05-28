# Architecture: Deep Dive

This document explains the internal design and lifecycle of the Migasfree Agent. It's intended for developers and maintainers who want to understand how the agent bridges network boundaries using WebSocket tunneling.

## 🏗️ High-Level Component Model

The Migasfree Agent is an asynchronous Python application designed to create secure TCP tunnels through persistent WebSocket connections. It operates within a three-tier architecture comprising the **Manager** (for discovery), the **Relay** (for traffic routing), and the **Agent** itself.

### System Context

```mermaid
graph TD
    subgraph "External Control Plane"
        Manager[Migasfree Manager<br/>REST API]
        Relay[Relay Server<br/>WebSocket]
    end

    subgraph "Local Corporate Network"
        subgraph "Endpoint with Agent"
            Agent[Migasfree Agent]
        end
        
        subgraph "Local Services"
            SSH[SSH :22]
            VNC[VNC :5900]
            RDP[RDP :3389]
        end
    end

    Agent -- "1. POST /register (mTLS)" --> Manager
    Manager -- "2. Relay Assignment" --> Agent
    Agent -- "3. WSS Connect (mTLS)" --> Relay
    Relay -- "4. Tunnel Data" --> Agent
    Agent -- "5. TCP Forwarding" --> SSH
    Agent -- "5. TCP Forwarding" --> VNC
    Agent -- "5. TCP Forwarding" --> RDP
```

---

## 🔄 Lifecycle and Flows

### 🎢 Tunnel Establishment Flow

The agent's primary task is to maintain a state machine that transitions from discovery to tunnel operation.

```mermaid
sequenceDiagram
    participant A as Migasfree Agent
    participant M as Manager (REST)
    participant R as Relay (WebSocket)
    participant S as Local Service (SSH/VNC)

    Note over A, S: Phase 1: Registration
    A->>M: POST /register (mTLS)
    M-->>A: 200 OK (relay assignment URL)
    
    Note over A, S: Phase 2: Connection
    A->>R: WSS Connect (mTLS)
    A->>R: JSON type: "register_agent"
    
    Note over A, S: Phase 3: Tunneling
    R->>A: JSON type: "start_tcp_tunnel"
    A->>S: TCP connect (localhost:port)
    A-->>R: JSON type: "tunnel_data" (hex)
    S-->>A: Raw Binary
    A->>R: WebSocket Frames
```

---

## 📊 Data & State Model

### Entity-Relationship: Agent State

The agent maintains several logical entities to track its configuration and active tunnels.

```mermaid
erDiagram
    MultiProtocolAgent ||--o{ TunnelInfo : manages
    MultiProtocolAgent ||--|| SSLConfig : authenticates
    MultiProtocolAgent ||--|| WebSocketPayload : sends
    
    TunnelInfo {
        string tunnel_id
        string service
        int port
        float start_time
    }
    
    SSLConfig {
        string fqdn
        string cert_file
        string key_file
    }
```

---

## 🛡️ Security Posture

### mTLS Integrity

All communication is protected via **Mutual TLS (mTLS)**.

1. The Agent verifies the **Relay's certificate** against the configured CA.
2. The Relay verifies the **Agent's certificate** to ensure it belongs to a managed computer.
3. This creates a cryptographically secure "authenticated tunnel" where both ends of the WebSocket are verified identities.

### Command Execution

Remote commands are severely restricted:

- **Whitelist Enforcement**: The `ALLOWED_COMMANDS` list is the source of truth.
- **Subprocess Safety**: Arguments are never blindly passed to a shell; they are split and executed using standard `asyncio` subprocess utilities.

---

## 🚦 Error Handling & Resilience

### Reconnection Strategy

The agent implements an "infinite retry" loop with exponential backoff logic (simplified to a fixed delay currently) to ensure persistent connectivity.

```mermaid
stateDiagram-v2
    [*] --> Registering
    Registering --> Connecting : Success
    Registering --> Registering : Failure (Wait REC_DELAY)
    
    Connecting --> Operational : WS Open
    Connecting --> Registering : Failure (URL stale)
    
    Operational --> Operational : Handling Tunnels
    Operational --> Registering : WS Close / Error
```

### Connection Health & Heartbeat

To prevent "zombie" online statuses in Redis (e.g., when the agent crashes or experiences network failure without a clean disconnect), a cooperative heartbeat is active:

1. **Short-lived initial registration**: When the agent registers with the Manager, the record has a **120-second TTL**.
2. **Periodic WS Heartbeats**: While connected to the Relay WebSocket, the agent executes a background loop sending `register_agent` frames every **60 seconds**.
3. **Automatic Redis TTL Refresh**: The Relay handles these periodic frames to dynamically update the agent's Redis key TTL to **300 seconds**, maintaining its online status active. If the connection fails, the key naturally expires, ensuring high reliability of the remote access dashboard.

### Resource Cleanup

To prevent memory leaks and "zombie" connections:

- Every tunnel has a timeout for local port checks.
- Binary streams are explicitly closed when `tunnel_managed` messages arrive.
- Signal handlers (SIGTERM) ensure graceful shutdown and notification to the Relay.

### Unregistered Client Behavior

If the local machine is not yet registered with Migasfree:

1. **Missing Certificates**: No client mTLS keys (`cert.pem` and `key.pem`) exist in `/var/migasfree-client/mtls/`.
2. **Missing ID**: The official CLI commands (`migasfree --quiet info id`) fail to return a valid Computer ID (`CID`).

Under these conditions, the agent will throw a `RuntimeError` during startup. When run as a systemd service, this causes the service to exit. Systemd will continuously attempt to restart the agent (according to its restart policy). Once the machine is registered (e.g., after the first `migasfree sync`), the agent automatically recovers, initializes successfully, and connects to the Relay.
