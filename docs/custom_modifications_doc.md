# Custom Template Modifications Documentation

## Current Template Overview
**Template Name**: pyproject-template  
**Location**: `pytemplate/templates/pyproject-template/`  
**Template Engine**: Cookiecutter  

## Core Custom Features

### 1. Dynaconf Configuration System
- **File**: `{{cookiecutter.package_name}}/config.py`
- **Features**:
  - Environment-based configuration with `settings.yaml` and `.secrets.yaml`
  - Environment variable support with DYNACONF prefix
  - Automatic `.env` file loading
  - Centralized settings object accessible throughout the app

### 2. Loguru Logging Setup
- **File**: `{{cookiecutter.package_name}}/config.py`
- **Features**:
  - Pre-configured colored console output
  - Automatic log rotation (10 MB)
  - Log retention (1 week)
  - Compression of old logs
  - Structured log format with timestamps
  - Configurable log levels via settings

### 3. Typer CLI Framework
- **File**: `{{cookiecutter.package_name}}/cli.py`
- **Features**:
  - Rich integration for better terminal output
  - Structured CLI entry point
  - Command-line argument parsing
  - Help text generation

### 4. Project Structure
```
{{cookiecutter.project_name}}/
├── {{cookiecutter.package_name}}/
│   ├── __init__.py
│   ├── cli.py         # Typer CLI entry point
│   ├── config.py      # Dynaconf + Loguru setup
│   └── main.py        # Main application logic
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_main.py
├── Dockerfile         # Docker support
├── Makefile           # Development commands
├── README.md
├── pyproject.toml     # Project configuration
└── {{cookiecutter.envfile}}  # Environment variables
```

### 5. Development Tools Configuration

#### Ruff Configuration
- Line length: 88
- Target Python: 3.11+
- Enabled rules: E, F, W, I, N, UP, C4
- isort integration with 2 lines after imports

#### Black Configuration
- Line length: 88
- Target Python: 3.11+
- Preview mode enabled

#### MyPy Configuration
- Strict mode enabled
- Disallow untyped definitions
- Warn on return any
- Python version: 3.11

#### Pytest Configuration
- Coverage enabled by default
- Coverage report in terminal
- Test path: tests/
- Filters deprecation warnings

### 6. Build System
- **Current**: setuptools with setuptools_scm
- **Package Discovery**: Explicit package listing
- **Entry Points**: CLI script via project.scripts

### 7. Dependencies

#### Core Dependencies
- python-dotenv (>=1.0.0) - Environment variable loading
- loguru (>=0.7.0) - Advanced logging
- dynaconf (>=3.2.10) - Configuration management
- typer (>=0.9.0) - CLI framework
- rich (>=13.7.0) - Terminal formatting
- pydantic (>=2.6.0) - Data validation

#### Development Dependencies
- ruff (>=0.1.9) - Linting and formatting
- pytest (>=7.4.4) - Testing
- black (>=23.12.1) - Code formatting
- pre-commit (>=3.6.0) - Git hooks
- mypy (>=1.7.1) - Type checking
- coverage (>=7.4.0) - Code coverage

#### Documentation Dependencies
- mkdocs (>=1.5.3) - Documentation site
- mkdocstrings[python] (>=0.24.0) - Python docs
- pdoc (>=0.10.0) - API documentation

### 8. Makefile Commands
The template includes a Makefile with development commands:
- lint
- format
- test
- type checking
- documentation generation

### 9. Docker Support
- Dockerfile included with cookiecutter conditional
- Configurable via `dockerfile` parameter

### 10. Cookiecutter Variables
```json
{
    "project_name": "my-python-project",
    "package_name": "{{cookiecutter.project_name|lower|replace('-', '_')}}",
    "description": "A Python project template",
    "author": "Your Name",
    "email": "your@email.com",
    "github_username": "your_username",
    "python_version": "3.11",
    "docs": "y",
    "coverage": "y",
    "dockerfile": "y",
    "mypy": "y",
    "license": "MIT",
    "envfile": ".env"
}
```

## Key Differences from Standard Templates

1. **Configuration Management**: Full Dynaconf integration vs simple .env
2. **Logging**: Loguru with rotation/compression vs standard logging
3. **CLI**: Typer with Rich integration vs argparse/click
4. **Build System**: setuptools vs modern hatchling
5. **Testing**: Integrated coverage reporting
6. **Documentation**: Both mkdocs and pdoc support

## Migration Considerations

### Must Preserve
1. Dynaconf configuration system
2. Loguru logging setup
3. Typer CLI structure
4. Rich terminal formatting
5. Comprehensive type checking setup

### Can Adapt
1. Build system (setuptools → hatchling)
2. Package manager (pip → uv)
3. Formatter consolidation (black + ruff → ruff only)
4. Documentation system (pdoc → mkdocs only)

### New Features to Add
1. uv package management
2. Hatchling build backend
3. GitHub Actions workflows
4. Consolidated ruff configuration
5. Modern Python packaging standards