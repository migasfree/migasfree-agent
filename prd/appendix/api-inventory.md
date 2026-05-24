# Appendix A: API & WebSocket Message Inventory

> **Type:** API Reference Specs
> **Last Updated:** 2026-05-24

This reference catalog defines all REST API endpoints and WebSocket messages used during the lifecycle of the Migasfree Agent.

---

## 1. REST API Catalog

### 1.1 `POST /manager/v1/private/tunnel/`

Inbounds to the Migasfree Manager to request a Relay server assignment.

* **Security**: Mutual TLS (mTLS) Required.

#### Query/Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uuid` | String | Yes | Hardware UUID identifying the system. |
| `version` | String | Yes | Agent version (e.g., `1.0.12`). |
| `protocols` | Array[String] | Yes | List of supported tunnel protocols (e.g. `["ssh", "vnc", "rdp"]`). |

#### Response Schema (Success 200 OK)

```json
{
  "status": "success",
  "relay_url": "wss://relay.migasfree.es/ws/tunnel/",
  "token": "sec_auth_token_982348a8cf"
}
```

#### Response Schema (Error 403 Forbidden)

Returned if mTLS validation fails or the computer UUID is blocked/unregistered:

```json
{
  "status": "error",
  "message": "mTLS Certificate validation failed or computer UUID is not authorized."
}
```

---

## 2. WebSocket Action Registry

Once connected to the Relay WebSocket, the following frames are exchanged. All frames must be serialized as JSON strings.

### 2.1 Agent to Relay (Outbound)

#### 2.1.1 `register`

Sent immediately upon opening the WebSocket to authenticate the connection.

```json
{
  "action": "register",
  "token": "sec_auth_token_982348a8cf",
  "uuid": "4a73752e-c5ee-45df-bbdf-5d556c4d7eb8"
}
```

#### 2.1.2 `tunnel_data`

Sends outgoing bytes read from the local TCP service to the Relay.

```json
{
  "action": "tunnel_data",
  "tunnel_id": "c1f7b88e-4a6c-482a-bc96-189fdf2ab765",
  "data": "aGVsYWxvIHdvcmxk"
}
```

#### 2.1.3 `tunnel_close`

Notifies the Relay that a local TCP socket has closed.

```json
{
  "action": "tunnel_close",
  "tunnel_id": "c1f7b88e-4a6c-482a-bc96-189fdf2ab765"
}
```

---

### 2.2 Relay to Agent (Inbound)

#### 2.2.1 `tunnel_create`

Instructs the agent to open a local connection.

```json
{
  "action": "tunnel_create",
  "tunnel_id": "c1f7b88e-4a6c-482a-bc96-189fdf2ab765",
  "protocol": "ssh"
}
```

#### 2.2.2 `tunnel_data`

Passes incoming bytes to write to the local TCP service.

```json
{
  "action": "tunnel_data",
  "tunnel_id": "c1f7b88e-4a6c-482a-bc96-189fdf2ab765",
  "data": "aGVsYWxvIHdvcmxk"
}
```

#### 2.2.3 `execute_command`

Requests execution of a whitelisted administration command.

```json
{
  "action": "execute_command",
  "execution_id": "e2f7b88e-4a6c-482a-bc96-189fdf2ab765",
  "command": "migasfree --sync"
}
```
