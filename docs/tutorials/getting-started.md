# Tutorial: Getting Started with Migasfree Agent

Welcome! This tutorial guides you through your first steps with the Migasfree Agent. By the end of this tutorial, you'll have an agent installed and configured to create secure tunnels on your system.

## 🎯 Our Goal

We'll set up a local agent that connects to a **Migasfree Manager** and makes its **SSH service** accessible via a remote **Relay**.

---

## 🛠️ Prerequisites

Before we begin, ensure you have:

1. **Python 3.6** or higher.
2. The **migasfree-client** package installed and registered.
3. A **Migasfree Manager** URL.

---

## 🚀 Step 1: Install the Agent

For this guide, we'll use a standard Debian package installation.

```bash
# Install the latest agent package
sudo dpkg -i migasfree-agent_latest_all.deb
```

## 🚀 Step 2: Verify Registration

The agent will automatically attempt to register itself with the manager.

1. **Check the logs**:

    ```bash
    sudo journalctl -u migasfree-agent -f
    ```

2. **Look for successful registration**:

    ```text
    INFO  [migasfree-agent] Successfully registered with manager
    INFO  [migasfree-agent] Relay assignment: wss://relay.example.com/agent
    INFO  [migasfree-agent] WebSocket connection established
    ```

## 🚀 Step 3: Test a Remote Tunnel

Once the agent is "Green" (Connected) in the Migasfree Manager dashboard:

1. **Initiate an SSH session** from the manager dashboard.
2. **Check the agent logs** again. You should see the tunnel creation:

    ```text
    INFO  [migasfree-agent] Starting TCP tunnel for service: ssh
    INFO  [migasfree-agent] Local connection to 127.0.0.1:22 established
    ```

---

## 🏁 Summary

Congratulations! You've successfully:

1. **Installed** the Migasfree Agent.
2. **Verified** its automatic mTLS-based registration.
3. **Witnessed** a live tunnel creation.

---

## 📖 Next Steps

- Learn about **[Architecture](../explanation/architecture.md)** to understand how the tunnels work.
- Consult the **[API Reference](../reference/api.md)** for protocol details.
- Discover **[Configuration options](../how-to/how-to.md)** for advanced environments.
