# AGENTS.md

> **Context for AI Agents working on `migasfree-agent`**
> This file provides the essential context, commands, and conventions for AI agents to work effectively on this project.

## 1. Project Overview

**migasfree-agent** is a multi-protocol TCP tunnel agent designed for secure remote access (SSH, VNC, RDP) via WebSocket tunnels. It uses mTLS for mutual authentication with Migasfree Manager and Relay servers.

- **Language**: Python 3.6+
- **Network Stack**: `asyncio`, `websockets`, `requests`.
- **Security**: mTLS (Mutual TLS) using `migasfree-client` certificate infrastructure.
- **Packaging**: Debian (.deb), RPM (.rpm), and Windows (NSSM service).

## 2. Setup & Commands

Always use a virtual environment (e.g., `.venv`).

- **Install Dependencies**: `pip install -e .[dev]`
- **Run Agent (Local)**: `python agent/migasfree-agent`
- **Build Packages (Linux)**: `./build.sh`
- **Build Package (Windows)**: `build.bat`
- **Lint Code**: `ruff check agent/`
- **Type Check**: `mypy agent/`
- **Format Code**: `ruff format agent/`

## 3. Code Style & Conventions

- **Compatibility**: Code MUST be compatible with **Python 3.6+**. Handle `dataclasses` backport and `asyncio` loop differences carefully.
- **Linter/Formatter**: Ruff is authoritative.
- **Quote Style**: Single quotes (`'`) are preferred.
- **Async Patterns**: Use modern `asyncio` features but maintain fallback for Python 3.6 (e.g., `asyncio.get_event_loop().run_until_complete()` instead of `asyncio.run()`).
- **Dependency Management**: Rely on `migasfree-client` for mTLS configuration and certificate paths.

## 4. Architecture Standards

- **`agent/`**: Contains the main agent script.
  - **Discrepancy Note**: The file `agent/migasfree-agent` is the primary executable. Do not confuse it with the `migasfree_agent` package name used in `pyproject.toml`.
- **`packaging/`**: Contains platform-specific service descriptors and installer scripts.
- **`docs/`**: Architecture and API documentation.

## 5. Available Skills & Specialized Constraints

Apply the following generalist skills when needed:

- **Python Language**: Pythonic patterns, quality, and Python 3.6+ compatibility.
- **Security**: AppSec, mTLS, encryption, and secure subprocess execution.
- **Bash & Scripting**: Build automation and integration scripts.
- **Documentation**: Diátaxis-structured docs.

## 6. Critical Rules

1. **Security (Command Injection)**: NEVER use `asyncio.create_subprocess_shell` with unvalidated user input. ALWAYS use `shlex.split()` and `asyncio.create_subprocess_exec` to prevent shell injection.
2. **mTLS Integrity**: Do not bypass mTLS certificate verification. Always use the CA provided by `migasfree-client`.
3. **Python 3.6 Support**: Maintain strict compatibility for legacy systems managed by Migasfree.
4. **Whitelist Enforcement**: The `ALLOWED_COMMANDS` list must be the only source of truth for remote execution.
5. **No Placeholders**: Avoid hardcoded credentials or mock certificates; use the system's `migasfree.conf` discovery mechanism.
