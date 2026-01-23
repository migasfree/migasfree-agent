# Contributing to Migasfree Agent

First off, thank you for considering contributing to Migasfree Agent! It's people like you that make Migasfree Agent such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Process](#development-process)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inclusive environment. By participating, you are expected to uphold this standard. Please report unacceptable behavior to the maintainers.

---

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork locally:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/migasfree-agent.git
   cd migasfree-agent
   ```

3. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

4. **Install development dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

5. **Add upstream remote:**

   ```bash
   git remote add upstream https://github.com/migasfree/migasfree-agent.git
   ```

### Keeping Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues as you might find that the problem has already been reported.

**When reporting a bug, include:**

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details:**
  - OS and version
  - Python version
  - Agent version
  - Migasfree-client version
- **Relevant logs** (with sensitive information redacted)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the proposed functionality
- **Explain why** this enhancement would be useful
- **List any alternatives** you've considered

### 🔧 Contributing Code

1. Look for issues labeled `good first issue` or `help wanted`
2. Comment on the issue to express your interest
3. Follow the development process outlined below

---

## Development Process

### Branching Strategy

- `main` - Stable production code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Creating a Feature Branch

```bash
# Ensure you're on the latest main
git checkout main
git pull upstream main

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent

# Run specific test file
pytest tests/test_agent.py
```

### Running Linters

```bash
# Run Ruff linter
ruff check agent/

# Run with auto-fix
ruff check agent/ --fix

# Run type checker
mypy agent/
```

---

## Style Guidelines

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following specifics:

| Rule                | Value                  |
|---------------------|------------------------|
| Maximum line length | 120 characters         |
| String quotes       | Single quotes preferred|
| Indentation         | 4 spaces               |
| Import order        | isort compatible       |

### Type Hints

All public functions and methods must include type hints:

```python
# Good
def process_message(self, message: dict) -> Optional[str]:
    """Process an incoming message."""
    ...

# Bad
def process_message(self, message):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_timeout(base: int, multiplier: float = 1.0) -> int:
    """Calculate timeout value with optional multiplier.
    
    Args:
        base: Base timeout in seconds.
        multiplier: Optional multiplier for the base value.
    
    Returns:
        Calculated timeout value in seconds.
    
    Raises:
        ValueError: If base is negative.
    """
    ...
```

### Async Code

- Use `async/await` syntax (not `yield from`)
- Prefer `asyncio.create_task()` over `ensure_future()`
- Always handle `asyncio.CancelledError` appropriately

---

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```text
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Types

| Type       | Description                           |
|------------|---------------------------------------|
| `feat`     | New feature                           |
| `fix`      | Bug fix                               |
| `docs`     | Documentation changes                 |
| `style`    | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring                      |
| `perf`     | Performance improvements              |
| `test`     | Adding or modifying tests             |
| `chore`    | Maintenance tasks                     |
| `ci`       | CI/CD changes                         |

### Examples

```text
feat(tunnel): add support for custom port configuration

fix(websocket): handle reconnection on connection timeout

docs(readme): add troubleshooting section

refactor(agent): extract SSL configuration to separate class
```

### Guidelines

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit the subject line to 72 characters
- Reference issues in the footer: `Fixes #123`

---

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest upstream changes
2. **Run all tests** and ensure they pass
3. **Run linters** and fix any issues
4. **Update documentation** if needed
5. **Add tests** for new functionality

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] Code is commented, especially in complex areas
- [ ] Documentation has been updated
- [ ] No new warnings introduced
- [ ] Tests added that prove the fix/feature works
- [ ] All tests pass locally

### PR Description Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran.

## Related Issues
Fixes #(issue number)
```

### Review Process

1. **Automated checks** must pass (CI, linting)
2. At least **one maintainer** must approve
3. All review comments must be **resolved**
4. **Squash and merge** is preferred for clean history

---

## Recognition

Contributors will be recognized in:

- The project's AUTHORS file
- Release notes when their contribution is included
- GitHub's contributor graph

---

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

**Thank you for contributing!** 🎉
