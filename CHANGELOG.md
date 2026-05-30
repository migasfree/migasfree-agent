# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-05-30

### Added

- Support for conditional mTLS mode, enabling dynamic fallback to standard TLS when mTLS client certificates/keys are not present on the filesystem.
- Startup warning indicating when the agent runs in standard TLS mode due to missing certificates.

## [1.2.0] - 2026-05-29

### Fixed

- Resolved `'ClientConnection' object has no attribute 'closed'` error in the heartbeat loop when running with `websockets` v14+, which removed the legacy `.closed` attribute.
- Added version-compatible `_ws_is_open()` helper that detects connection state via `.closed` (v10-v13) or `.state == State.OPEN` (v14+), preventing premature disconnection cycles.

## [1.1.0] - 2026-05-28

### Added

- Implemented periodic heartbeat registration (`_heartbeat_loop`) that runs asynchronously every 60 seconds once connected to the Relay.
- Introduced dynamic local service port detection during heartbeats to keep central service availability up-to-date.
- Added a robust unit test suite (`TestAgentHeartbeat`) to verify heartbeat loops, message registration, and task cancellation.

### Changed

- Enhanced connection lifecycle management to safely launch and clean up the background heartbeat task, avoiding resource leaks.

## [1.0.13] - 2026-05-27

### Changed

- Decoupled the agent completely from `migasfree-client` Python packages and modules, eliminating all library-level imports.
- Replaced direct internal config and mTLS path lookups with synchronous CLI execution of `migasfree --quiet conf --json`.
- Dynamically resolved client certificate and key paths (`cert.pem`, `key.pem`) relative to the directory containing the retrieved `ca.pem` (`ca_file`).
- Replaced internal cache traits file parser with synchronous execution of `migasfree --quiet info id` (falling back to `sudo` execution if required) to securely retrieve the local Computer ID (`CID`).

## [1.0.12] - 2026-05-24

### Added

- Added Windows-specific troubleshooting notes regarding execution and privilege management.

### Changed

- Harmonized post-installation scripts for Debian (`.deb`) and RedHat (`.rpm`) packages, improving systemd configuration behavior in containerized environments.

### Fixed

- **Critical**: Resolved an issue where configuring a scheme (like `https://`) in the `Server` parameter caused mTLS CA/certificate lookup paths to point to invalid directories (such as `https:/migasfree.es`) and led to double-scheme API URLs (`https://https://...`). The agent now parses the server URL cleanly using `urllib.parse.urlparse`.
- Explicitly imported `requests.adapters` to satisfy static analysis and updated unit tests to mock the adapters submodule in `sys.modules`.

## [1.0.11] - 2026-05-08

### Added

- Integrated `pre-commit` hooks for Ruff and Mypy.

### Fixed

- Resolved multiple static analysis and type safety warnings, including proper type annotations for `init_poolmanager` and `proxy_manager_for` in `StrictSSLCompatAdapter`.
- Resolved CI deprecation warning by upgrading the mypy target python_version to 3.10.

### Style

- Standardized Ruff formatting for the `init_poolmanager` function signature in `agent.py`.

## [1.0.10] - 2026-04-13

### Fixed

- **Critical**: Refactored SSL context in WebSocket connections to improve mTLS compatibility with HAProxy, forcing TLSv1.2+ and refining certificate verification to prevent handshake failures in zero-trust environments.
- Improved connection resilience by optimizing internal routing handled by the agent during tunnel establishment.

## [1.0.9] - 2026-04-06

### Security

- **Critical**: Improved security in remote command execution by replacing shell execution with strict `asyncio.create_subprocess_exec` and argument sanitization to prevent command injection.

### Added

- Comprehensive automated test suite with unit tests for agent logic and security.
- Major CI/CD pipeline overhaul using GitHub Actions with matrix testing (Python 3.6 - 3.13), linting, and type checking.
- Synchronized build system for Linux and Windows with automatic version extraction from `pyproject.toml`.
- Standardized `.vscode/settings.json` to resolve python interpreter issues across environments.

### Fixed

- Resolved multiple Mypy type-checking errors and improved overall type safety with explicit type guards.
- Fixed CI runner compatibility for legacy Python 3.6 environments.

### Changed

- Comprehensive documentation refactoring following the Diátaxis framework.
- Aligned project internal structure with `pyproject.toml` naming standards.
- Improved build consistency for DEB, RPM, and Windows distributions.

## [1.0.8] - 2026-01-20

### Fixed

- WebSocket connection compatibility and async/await usage improvements.

## [1.0.7] - 2025-12-19

### Added

- Forced color output support for remote command execution.

## [1.0.6] - 2025-12-19

### Added

- Remote command execution support via authenticated tunnels.

## [1.0.5] - 2025-12-18

### Changed

- Refactored agent ID types and simplified registration payload.

## [1.0.4] - 2025-12-16

### Fixed

- Resolved agent crashes and improved Python 3.13 compatibility.

## [1.0.3] - 2025-12-16

### Added

- Windows platform packaging support.
- Added `pyproject.toml` for modern build toolchain.

### Changed

- Adjusted code for strict Python 3.6+ compatibility.

## [1.0.2] - 2025-12-15

### Fixed

- DEB and RPM package build directory structure.
- Refactored mTLS certificate loading logic.

## [1.0.1] - 2025-12-14

### Changed

- Improved logging by removing redundant timestamps.

## [1.0.0] - 2025-12-14

### Added

- Initial release of Migasfree Agent.
- Multi-protocol TCP tunnel support (SSH, VNC, RDP).
- mTLS authentication and WebSocket-based encryption.
- Multi-platform support (Linux and Windows).

---

[1.3.0]: https://github.com/migasfree/migasfree-agent/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/migasfree/migasfree-agent/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/migasfree/migasfree-agent/compare/1.0.13...1.1.0
[1.0.13]: https://github.com/migasfree/migasfree-agent/compare/1.0.12...1.0.13
[1.0.12]: https://github.com/migasfree/migasfree-agent/compare/1.0.11...1.0.12
[1.0.11]: https://github.com/migasfree/migasfree-agent/compare/1.0.10...1.0.11
[1.0.10]: https://github.com/migasfree/migasfree-agent/compare/1.0.9...1.0.10
[1.0.9]: https://github.com/migasfree/migasfree-agent/compare/1.0.8...1.0.9
[1.0.8]: https://github.com/migasfree/migasfree-agent/compare/1.0.7...1.0.8
[1.0.7]: https://github.com/migasfree/migasfree-agent/compare/1.0.6...1.0.7
[1.0.6]: https://github.com/migasfree/migasfree-agent/compare/1.0.5...1.0.6
[1.0.5]: https://github.com/migasfree/migasfree-agent/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/migasfree/migasfree-agent/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/migasfree/migasfree-agent/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/migasfree/migasfree-agent/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/migasfree/migasfree-agent/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/migasfree/migasfree-agent/releases/tag/1.0.0
