# PyTemplate UV

## Overview

PyTemplate UV is a powerful CLI tool for creating Python project templates using the `uv` package manager. It provides a seamless way to generate standardized project structures with modern development practices.

## Features

- 🚀 Quick project initialization
- 🔧 Support for multiple project templates (FastAPI, Standard Python)
- 📦 Integrated with `uv` package management
- 🧪 Comprehensive testing infrastructure
- 🔍 Linting and type checking support

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

### Create a Project

```bash
# Create a standard Python project (default)
pytemplate-uv create-project

# Create a FastAPI project
pytemplate-uv create-project --template fastapi

# Create a project with a custom name
pytemplate-uv create-project --name my-awesome-project

# Create a project with custom template and name
pytemplate-uv create-project --template fastapi --name my-api-project
```

### Project Creation Options

- `--template`: Choose the project template (default: pyproject)
  - Options: `pyproject`, `fastapi`
- `--name`: Specify a custom project name
- Additional template-specific options can be passed as needed

### Next Steps After Project Creation

1. `cd` into your project directory
2. Run `uv venv` to create a virtual environment
3. Run `uv pip install -e .` to install dependencies
4. Run `make setup` to set up the development environment

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
  - `mock_template_config`: Mock template configuration

- `tests/test_cli.py`: CLI command tests covering:
  - Project creation (basic, with template, no-input, force)
  - Config-based project creation
  - Configuration file generation
  - Template management (init, list, copy)
  - Edge cases and error scenarios

#### Test Coverage

The test suite aims to cover:
- All CLI commands and their options
- Edge cases and error handling
- Template management functionality
- Project creation workflows
- Configuration file handling

### Linting

```bash
ruff check .
black .
mypy .
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

- [ ] use gh:arthurhenrique/cookiecutter-fastapi for fastapi template

Please review the code and help arrange the templates naming convention properly. Project uses two kind of template. One as the base template to create new project, which is more of a project-wide template. And then there are templates to define config and settings within the project. As currently the naming convention is using template for everything, it will be more suitable to adjust the naming convention to differentiate between the two. So please review the code thoroughly and suggest changes or implement changes, keeping in mind that it doesn't break the code.


Please fix the failing tests and remove any redundant tests. 