# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## 🚀 Features

- Clean, modern Python project structure
- Comprehensive development tooling
- Easy-to-use CLI
- Robust testing and type checking

## 📦 Installation

```bash
# Using pip
pip install {{cookiecutter.package_name}}

# Using uv
uv pip install {{cookiecutter.package_name}}
```

## 🔧 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python {{cookiecutter.python_version}}+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **[Task](https://taskfile.dev/)** - Task runner (optional but recommended)
  ```bash
  # macOS
  brew install go-task
  # Linux/WSL
  sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
  # Windows
  choco install go-task
  ```

## 🔧 Development Setup

1. Clone the repository
2. Install dependencies (includes dev tools)
```bash
task setup
# Or without Task:
uv sync --extra dev --extra test && uv run pre-commit install
```

This creates the virtual environment, installs all dependencies including dev tools, and sets up pre-commit hooks.

## 💻 Usage

### CLI Commands

```bash
# Show help
{{cookiecutter.package_name}} --help

# Hello command
{{cookiecutter.package_name}} hello --name World

# Project info
{{cookiecutter.package_name}} info
```

## 🧪 Testing

Run tests with comprehensive coverage:

```bash
task test
```

## 📝 Development Workflow

- `task lint`: Run code linters
- `task lint-fix`: Run linter with auto-fix
- `task format`: Auto-format code
- `task format-check`: Check code formatting
- `task test`: Run tests
- `task test-cov`: Run tests with coverage report
- `task quality`: Run all quality checks (lint, format-check{% if cookiecutter.mypy == "y" %}, typecheck{% endif %}{% if cookiecutter.deptry == "y" %}, deptry{% endif %})
{%- if cookiecutter.mkdocs == "y" %}
- `task docs-serve`: Serve documentation locally
- `task docs-build`: Build documentation
{%- endif %}

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

{{cookiecutter.license}} License

## 👥 Authors

- {{cookiecutter.author}} <{{cookiecutter.email}}>
