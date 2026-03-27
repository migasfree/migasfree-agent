# How-To: Development & Testing

Guide for developers who want to modify, test, or audit the Migasfree Agent.

## 🛠️ Environment Setup

1. **Clone and Create Venv**:

    ```bash
    git clone https://github.com/migasfree/migasfree-agent.git
    cd migasfree-agent
    python -m venv .venv
    source .venv/bin/activate
    ```

2. **Install Dev Dependencies**:

    ```bash
    pip install -e ".[dev]"
    ```

---

## 🧪 Validating Changes

### Running Tests

The project uses `pytest` for unit and integration testing.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=migasfree_agent
```

### Static Analysis (Linting)

We enforce strict style and type guidelines using `ruff` and `mypy`.

```bash
# Lint check
ruff check migasfree_agent/

# Type check
mypy migasfree_agent/
```

---

## 🏗️ Build System

### Generating Packages

The `build.sh` script automates the creation of Linux packages.

```bash
./build.sh [VERSION]
```

This generates:

- `dist/migasfree-agent_VERSION_all.deb`
- `dist/migasfree-agent-VERSION-1.noarch.rpm`

---

## 🖋️ Style & Conventions

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these preferences:

- **Max line length**: 120 characters.
- **Quotes**: Single quotes preferred.
- **Async**: Use `async/await` syntax; handle `asyncio.CancelledError`.

### Type Hints & Docstrings

All public functions must include type hints and Google-style docstrings.

```python
def example(param: int) -> str:
    """Example docstring.
    Args:
        param: Description.
    Returns:
        Description.
    """
```

---

## 📝 Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<scope>): <subject>`

| Type | Description |
| :--- | :--- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation updates |
| `style` | Formatting/Style |
| `refactor` | Code refactoring |
| `test` | Adding tests |

---

## 🚀 Pull Request Process

1. **Update branch** with the latest upstream changes.
2. **Run all tests & linters** (`pytest`, `ruff`, `mypy`).
3. **Update documentation** if functionality changed.
4. **Add tests** for new functionality.
5. **Squash and merge** is preferred for clean history.

---

## 🛡️ Security Auditing (Mandatory)

When modifying the tunnel or command execution logic, you MUST:

1. **Audit `asyncio.create_subprocess_exec`**: Do not use `shell=True`. Ensure arguments are sanitized and never passed through a shell interpreter.
2. **Verify mTLS context**: Ensure the systemic CA from `migasfree-client` is used; NEVER bypass certificate verification.
3. **Trace Buffer Sizes**: Monitor `BUFFER_SIZE` impacts on memory during high-load binary transfers.
