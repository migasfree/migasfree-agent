# Feature 01: Mutual TLS (mTLS) Authentication

> **Path:** `migasfree_agent/agent.py` (via `migasfree_client.mtls`)
> **Type:** System Security Requirements
> **Last Updated:** 2026-05-24

## 1. Overview

The Migasfree Agent must establish an absolute zero-trust channel with the Migasfree Manager and Relay servers. Security is implemented at the transport layer using mutual TLS (mTLS), which guarantees both client identity verification and server authenticity.

> [!IMPORTANT]
> The agent does not generate or manage its own keys. Instead, it relies on the pre-existing client certificate infrastructure created by `migasfree-client` during system enrollment.

---

## 2. Dynamic FQDN & Scheme Parsing

When parsing the system configuration, the agent discovers the target server using the `Server` property in `/etc/migasfree.conf`.

### 2.1 Problem Statement

The `Server` property may be defined as a raw FQDN (`migasfree.es`) or a fully qualified URL containing a scheme (`https://migasfree.es`).

* If a scheme is included, string joining could lead to broken paths (e.g. searching for certificates in `/var/migasfree-client/mtls/https:/migasfree.es/...`).
* It could also cause URL formatting errors like duplicate schemes (`https://https://migasfree.es/...`).

### 2.2 Functional Requirements

1. **Scheme Extraction**: The agent must extract the protocol (`https` or `http`) to correctly construct API endpoints.
2. **Clean Hostname Isolation**: The agent must isolate the clean FQDN (without scheme, port, or path parameters) to locate local mTLS certificates.
3. **Directory Verification**: The certificates are searched dynamically under `/var/migasfree-client/mtls/{fqdn}/` where `{fqdn}` is the isolated hostname.

---

## 3. Python 3.13 Strict SSL Compatibility

To maintain backward compatibility with legacy servers while allowing execution on modern Python interpreters (Python 3.13+), the agent incorporates a compatibility layer.

### 3.1 Strict Verification Bypass

In modern Python releases, default SSL settings enforce strict certificate compliance (`VERIFY_X509_STRICT` and `VERIFY_X509_PARTIAL_CHAIN`). In environments with intermediate CAs or legacy certificates, this causes TLS handshakes to fail.

### 3.2 Technical Implementation

The `StrictSSLCompatAdapter` extends `requests.adapters.HTTPAdapter` to customize the `ssl.SSLContext`:

```python
class StrictSSLCompatAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **kwargs: Any) -> Any:
        context = ssl.create_default_context()
        if hasattr(ssl, 'VERIFY_X509_STRICT'):
            context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        if hasattr(ssl, 'VERIFY_X509_PARTIAL_CHAIN'):
            context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
        kwargs['ssl_context'] = context
        return super().init_poolmanager(connections, maxsize, block=block, **kwargs)
```

---

## 4. Key Security Controls & Mappings

The table below defines the certificate resolution mechanism:

| File Type | Source Function (migasfree-client) | Default Linux Path | Default Windows Path |
|-----------|----------------------------------|--------------------|----------------------|
| **CA Certificate** | `get_mtls_ca_file(server)` | `/var/migasfree-client/mtls/{fqdn}/ca.pem` | `%PROGRAMDATA%/migasfree-client/mtls/{fqdn}/ca.pem` |
| **Client Certificate** | `get_mtls_cert_file(server)` | `/var/migasfree-client/mtls/{fqdn}/cert.pem` | `%PROGRAMDATA%/migasfree-client/mtls/{fqdn}/cert.pem` |
| **Client Private Key** | `get_mtls_key_file(server)` | `/var/migasfree-client/mtls/{fqdn}/key.pem` | `%PROGRAMDATA%/migasfree-client/mtls/{fqdn}/key.pem` |
