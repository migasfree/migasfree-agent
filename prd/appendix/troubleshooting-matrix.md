# Appendix B: Platform-Specific Compatibility & Privilege Matrix

> **Type:** Administration & Operations Guide
> **Last Updated:** 2026-05-24

This reference matrix summarizes operational privileges, platform differences (Linux vs. Windows), and troubleshooting strategies.

---

## 1. Cross-Platform Operational Matrix

The agent runs natively on both Linux distributions and Windows environments, utilizing platform-specific service wrapper and loopback routing mechanisms.

| Operational Aspect | Linux Platform | Windows Platform |
|--------------------|----------------|------------------|
| **Executable/Service** | `systemd` daemon (`migasfree-agent.service`) | NSSM wrapper (`migasfree-agent`) |
| **Default Configuration Path** | `/etc/migasfree.conf` | `%PROGRAMDATA%/wpt/wpt.conf` or dynamic system registry keys |
| **Client SSL Certificate Path** | `/var/migasfree-client/mtls/{server}/` | `%PROGRAMDATA%/migasfree-client/mtls/{server}/` |
| **Default SSH Port Forward** | `22` (routes to `sshd`) | `22` (routes to OpenSSH Server service) |
| **Desktop screen-sharing** | `5900` (VNC server) | `3389` (Remote Desktop / RDP) |
| **System Privileges Required** | `root` user | `Administrator` (elevated command prompt) |

---

## 2. Security Privilege Constraints

Remote terminal command executions (`execute_command`) and local socket tunneling require elevated system privileges:

> [!CAUTION]
> **Privilege Escalation Risk**:
>
> * **Linux**: The agent daemon runs under root privileges to execute commands (like `migasfree` package sync) and bind to local sockets. To prevent security vulnerabilities, any remote executions MUST be strictly whitelisted and audited.
> * **Windows**: The agent service runs under the `LocalSystem` account. Administrative command execution uses standard Windows shell commands and PowerShell under a secure SYSTEM context.

---

## 3. Active Troubleshooting Scenarios

### 3.1 Scenario A: SSL Path Handshake Failure (`https:/migasfree.es` Invalid Path)

* **Symptom**: The agent logs traceback errors when trying to locate certificates or fails to resolve the `/var/migasfree-client/mtls/` folder.
* **Root Cause**: The configured server variable inside `migasfree.conf` contains an explicit protocol prefix (e.g. `Server = https://migasfree.es`), causing path joining to produce an invalid directory with single slashes (like `https:/migasfree.es`).
* **Resolution**: The parsing logic extracted in version `1.0.12` uses `urllib.parse.urlparse` to dynamically clean the hostname and isolate the raw FQDN (`migasfree.es`) for certificate loading. Ensure the agent version is updated to `1.0.12`.

### 3.2 Scenario B: Port Binding Collision (Port 22/5900/3389 Unavailable)

* **Symptom**: The agent logs traceback socket errors when a `tunnel_create` command is received.
* **Root Cause**: The targeted remote port (e.g. 22 for SSH) is not listening locally on the system loopback interface (`127.0.0.1`), or another local process has exclusively bound to the port.
* **Resolution**: Verify that the corresponding local system service (SSH daemon, VNC server, or RDP service) is running and configured to accept local connections.
