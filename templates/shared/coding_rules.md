
## 1. Dependency Management (`uv`)
- **Environment**: `uv venv` to create, then `source .venv/bin/activate`.
- **Packages**: `uv sync` to install from `pyproject.toml`. `uv add <package>` to add a new dependency.

## 2. Core Commands
You MUST use `uv run` to run any commands. 
- **Lint & Fix**: `make lint`
- **Format**: `make format`
- **Type Check**: `uv run mypy .`
- **Run code**: you MUST use uv to run the code. for example `uv run ms_ai_assistant.cli`

## 3. Code Style & Rules
- **Formatting**: Use `make format`. Line length is 88 characters.
- **Linting**: Use `make lint`. Rules are configured in `pyproject.toml`.
- **Type Hints**: Mandatory for all function signatures. Must pass `mypy` checks. Avoid `typing.Any`.
- **Docstrings**: Google-style for all public modules, classes, and functions.
- **Error Handling**: Use `loguru` for logging. Use `@logger.catch` for robust error tracking.
- **Naming**: PEP 8 (`snake_case` for functions/variables, `PascalCase` for classes).
- **Imports**: `isort` is run via `ruff`. Order: stdlib, third-party, then local project modules.

## 4. Configuration (`Dynaconf`)
- **Usage**: Import the `settings` object from the project's `config.py`. Do not create new instances.
- **Files**: Settings are loaded from `settings.yaml`, `.secrets.yaml`, and `.env`.
- **Security**: Never commit secret files (`.secrets.yaml`, `.env`) to version control.

## 5. Key Libraries
- **Paths**: Use `pathlib` for all filesystem path manipulation.
- **CLI**: Use `typer` for building command-line interfaces.
- **Logging**: Use `loguru` for all application logging. Use appropriate log levels (trace, debug, info, success, warning, error, critical)

## 6. Logging
- **Implementation**: Use `loguru` for comprehensive logging
- **Message Quality**: Ensure clear, debuggable log messages with proper context
- **Log Levels**: Use appropriate levels (trace, debug, info, success, warning, error, critical)
- **Error Tracking**: Use `@logger.catch` for robust error tracking
