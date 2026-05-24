# Migasfree Agent — Product Requirements Document (PRD)

## 1. System Overview

**Migasfree Agent** is the secure remote-access component of the Migasfree Systems Management ecosystem. It enables system administrators to manage and access remote devices (Linux and Windows) securely even when they are behind NATs or strict firewalls. The agent achieves this by establishing a secure, persistent WebSocket connection to a central Relay server and multiplexing local system services (such as SSH, VNC, and RDP) through reverse TCP tunnels.

```mermaid
graph TD
    subgraph Client Machine
        Agent[Migasfree Agent]
        SSH[Local SSH:22]
        VNC[Local VNC:5900]
        RDP[Local RDP:3389]
    end
    subgraph Migasfree Infrastructure
        Manager[Migasfree Manager]
        Relay[Migasfree Relay]
    end
    
    Agent -- 1. mTLS Authentication --> Manager
    Agent -- 2. Get Relay Assignment --> Manager
    Agent -- 3. Secure WebSocket Tunnel --> Relay
    Relay -- 4. Establish Remote Access --> Agent
    Agent -. 5. Local Port Forwarding .-> SSH
    Agent -. 5. Local Port Forwarding .-> VNC
    Agent -. 5. Local Port Forwarding .-> RDP
```

### 1.1 Business Context & Value Proposition

In corporate and public sector fleets, client devices are frequently located behind restrictive networks (NAT, firewalls, custom proxies) making direct inbound administration impossible.

* **Security First (mTLS)**: Every remote connection is strictly authenticated using mutual TLS (mTLS), leveraging the existing certificate infrastructure of `migasfree-client`.
* **Zero Firewall Configuration**: Port forwarding and reverse tunneling eliminate the need to modify client-side router configurations or open inbound ports.
* **Unified Console**: Integrates seamlessly with the Migasfree Manager UI to allow remote command execution and secure terminal/desktop sharing.

---

## 2. Feature & Architecture Inventory

| # | Feature / Component | Description | Doc Link |
|---|---------------------|-------------|----------|
| 1 | **Mutual TLS (mTLS) Authentication** | Secure device identity validation using pre-existing client certificate infrastructure. | [→](./features/01-mtls-authentication.md) |
| 2 | **Relay Registration & Discovery** | Contacting the Manager to register active local services and obtain a secure Relay server assignment. | [→](./features/02-relay-registration.md) |
| 3 | **WebSocket Tunneling Protocol** | Multiplexing TCP connections (SSH, VNC, RDP) into binary WebSocket frames for reverse port forwarding. | [→](./features/03-websocket-tunneling.md) |
| 4 | **Secure Remote Command Execution** | Sandboxed execution of allowed administrator commands with real-time logging and shell-injection protection. | [→](./features/04-remote-execution.md) |

---

## 3. Appendix Reference Index

* **[Relay & Manager API Inventory](./appendix/api-inventory.md)**: Exhaustive list of REST API endpoints and WebSocket message schemas.
* **[Troubleshooting & Privilege Matrix](./appendix/troubleshooting-matrix.md)**: Permissions, environment flags, and platform-specific behaviors (Linux vs. Windows).
