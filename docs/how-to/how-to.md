# How-To Guides: Support & Deployment

Practical guides for deploying the Migasfree Agent across different platforms and environments.

## 🛠️ Deploying the Agent

### Linux (Systemd)

1. **Install the package**:

   ```bash
   sudo dpkg -i migasfree-agent_*.deb   # Debian/Ubuntu
   sudo rpm -ivh migasfree-agent-*.rpm  # RHEL/Fedora
   ```

2. **Enable and start the service**:

   ```bash
   sudo systemctl enable migasfree-agent
   sudo systemctl start migasfree-agent
   ```

3. **Verify the status**:

   ```bash
   sudo systemctl status migasfree-agent
   sudo journalctl -u migasfree-agent -f
   ```

### Windows (NSSM Service)

The agent on Windows is typically managed using the **Non-Sucking Service Manager (NSSM)** for maximum reliability.

#### Automatic Install

Run the provided installer as **Administrator**:

```cmd
cd packaging\windows
install.bat
```

#### Manual Configuration

If you prefer manual setup:

1. **Copy the agent script**:

    ```cmd
    mkdir "%PROGRAMDATA%\migasfree-agent"
    copy migasfree_agent\agent.py "%PROGRAMDATA%\migasfree-agent\migasfree-agent"
    ```

2. **Configure NSSM**:

    ```cmd
    nssm install migasfree-agent python "%PROGRAMDATA%\migasfree-agent\migasfree-agent"
    nssm set migasfree-agent AppDirectory "%PROGRAMDATA%\migasfree-agent"
    nssm set migasfree-agent DisplayName "Migasfree Agent"
    nssm start migasfree-agent
    ```

---

## 🔧 Configuring the Agent

The agent is designed to be **Zero-Config** for most environments, inheriting its settings from the `migasfree-client` ecosystem.

### Centralized Configuration

- **Linux**: `/etc/migasfree-client/migasfree.conf`
- **Windows**: `%PROGRAMDATA%\migasfree-client\migasfree.conf`

The agent automatically discovers:

- The **Manager Server URL**.
- **mTLS certificates** (Client cert, Private key, and CA).
- The **Computer ID (CID)**.

---

## 🏗️ Building from Source

### Building Linux Packages (.deb / .rpm)

Requires `dpkg-deb` and `rpmbuild`.

```bash
chmod +x build.sh
./build.sh 1.2.0  # Optional: specify version
```

The resulting packages will be in the `dist/` directory.

### Building Windows Bundle (.zip)

Run on a Windows machine with Python installed:

```cmd
build.bat 1.2.0
```

---

## 🔬 Troubleshooting common issues

| Issue | Check | Solution |
| :--- | :--- | :--- |
| **"Manager error: 401"** | Client certs | Check if `migasfree-client` is registered. |
| **"No relay assigned"** | Manager server | Verify the Manager has available Relays. |
| **"VNC port closed"** | Local service | Ensure `vnc-server` is running on :5900. |
| **"Python 3.6 error"** | Dependencies | Ensure `dataclasses` backport is installed. |
