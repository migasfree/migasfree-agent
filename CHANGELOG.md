# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (Unreleased)

- Comprehensive documentation refactoring
- CONTRIBUTING.md with development guidelines
- CHANGELOG.md for tracking changes

---

## [1.0.0] - 2024-01-01

### Added (1.0.0)

- Initial release of Migasfree Agent
- Multi-protocol TCP tunnel support (SSH, VNC, RDP)
- WebSocket-based tunneling for firewall traversal
- mTLS authentication for secure communication
- Cross-platform support (Linux and Windows)
- Automatic reconnection with configurable delays
- Remote command execution with whitelist protection
- systemd service integration for Linux
- NSSM service support for Windows
- `.deb` and `.rpm` package build scripts
- Windows ZIP package build script
- GitHub Actions CI/CD workflow

### Security

- Implemented mutual TLS (mTLS) for all connections
- Command execution whitelist to prevent unauthorized commands
- Secure WebSocket (WSS) connections enforced

### Technical Details

- Python 3.6+ compatibility with dataclasses backport
- Async/await architecture using asyncio
- Configurable WebSocket parameters (ping interval, timeouts)
- Hexadecimal encoding for binary tunnel data

---

## Version History Quick Reference

| Version | Date       | Highlights                              |
|---------|------------|-----------------------------------------|
| 1.0.0   | 2024-01-01 | Initial release with full tunnel support|

---

## Upgrade Notes

### Upgrading to 1.0.0

This is the initial release. No upgrade path required.

---

## Links

- [Repository](https://github.com/migasfree/migasfree-agent/)
- [Issues](https://github.com/migasfree/migasfree-agent/issues)
- [Releases](https://github.com/migasfree/migasfree-agent/releases)

[Unreleased]: https://github.com/migasfree/migasfree-agent/compare/1.0.0...HEAD
[1.0.0]: https://github.com/migasfree/migasfree-agent/releases/tag/1.0.0
