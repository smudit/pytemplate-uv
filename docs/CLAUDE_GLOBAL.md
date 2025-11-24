# Global Python Development Guide for LLM Assistants

This guide establishes baseline Python development standards applicable across all projects. LLM assistants should follow these conventions unless project-specific `CLAUDE.md` overrides them.

## Core Python Standards

### Code Style & Formatting

- **PEP 8 Compliance**: Follow PEP 8 with 88-character line limit (Black default)
- **Imports**: Order: stdlib → third-party → local. Use `ruff` for auto-sorting
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private: prefix with `_`

### Type Hints & Documentation

- **Type Hints**: Required for all public functions. Use `from typing import` for complex types
- **Docstrings**: Google-style for all public modules, classes, and functions
- **Return Types**: Always specify, including `-> None` for procedures

```python
def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
    """Calculate total with tax.
    
    Args:
        items: List of item prices.
        tax_rate: Tax rate to apply (default: 0.1).
    
    Returns:
        Total amount including tax.
    """
```

## Development Environment

### Dependency Management (`uv`)

- **Create Environment**: `uv venv`
- **Activate**: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows)
- **Install Dependencies**: `uv sync`
- **Add Package**: `uv add <package>` (adds to `pyproject.toml`)
- **Add Dev Dependency**: `uv add --dev <package>`
- **Run Commands**: Always use `uv run <command>` for consistency

## Quality Assurance

### Linting & Formatting (`ruff`)

- **Check**: `ruff check .`
- **Fix**: `ruff check --fix .`
- **Format**: `ruff format .`
- **Configuration**: Define in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
```

### Testing (`pytest`)

- **Test Discovery**: Files matching `test_*.py` or `*_test.py`
- **Naming**: Test functions must start with `test_`
- **Structure**: Mirror source tree under `tests/`
- **Run Tests**: `pytest` or `uv run pytest`
- **Coverage**: `pytest --cov=src --cov-report=term-missing`
- **Fixtures**: Use `conftest.py` for shared fixtures

### Type Checking

- **Tool**: `mypy` for static type checking
- **Run**: `uv run mypy .`
- **Strict Mode**: Prefer `--strict` for new projects
- **Configuration**: In `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

## Configuration Management (`Dynaconf`)

- **Usage**: Import the `settings` object from the project's `config.py`. Do not create new instances.
- **Files**: Settings are loaded from `settings.yaml`, `.secrets.yaml`, and `.env`.
- **Security**: Never commit secret files (`.secrets.yaml`, `.env`) to version control.

## Key Libraries

- **Paths**: Use `pathlib` for all filesystem path manipulation.
- **CLI**: Use `typer` for building command-line interfaces.
- **Logging**: Use `loguru` for all application logging. Use appropriate log levels (trace, debug, info, success, warning, error, critical)

## Logging

- **Implementation**: Use `loguru` for comprehensive logging
- **Message Quality**: Ensure clear, debuggable log messages with proper context
- **Log Levels**: Use appropriate levels (trace, debug, info, success, warning, error, critical)
- **Error Tracking**: Use `@logger.catch` for robust error tracking

## Version Control

### Git Practices

- **`.gitignore`**: Must include:
  - `.env`, `.secrets*`
  - `__pycache__/`, `*.pyc`
  - `.venv/`, `venv/`
  - `.mypy_cache/`, `.ruff_cache/`
  - `dist/`, `*.egg-info/`

### Commit Messages

- **Format**: `<type>: <description>` (e.g., `fix: resolve import error`)
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **Body**: Add details for complex changes

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
```

## LLM Assistant Guidelines

### How to Use This Guide

1. **Read project-specific `CLAUDE.md` first** - it overrides these defaults
2. **Check for Makefile or scripts** - projects may have custom commands
3. **Verify tool versions** - check `pyproject.toml` for specific versions
4. **Run quality checks** - always lint/format/test after changes

### Common Tasks

- **Before making changes**: Read existing code style in the file
- **After writing code**: Run `ruff format` then `ruff check --fix`
- **Before completing task**: Run tests and type checking
- **When creating files**: Follow project structure conventions

### Key Principles

- **Consistency**: Match existing project patterns
- **Safety**: Never commit secrets or credentials
- **Quality**: All code must pass linting, formatting, and tests
- **Documentation**: Update docstrings and comments when changing functionality

## Security Considerations

- **Never hardcode**: API keys, passwords, tokens, or sensitive data
- **Use environment variables**: For all configuration that varies by environment
- **Validate inputs**: Especially for web applications and CLIs
- **Log safely**: Never log sensitive information

---
*This is a living document. Project-specific `CLAUDE.md` files override these defaults.*
