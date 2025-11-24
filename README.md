# PyTemplate UV

## Overview

PyTemplate UV is a powerful CLI tool for creating Python project templates using the `uv` package manager. It provides a seamless way to generate standardized project structures with modern development practices.

## Features

- 🚀 Quick project initialization with configuration-driven approach
- 🔧 Support for multiple project types (Library, Service, Workspace)
- 📦 Integrated with `uv` package management
- 🧪 Comprehensive testing infrastructure
- 🔍 Linting and type checking support
- 🐳 Docker and DevContainer support for services
- 🤖 AI copilot integration (Cursor, Cline)

## Prerequisites

- Python 3.11+
- `uv` package manager
- `cookiecutter`

## Installation

To install the project creator tool:

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install the tool:

   ```bash
   pip install -e .
   ```

3. Now you can use the `create-project` command from anywhere while your virtual environment is activated.

## Usage

PyTemplate UV uses a two-step process for project creation:

1. Create a configuration file that specifies project requirements
2. Generate the project structure from the configuration

### Step 1: Create a Configuration File

```bash
# Create configuration for a library project
pytemplate-uv create-config lib

# Create configuration for a service project
pytemplate-uv create-config service

# Create configuration for a workspace project
pytemplate-uv create-config workspace

# Specify custom output path
pytemplate-uv create-config lib --output-path my-lib-config.yaml
```

### Step 2: Create Project from Configuration

```bash
# Create project from configuration file
pytemplate-uv create-project-from-config project_config.yaml

# With interactive mode (allows customization during creation)
pytemplate-uv create-project-from-config project_config.yaml --interactive

# Force overwrite existing directory
pytemplate-uv create-project-from-config project_config.yaml --force
```

### Template Architecture

PyTemplate UV uses three types of templates:

1. **Project Scaffolds** (`project_scaffolds/`): Cookiecutter templates that create project directory structures
   - `pyproject`: Basic Python project structure for services and workspaces
   - `pylibrary`: Full-featured library structure with documentation, CI/CD

2. **Configuration Specifications** (`config_specs/`): YAML templates that define project requirements
   - `lib.yaml.template`: Configuration for library projects
   - `service.yaml.template`: Configuration for service projects (includes Docker)
   - `workspace.yaml.template`: Configuration for workspace/monorepo projects

3. **Shared Resources** (`shared_resources/`): Common files copied to projects
   - `coding_rules.md`: Coding guidelines for AI assistants
   - AI copilot files are automatically configured for:
     - Cursor (`.cursor/rules`)
     - Cline (`.clinerules`)
     - Augment (`.augment-guidelines`)
     - Claude (`CLAUDE.md`)

### Project Types

- **Library (`lib`)**: Python packages meant for distribution
  - Full testing and documentation setup
  - PyPI publishing configuration
  - No Docker/DevContainer support

- **Service (`service`)**: Standalone applications/APIs
  - Docker and docker-compose support
  - DevContainer for VS Code
  - Service port configuration

- **Workspace (`workspace`)**: Monorepo or multi-project setups
  - Shared dependencies management
  - DevContainer support
  - No Docker by default

### Next Steps After Project Creation

1. `cd` into your project directory
2. Run `uv sync` to create virtual environment and install dependencies
3. For services: Run `docker-compose up` if Docker is configured
4. For libraries: Run tests with `pytest`

## Development

### Setup

1. Clone the repository
2. Create a virtual environment:

   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install development dependencies:

   ```bash
   uv sync  # Install all dependencies from pyproject.toml
   # Or install with development extras
   uv pip install -e .[dev]
   ```

### Running Tests

The project uses pytest for testing. The test suite includes comprehensive tests for all CLI commands and edge cases.

#### Setting Up Test Environment

1. Create a dedicated test virtual environment:

   ```bash
   # Using uv
   uv venv .venv-test
   source .venv-test/bin/activate  # On Windows: .venv-test\Scripts\activate
   uv pip install -e .[dev]

   # Or using standard venv
   python -m venv .venv-test
   source .venv-test/bin/activate  # On Windows: .venv-test\Scripts\activate
   pip install -e .[dev]
   ```

2. Run tests using the specific virtual environment:

   ```bash
   # Using the activated virtual environment
   pytest

   # Or specify python path directly
   .venv-test/bin/python -m pytest  # On Windows: .venv-test\Scripts\python -m pytest
   ```

#### Test Commands

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=pytemplate tests/

# Run specific test file
pytest tests/test_cli.py

# Run tests matching specific pattern
pytest -k "test_create_project"

# Run tests with specific python interpreter
/path/to/venv/bin/python -m pytest
```

#### Test Structure

- `tests/conftest.py`: Contains test fixtures including:
  - `temp_project_dir`: Temporary directory for project creation
  - `project_templates_path`: Path to test templates
  - `temp_config_dir`: Temporary directory for config files
  - `sample_lib_config`: Sample library configuration
  - `temp_templates_dir`: Temporary templates directory
  - `mock_template_config`: Mock template configuration with new naming convention

- `tests/test_cli.py`: CLI command tests covering:
  - Configuration-based project creation
  - Configuration file generation for all project types
  - Debug and force flags
  - Error handling scenarios

- `tests/test_template_manager.py`: Template management tests:
  - Template path resolution
  - Project scaffold loading
  - Configuration spec handling
  - Shared resource management

#### Test Coverage

The test suite comprehensively covers:

- All CLI commands and their options
- Configuration validation and loading
- Template resolution with new naming convention
- Project creation for all types (lib, service, workspace)
- Edge cases and security scenarios
- Integration tests for end-to-end workflows

### Linting and Type Checking

```bash
# Run all linting and formatting
make lint      # Run ruff linter
make format    # Run ruff formatter

# Or run individually
ruff check .   # Lint code
ruff format .  # Format code
mypy .         # Type checking (requires mypy>=1.15.0)
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contact

Leo Liu - [GitHub](https://github.com/yuxuzi)

---

*Simplifying Python project creation with modern best practices* 🐍✨

# TODO

- [] Add .gitignore to shared resources
- [] Add CLAUDE.md to ai rules
- [] Fix not creating git if add_on_github is false
