# CLAUDE.md - Guide for agentic assistants working with pytemplate-uv

## Build/Test Commands
- Install: `pip install -e .[dev]`
- Lint: `ruff check .`
- Format: `black .`
- Type check: `mypy .`
- Run tests: `pytest`
- Run single test: `pytest tests/test_file.py::test_function_name`
- Test with coverage: `pytest --cov=pytemplate`

## Code Style
- **Formatting**: Black with 100 char line length
- **Linting**: Ruff with rules E,W,F,I,B,UP,C90,N,D
- **Types**: All functions must have type hints; avoid `Any`
- **Imports**: Use isort (via ruff); stdlib first, then third-party, then local
- **Documentation**: Google-style docstrings for all functions/classes
- **Error handling**: Use loguru for logging errors; `@logger.catch` for tracking
- **Naming**: Follow PEP8; snake_case for vars/functions, PascalCase for classes
- **Organization**: Keep files under 500 lines; one class per file
- **Libraries**: Use pathlib for paths, typer for CLI, loguru for logging
- **Testing**: Write tests for all new functionality