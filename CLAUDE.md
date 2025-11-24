# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyTemplate UV is a CLI tool for creating Python project templates using the `uv` package manager. It uses a configuration-driven approach to generate standardized project structures for libraries, services, and workspaces.

## Essential Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pytemplate tests/

# Run specific test file
uv run pytest tests/test_cli.py

# Run tests matching pattern
uv run pytest -k "test_create_project"
```

### Code Quality
```bash
# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy .
```

### Using the CLI
```bash
# Create a configuration file
uv run pytemplate create-config lib             # Library
uv run pytemplate create-config service         # Service
uv run pytemplate create-config workspace       # Workspace

# Create project from config
uv run pytemplate create-project-from-config project_config.yaml

# With options
uv run pytemplate create-project-from-config project_config.yaml --interactive
uv run pytemplate create-project-from-config project_config.yaml --force
uv run pytemplate create-project-from-config project_config.yaml --debug
```

## Architecture Overview

### Core Components

**1. Template Resolution System (`template_manager.py`)**
- `TemplateResolver`: Resolves template paths from `template_paths.yaml`
- `TemplateManager`: Manages template operations
- Templates are resolved relative to package directory or from GitHub repos (e.g., `gh:ionelmc/cookiecutter-pylibrary`)

**2. Project Creation Pipeline (`project_creator.py`)**
- `ProjectCreator`: Main orchestrator for project creation
- Flow: Load config → Validate → Create with Cookiecutter → Initialize Git → Create GitHub repo (optional) → Copy AI templates
- Handles three project types: `lib` (libraries), `service` (applications/APIs), `workspace` (monorepos)

**3. CLI Interface (`main.py`)**
- Built with Typer
- Two main commands: `create-config` and `create-project-from-config`
- Supports interactive mode, debug logging, and force overwrite

### Template System

The project uses a three-tier template architecture defined in `pytemplate/template_paths.yaml`:

1. **Project Scaffolds** (`project_scaffolds`): Cookiecutter templates for directory structure
   - `pyproject`: For services and workspaces (local template)
   - `pylibrary`: For libraries (GitHub: ionelmc/cookiecutter-pylibrary)
   - `terraform-infra`: For infrastructure (GitHub template)

2. **Configuration Specifications** (`config_specs`): YAML templates defining project requirements
   - `lib.yaml.template`: Library project configuration
   - `service.yaml.template`: Service project configuration (includes Docker)
   - `workspace.yaml.template`: Workspace/monorepo configuration

3. **Shared Resources** (`shared_resources`): Common files copied to all projects
   - `coding_rules.md`: Coding guidelines distributed to AI copilots

### AI Copilot Integration

The system automatically copies coding rules to multiple AI copilot configuration files:
- Cursor: `.cursor/rules`
- Cline: `.clinerules`
- Augment: `.augment-guidelines`
- Claude: `CLAUDE.md`

Configuration is managed via `ai_copilots` section in `template_paths.yaml`.

### Project Type Differences

**Library (`lib`)**:
- Uses `pylibrary` Cookiecutter template
- Full documentation setup (Sphinx)
- PyPI publishing configuration
- No Docker/DevContainer support
- Complex development settings (coverage, code quality tools, etc.)

**Service (`service`)**:
- Uses `pyproject` template
- Docker and docker-compose support
- DevContainer for VS Code
- Service port configuration
- Simpler structure focused on deployment

**Workspace (`workspace`)**:
- Uses `pyproject` template
- Shared dependencies management
- DevContainer support
- No Docker by default

## Key Implementation Details

### Configuration Loading and Validation

The `ProjectCreator.load_config()` method:
1. Parses YAML configuration
2. Validates required sections: `project`, `github`, `docker`, `devcontainer`
3. Validates project type is one of: `lib`, `service`, `workspace`
4. Validates Docker settings (libraries can't have Docker, services must have Docker)
5. Validates project name format (alphanumeric, underscore, hyphen only)
6. Validates development settings (CLI interface options, etc.)

### Template Path Resolution

Template paths in `template_paths.yaml` are resolved as:
- GitHub repos: `gh:username/repo` (passed directly to Cookiecutter)
- Local paths: Relative to package directory (e.g., `templates/pyproject-template`)

The `TemplateResolver._resolve_template_path()` handles both cases.

### Library Project Creation

Library projects use special handling in `_create_project_with_cookiecutter()`:
1. Maps configuration from `lib.yaml.template` format to Cookiecutter context
2. Derives `repo_name` from `project_name` if not specified
3. Converts boolean flags to "yes"/"no" strings for Cookiecutter
4. Handles complex development settings (pytest, sphinx, coverage tools, etc.)

### Git and GitHub Integration

Projects are initialized with:
1. Local Git repo on `main` branch (always)
2. Initial commit with all generated files
3. Optional GitHub repo creation via `gh` CLI
4. Automatic push to GitHub if created

## Testing Strategy

### Test Structure (`tests/`)

- `conftest.py`: Shared fixtures for temporary directories, sample configs, and mock templates
- `test_cli.py`: CLI command tests (help, options, error handling)
- `test_template_manager.py`: Template resolution and path management tests
- `test_project_creator.py`: End-to-end project creation tests

### Important Test Fixtures

- `temp_project_dir`: Temporary directory for project creation
- `sample_lib_config`: Sample library configuration file
- `mock_template_config`: Mock template configuration with new naming convention

### Testing Mode

`ProjectCreator.enable_testing_mode()` allows proper exception propagation instead of `typer.Exit()` for testability.

## Common Development Patterns

### Adding a New Project Type

1. Create configuration template in `pytemplate/templates/configs/`
2. Add entry to `config_specs` in `template_paths.yaml`
3. Update validation in `ProjectCreator._validate_project_type()`
4. Add special handling in `_create_project_with_cookiecutter()` if needed
5. Create tests in `tests/test_cli.py`

### Adding a New AI Copilot

1. Add entry to `ai_copilots` in `template_paths.yaml`
2. Format: `copilot_name: path/to/rules/file`
3. The system will automatically copy `coding_rules.md` to the specified path

### Modifying Template Resolution

Template resolution logic is in `TemplateResolver`:
- `get_template_path()`: Main entry point
- `_get_relative_path()`: Retrieves path from config
- `_resolve_template_path()`: Converts relative to absolute paths

## Code Style Notes

- Line length: 100 characters (Black/Ruff configuration)
- Type hints required for all public functions
- Google-style docstrings with Args/Returns/Raises sections
- Use `loguru` for all logging with appropriate levels
- Exception handling: Raise `typer.Exit()` for CLI errors, allow exceptions in testing mode

## Security Considerations

- Repository names are validated with regex: `^[a-z0-9-_]{1,100}$`
- Project names validated: alphanumeric, underscore, hyphen only
- Template paths verified to prevent directory traversal (in `TemplateResolver`)
- No secrets should be committed (`.env`, `.secrets*` in `.gitignore`)
