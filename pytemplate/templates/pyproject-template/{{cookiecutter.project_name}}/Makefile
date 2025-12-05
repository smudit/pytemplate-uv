# Detect the operating system
ifeq ($(OS),Windows_NT)
    PYTHON = python
    RM = del /f /q
    RMDIR = rmdir /s /q
    MKDIR = mkdir
else
    PYTHON = python
    RM = rm -f
    RMDIR = rm -rf
    MKDIR = mkdir -p
endif

# Use uv run for all commands to ensure correct venv
UV_RUN = uv run

# Targets
.PHONY: help setup dev start run lint lint-fix format format-check test test-cov clean build publish
{%- if cookiecutter.mypy == "y" %}
.PHONY: typecheck
{%- endif %}
{%- if cookiecutter.deptry == "y" %}
.PHONY: deptry
{%- endif %}
{%- if cookiecutter.mkdocs == "y" %}
.PHONY: docs-serve docs-build
{%- endif %}
.PHONY: quality

help:
	@echo " {{cookiecutter.project_name}} - Project Management Commands"
	@echo ""
	@echo "Development:"
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make dev      - Set up development environment (pre-commit, etc.)"
	@echo "  make start    - Start the application"
	@echo "  make run      - Alias for 'start'"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint     - Run code linting"
	@echo "  make lint-fix - Run linter with auto-fix"
	@echo "  make format   - Format code using Black"
	@echo "  make format-check - Check code formatting"
{%- if cookiecutter.mypy == "y" %}
	@echo "  make typecheck - Run type checking with mypy"
{%- endif %}
{%- if cookiecutter.deptry == "y" %}
	@echo "  make deptry   - Check for dependency issues"
{%- endif %}
	@echo "  make quality  - Run all quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  make test     - Run tests"
	@echo "  make test-cov - Run tests with coverage report"
	@echo ""
{%- if cookiecutter.mkdocs == "y" %}
	@echo "Documentation:"
	@echo "  make docs-serve - Serve documentation locally"
	@echo "  make docs-build - Build documentation"
	@echo ""
{%- endif %}
	@echo "Packaging:"
	@echo "  make build    - Build distribution packages"
	@echo "  make publish  - Publish package to PyPI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean    - Remove virtual environment and cache files"

# Setup project dependencies
setup:
	@echo "Creating virtual environment and installing dependencies..."
	uv sync
	$(UV_RUN) pre-commit install

# Development environment setup
dev: setup
	@echo "Development environment ready."

# Start the application
start:
	@echo "Starting application..."
	$(UV_RUN) python -m {{cookiecutter.package_name}}.cli

# Alias for start
run: start

# Linting
lint:
	@echo "Running linter..."
	$(UV_RUN) ruff check .

# Linting with auto-fix
lint-fix:
	@echo "Running linter with auto-fix..."
	$(UV_RUN) ruff check . --fix

# Code formatting
format:
	@echo "Formatting code with Black..."
	$(UV_RUN) black .

# Check code formatting
format-check:
	@echo "Checking code formatting..."
	$(UV_RUN) black . --check

# Run tests
test:
	@echo "Running tests..."
	$(UV_RUN) pytest tests/

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	$(UV_RUN) pytest --cov={{cookiecutter.package_name}} --cov-report=term-missing

# Clean up virtual environment and cache files
clean:
	@echo "Cleaning up..."
ifeq ($(OS),Windows_NT)
	-$(RMDIR) .venv 2>nul
	-$(RMDIR) .pytest_cache 2>nul
	-$(RMDIR) .ruff_cache 2>nul
	-$(RMDIR) .mypy_cache 2>nul
	-$(RM) .coverage 2>nul
	-for /d /r . %%d in (__pycache__) do @if exist "%%d" $(RMDIR) "%%d"
else
	$(RMDIR) .venv
	$(RMDIR) .pytest_cache
	$(RMDIR) .ruff_cache
	$(RMDIR) .mypy_cache
	$(RM) .coverage
	find . -type d -name "__pycache__" -exec $(RMDIR) {} + 2>/dev/null || true
endif

{%- if cookiecutter.mypy == "y" %}
# Type checking
typecheck:
	@echo "Running type checker..."
	$(UV_RUN) mypy .
{% endif %}
{%- if cookiecutter.deptry == "y" %}
# Check dependencies
deptry:
	@echo "Checking dependencies with deptry..."
	$(UV_RUN) deptry .
{% endif %}
{%- if cookiecutter.mkdocs == "y" %}
# Serve documentation locally
docs-serve:
	@echo "Serving documentation..."
	$(UV_RUN) mkdocs serve

# Build documentation
docs-build:
	@echo "Building documentation..."
	$(UV_RUN) mkdocs build
{% endif %}
# Run all quality checks
quality: lint format-check{% if cookiecutter.mypy == "y" %} typecheck{% endif %}{% if cookiecutter.deptry == "y" %} deptry{% endif %}

	@echo "All quality checks passed!"

# Build distribution packages
build:
	@echo "Building distribution packages..."
	$(UV_RUN) python -m build

# Publish to PyPI
publish: build
	@echo "Publishing to PyPI..."
	$(UV_RUN) twine upload dist/*
