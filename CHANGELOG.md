# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/migasfree/migasfree-agent/compare/1.0.9...HEAD
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
