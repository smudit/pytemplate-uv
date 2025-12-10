#!/usr/bin/env python3
"""Automated migration script for converting projects to modern uv-based toolchain.

This script migrates existing Python projects to use:
- uv for package management
- setuptools as build backend
- Taskfile for task running
- ruff for linting and formatting
- Modern GitHub Actions with setup-uv@v4
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import toml
import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

app = typer.Typer(
    name="migrate-to-uv",
    help="Migrate existing Python projects to modern uv-based toolchain",
)
console = Console()


def setup_logger(verbose: bool = False) -> None:
    """Set up logging."""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )


# =============================================================================
# Project Analysis
# =============================================================================


def analyze_project(project_path: Path) -> dict:
    """Analyze existing project structure and extract metadata.

    Args:
        project_path: Path to the project directory.

    Returns:
        Dictionary containing project analysis results.
    """
    analysis = {
        "project_name": project_path.name,
        "package_name": None,
        "version": "0.1.0",
        "description": "",
        "authors": [],
        "python_requires": ">=3.11",
        "dependencies": [],
        "dev_dependencies": [],
        "scripts": {},
        "has_pyproject": False,
        "has_setup_py": False,
        "has_requirements": False,
        "has_makefile": False,
        "has_taskfile": False,
        "has_dockerfile": False,
        "has_github_actions": False,
        "has_tests": False,
        "has_src_layout": False,
        "build_backend": None,
        "uses_black": False,
        "uses_ruff": False,
        "uses_mypy": False,
        "uses_pytest": False,
        "uses_pre_commit": False,
    }

    # Detect package name from directory structure
    if (project_path / "src").exists():
        analysis["has_src_layout"] = True
        src_packages = [
            d.name for d in (project_path / "src").iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]
        if src_packages:
            analysis["package_name"] = src_packages[0]
    else:
        # Look for package directories (containing __init__.py)
        for item in project_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                if item.name not in ("tests", "test", "docs", "build", "dist"):
                    analysis["package_name"] = item.name
                    break

    if not analysis["package_name"]:
        # Fallback: derive from project name
        analysis["package_name"] = analysis["project_name"].replace("-", "_").lower()

    # Check for various files
    analysis["has_pyproject"] = (project_path / "pyproject.toml").exists()
    analysis["has_setup_py"] = (project_path / "setup.py").exists()
    analysis["has_requirements"] = (project_path / "requirements.txt").exists()
    analysis["has_makefile"] = (project_path / "Makefile").exists()
    analysis["has_taskfile"] = (
        (project_path / "Taskfile.yml").exists() or
        (project_path / "Taskfile.yaml").exists()
    )
    analysis["has_dockerfile"] = (project_path / "Dockerfile").exists()
    analysis["has_github_actions"] = (project_path / ".github" / "workflows").exists()
    analysis["has_tests"] = (
        (project_path / "tests").exists() or
        (project_path / "test").exists()
    )

    # Parse existing pyproject.toml if present
    if analysis["has_pyproject"]:
        analysis = _parse_pyproject(project_path / "pyproject.toml", analysis)

    # Parse setup.py if present and no pyproject.toml
    if analysis["has_setup_py"] and not analysis["has_pyproject"]:
        analysis = _parse_setup_py(project_path / "setup.py", analysis)

    # Parse requirements.txt if present
    if analysis["has_requirements"]:
        analysis = _parse_requirements(project_path / "requirements.txt", analysis)

    # Check for dev requirements
    dev_req_files = ["requirements-dev.txt", "requirements_dev.txt", "dev-requirements.txt"]
    for dev_req in dev_req_files:
        if (project_path / dev_req).exists():
            analysis = _parse_requirements(
                project_path / dev_req, analysis, is_dev=True
            )

    return analysis


def _parse_pyproject(pyproject_path: Path, analysis: dict) -> dict:
    """Parse existing pyproject.toml for project metadata."""
    try:
        config = toml.load(pyproject_path)

        # Extract project metadata
        project = config.get("project", {})
        analysis["project_name"] = project.get("name", analysis["project_name"])
        analysis["version"] = project.get("version", analysis["version"])
        analysis["description"] = project.get("description", "")
        analysis["authors"] = project.get("authors", [])
        analysis["python_requires"] = project.get("requires-python", ">=3.11")
        analysis["dependencies"] = project.get("dependencies", [])
        analysis["scripts"] = project.get("scripts", {})

        # Extract dev dependencies
        optional_deps = project.get("optional-dependencies", {})
        for group in ["dev", "test", "development"]:
            if group in optional_deps:
                analysis["dev_dependencies"].extend(optional_deps[group])

        # Check build backend
        build_system = config.get("build-system", {})
        analysis["build_backend"] = build_system.get("build-backend")

        # Check tool configurations
        tools = config.get("tool", {})
        analysis["uses_black"] = "black" in tools
        analysis["uses_ruff"] = "ruff" in tools
        analysis["uses_mypy"] = "mypy" in tools
        analysis["uses_pytest"] = "pytest" in tools

        # Check if pre-commit config exists
        analysis["uses_pre_commit"] = (pyproject_path.parent / ".pre-commit-config.yaml").exists()

    except Exception as e:
        logger.warning(f"Failed to parse pyproject.toml: {e}")

    return analysis


def _parse_setup_py(setup_path: Path, analysis: dict) -> dict:
    """Parse setup.py for basic project metadata."""
    try:
        content = setup_path.read_text()

        # Extract name
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if name_match:
            analysis["project_name"] = name_match.group(1)

        # Extract version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            analysis["version"] = version_match.group(1)

        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if desc_match:
            analysis["description"] = desc_match.group(1)

    except Exception as e:
        logger.warning(f"Failed to parse setup.py: {e}")

    return analysis


def _parse_requirements(req_path: Path, analysis: dict, is_dev: bool = False) -> dict:
    """Parse requirements.txt file."""
    try:
        content = req_path.read_text()
        deps = []

        for line in content.splitlines():
            line = line.strip()
            # Skip comments, empty lines, and -r includes
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            deps.append(line)

        if is_dev:
            analysis["dev_dependencies"].extend(deps)
        else:
            # Don't overwrite if we already have deps from pyproject.toml
            if not analysis["dependencies"]:
                analysis["dependencies"] = deps

    except Exception as e:
        logger.warning(f"Failed to parse {req_path}: {e}")

    return analysis


def show_analysis(analysis: dict) -> None:
    """Display project analysis results."""
    table = Table(title="Project Analysis")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Project Name", analysis["project_name"])
    table.add_row("Package Name", analysis["package_name"] or "Not detected")
    table.add_row("Version", analysis["version"])
    table.add_row("Python Requires", analysis["python_requires"])
    table.add_row("Build Backend", analysis["build_backend"] or "None")
    table.add_row("Dependencies", str(len(analysis["dependencies"])))
    table.add_row("Dev Dependencies", str(len(analysis["dev_dependencies"])))

    console.print(table)

    # Show detected features
    features_table = Table(title="Detected Features")
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Status", style="green")

    feature_checks = [
        ("pyproject.toml", analysis["has_pyproject"]),
        ("setup.py", analysis["has_setup_py"]),
        ("requirements.txt", analysis["has_requirements"]),
        ("Makefile", analysis["has_makefile"]),
        ("Taskfile", analysis["has_taskfile"]),
        ("Dockerfile", analysis["has_dockerfile"]),
        ("GitHub Actions", analysis["has_github_actions"]),
        ("Tests directory", analysis["has_tests"]),
        ("src/ layout", analysis["has_src_layout"]),
        ("Black", analysis["uses_black"]),
        ("Ruff", analysis["uses_ruff"]),
        ("Mypy", analysis["uses_mypy"]),
        ("Pytest", analysis["uses_pytest"]),
        ("Pre-commit", analysis["uses_pre_commit"]),
    ]

    for feature, enabled in feature_checks:
        status = "✓" if enabled else "✗"
        color = "green" if enabled else "dim"
        features_table.add_row(feature, f"[{color}]{status}[/{color}]")

    console.print(features_table)


# =============================================================================
# File Generation
# =============================================================================


def generate_pyproject_toml(analysis: dict) -> str:
    """Generate a modern pyproject.toml based on project analysis.

    Args:
        analysis: Project analysis dictionary.

    Returns:
        Generated pyproject.toml content as string.
    """
    project_name = analysis["project_name"]
    package_name = analysis["package_name"]
    version = analysis["version"]
    # Sanitize description - take first line only and escape quotes
    raw_description = analysis["description"] or f"{project_name} - A Python project"
    description = raw_description.split("\n")[0].strip().replace('"', '\\"')
    python_requires = analysis["python_requires"]

    # Ensure python version is at least 3.11
    if python_requires and not _check_python_version(python_requires, "3.11"):
        python_requires = ">=3.11"

    # Extract python version number for target-version (e.g., "3.11" -> "py311")
    py_version = "3.11"
    if ">=" in python_requires:
        py_version = python_requires.replace(">=", "").strip()
    py_target = f"py{py_version.replace('.', '')}"

    # Format authors
    authors_str = ""
    if analysis["authors"]:
        authors_list = []
        for author in analysis["authors"]:
            if isinstance(author, dict):
                name = author.get("name", "")
                email = author.get("email", "")
                if email:
                    authors_list.append(f'    {{name = "{name}", email = "{email}"}}')
                else:
                    authors_list.append(f'    {{name = "{name}"}}')
            elif isinstance(author, str):
                authors_list.append(f'    {{name = "{author}"}}')
        authors_str = ",\n".join(authors_list)

    # Format dependencies - add standard deps if empty
    deps = _normalize_dependencies(analysis["dependencies"])
    if not deps:
        deps = [
            "loguru>=0.7.0",
            "dynaconf>=3.2.10",
            "typer>=0.9.0",
            "rich>=13.7.0",
        ]
    deps_str = ",\n".join(f'    "{dep}"' for dep in deps)

    # Format dev dependencies
    dev_deps = _normalize_dependencies(analysis["dev_dependencies"])
    # Add standard dev tools if not present
    standard_dev_deps = [
        "ruff>=0.1.9",
        "pytest>=7.4.4",
        "black>=23.12.1",
        "pre-commit>=3.6.0",
        "pre-commit-hooks>=4.5.0",
        "mypy>=1.7.1",
        "coverage>=7.4.0",
        "build>=1.0.0",
        "twine>=4.0.0",
        "deptry>=0.12.0",
    ]
    for std_dep in standard_dev_deps:
        pkg_name = std_dep.split(">=")[0].split("==")[0].split("<")[0]
        if not any(pkg_name in d for d in dev_deps):
            dev_deps.append(std_dep)

    dev_deps_str = ",\n".join(f'    "{dep}"' for dep in sorted(set(dev_deps)))

    # Format scripts/entry points
    scripts_section = ""
    if analysis["scripts"]:
        scripts_list = [
            f'{name} = "{entry}"' for name, entry in analysis["scripts"].items()
        ]
        scripts_section = "[project.scripts]\n" + "\n".join(scripts_list) + "\n"
    else:
        # Default CLI entry point
        scripts_section = f'''[project.scripts]
{package_name} = "{package_name}.cli:main"
'''

    # Determine package discovery for hatch
    if analysis["has_src_layout"]:
        packages_config = f'''[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]
'''
    else:
        packages_config = f'''[tool.hatch.build.targets.wheel]
packages = ["{package_name}"]
'''

    # Build the pyproject.toml content with hatchling
    content = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "{version}"
description = "{description}"
readme = "README.md"
requires-python = "{python_requires}"
license = {{text = "MIT"}}
'''

    if authors_str:
        content += f'''authors = [
{authors_str}
]
'''

    content += f'''keywords = ["python"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: {py_version}",
]

dependencies = [
{deps_str}
]

[project.optional-dependencies]
dev = [
{dev_deps_str}
]
test = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
]

{scripts_section}
{packages_config}
[tool.ruff]
line-length = 100
target-version = "{py_target}"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "C4",  # flake8-comprehensions
]
# E501 (line too long) is handled by Black formatter
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["{package_name}"]
combine-as-imports = true
lines-after-imports = 2

[tool.black]
line-length = 100
target-version = ['{py_target}']
preview = true

[tool.mypy]
python_version = "{py_version}"
strict = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov={package_name} --cov-report=term-missing"
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::UserWarning",
]

[tool.coverage.run]
source = ["{package_name}"]
omit = ["tests/*"]

[tool.deptry]
extend_exclude = ["tests", "docs"]
'''

    return content


def _check_python_version(requires: str, min_version: str) -> bool:
    """Check if requires-python includes the minimum version."""
    # Simple check - could be more sophisticated
    if ">=" in requires:
        version = requires.replace(">=", "").strip()
        return version >= min_version
    return True


def _normalize_dependencies(deps: list[str]) -> list[str]:
    """Normalize dependency specifications."""
    normalized = []
    for dep in deps:
        # Skip empty or comment lines
        if not dep or dep.startswith("#"):
            continue
        # Extract package name and normalize
        dep = dep.strip()
        normalized.append(dep)
    return normalized


def generate_taskfile(analysis: dict, project_path: Path) -> str:
    """Generate a Taskfile.yaml for the project.

    Args:
        analysis: Project analysis dictionary.
        project_path: Path to the project directory.

    Returns:
        Generated Taskfile.yaml content.
    """
    project_name = analysis["project_name"]
    package_name = analysis["package_name"]

    content = f'''# https://taskfile.dev
version: '3'

vars:
  PROJECT_NAME: {project_name}
  PACKAGE_NAME: {package_name}

tasks:
  default:
    desc: Show available tasks
    cmds:
      - task --list-all
    silent: true

  # ============================================================================
  # Development
  # ============================================================================
  setup:
    desc: Create virtual environment and install dependencies
    cmds:
      - echo "Creating virtual environment and installing dependencies..."
      - uv sync --extra dev --extra test
      - uv run pre-commit install

  dev:
    desc: Set up development environment (pre-commit, etc.)
    deps: [setup]
    cmds:
      - echo "Development environment ready."

  start:
    desc: Start the application
    cmds:
      - echo "Starting application..."
      - uv run python -m {{{{.PACKAGE_NAME}}}}.cli

  run:
    desc: Alias for 'start'
    deps: [start]

  # ============================================================================
  # Code Quality
  # ============================================================================
  lint:
    desc: Run code linting
    cmds:
      - echo "Running linter..."
      - uv run ruff check .

  lint-fix:
    desc: Run linter with auto-fix
    cmds:
      - echo "Running linter with auto-fix..."
      - uv run ruff check . --fix

  format:
    desc: Format code using Black
    cmds:
      - echo "Formatting code with Black..."
      - uv run black .

  format-check:
    desc: Check code formatting
    cmds:
      - echo "Checking code formatting..."
      - uv run black . --check

  typecheck:
    desc: Run type checking with mypy
    cmds:
      - echo "Running type checker..."
      - uv run mypy .

  deptry:
    desc: Check for dependency issues
    cmds:
      - echo "Checking dependencies with deptry..."
      - uv run deptry .

  quality:
    desc: Run all quality checks
    cmds:
      - task: lint
      - task: format-check
      - task: typecheck
      - task: deptry
      - echo "All quality checks passed!"

  # ============================================================================
  # Testing
  # ============================================================================
  test:
    desc: Run tests
    cmds:
      - echo "Running tests..."
      - uv run pytest tests/

  test-cov:
    desc: Run tests with coverage report
    cmds:
      - echo "Running tests with coverage..."
      - uv run pytest --cov={{{{.PACKAGE_NAME}}}} --cov-report=term-missing

  # ============================================================================
  # Packaging
  # ============================================================================
  build:
    desc: Build distribution packages
    cmds:
      - echo "Building distribution packages..."
      - rm -rf dist/
      - uv build

  publish:
    desc: Publish package to PyPI
    deps: [build]
    cmds:
      - echo "Publishing to PyPI..."
      - uv publish

  # ============================================================================
  # Cleanup
  # ============================================================================
  clean:
    desc: Remove virtual environment and cache files
    cmds:
      - echo "Cleaning up..."
      - rm -rf .venv .pytest_cache .ruff_cache .mypy_cache .coverage dist *.egg-info
      - find . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null || true
    platforms: [linux, darwin]

  clean:windows:
    desc: Remove virtual environment and cache files (Windows)
    cmds:
      - echo "Cleaning up..."
      - cmd /c "if exist .venv rmdir /s /q .venv"
      - cmd /c "if exist .pytest_cache rmdir /s /q .pytest_cache"
      - cmd /c "if exist .ruff_cache rmdir /s /q .ruff_cache"
      - cmd /c "if exist .mypy_cache rmdir /s /q .mypy_cache"
      - cmd /c "if exist .coverage del /f /q .coverage"
      - cmd /c "for /d /r . %%d in (__pycache__) do @if exist \\"%%d\\" rmdir /s /q \\"%%d\\""
    platforms: [windows]
'''

    return content


def generate_github_actions(analysis: dict) -> str:
    """Generate GitHub Actions CI workflow.

    Args:
        analysis: Project analysis dictionary.

    Returns:
        Generated CI workflow content.
    """
    package_name = analysis["package_name"]

    # Note: Template uses ruff format --check in CI even though local uses black
    # This is intentional for CI speed while allowing black locally
    content = f'''name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    env:
      UV_PYTHON: ${{{{ matrix.python-version }}}}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python ${{{{ matrix.python-version }}}}
        run: uv python install ${{{{ matrix.python-version }}}}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run ruff linting
        run: uv run ruff check .

      - name: Run ruff formatting check
        run: uv run ruff format --check .

      - name: Run mypy type checking
        run: uv run mypy .

      - name: Run deptry
        run: uv run deptry .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    env:
      UV_PYTHON: ${{{{ matrix.python-version }}}}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python ${{{{ matrix.python-version }}}}
        run: uv python install ${{{{ matrix.python-version }}}}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run tests with coverage
        run: uv run pytest --cov={package_name} --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
        env:
          CODECOV_TOKEN: ${{{{ secrets.CODECOV_TOKEN }}}}
'''

    return content


def generate_envrc() -> str:
    """Generate .envrc for direnv support.

    Returns:
        Generated .envrc content.
    """
    return '''# Load variables from .env into the environment.
# Uses direnv's built-in "dotenv" if available, otherwise falls back to manual.
if declare -f dotenv >/dev/null 2>&1; then
  # Loads .env in KEY=VALUE form
  dotenv
else
  # Fallback: POSIX-style loader
  set -a
  [ -f .env ] && . .env
  set +a
fi

# Optional: activate a Python virtualenv if it exists (works great with uv)
if [[ -d .venv ]] && [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi
'''


def generate_pre_commit_config() -> str:
    """Generate .pre-commit-config.yaml.

    Returns:
        Generated pre-commit config content.
    """
    return '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --select=E,F,W,I,N]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        additional_dependencies: ["types-all"]

  - repo: local
    hooks:
      - id: deptry
        name: deptry
        entry: uv run deptry .
        language: system
        always_run: true
        pass_filenames: false
'''


def generate_gitignore() -> str:
    """Generate comprehensive .gitignore.

    Returns:
        Generated .gitignore content.
    """
    return '''# Secrets files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.secrets.yaml

# direnv
.envrc

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Virtual environment
venv/
env/
ENV/
.venv/
.ENV/

# pipenv
Pipfile
Pipfile.lock

# Poetry
poetry.lock
.cache/

# Mypy
pyrightconfig.json
.mypy_cache/

# Unit test / coverage reports
*.cover
.coverage
.coverage.*
.cache
.nox/
nosetests.xml
coverage.xml
*.py,cover
.hypothesis/
.pytest_cache/

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# Jupyter Notebook
.ipynb_checkpoints

# Pyre type checker
.pyre/

# ruff
.ruff_cache/

# IDE and editor settings
.idea/
.vscode/
*.swp
*.swo

# Backup files
*.bak
*.tmp
*.old

# Temporary files
*.~*
*.temp
'''


# =============================================================================
# Migration Steps
# =============================================================================


def create_backup(project_path: Path) -> Path:
    """Create backup of project before migration."""
    import time
    backup_path = project_path.parent / f"{project_path.name}_backup_{int(time.time())}"
    shutil.copytree(project_path, backup_path)
    return backup_path


def migrate_pyproject(
    project_path: Path, analysis: dict, dry_run: bool = False, force: bool = False
) -> list[str]:
    """Migrate or create pyproject.toml."""
    changes = []
    pyproject_path = project_path / "pyproject.toml"

    # Check if pyproject.toml is already modern (using hatchling)
    if pyproject_path.exists() and not force:
        if (analysis["build_backend"] == "hatchling.build" and
            analysis["uses_ruff"] and analysis["uses_black"] and analysis["uses_mypy"]):
            changes.append("pyproject.toml already modern (hatchling) - skipping (use --force to overwrite)")
            return changes

    new_content = generate_pyproject_toml(analysis)

    if dry_run:
        if pyproject_path.exists():
            changes.append("Would update pyproject.toml with modern configuration")
        else:
            changes.append("Would create new pyproject.toml")
        return changes

    # Backup existing if present
    if pyproject_path.exists():
        backup = pyproject_path.with_suffix(".toml.bak")
        shutil.copy(pyproject_path, backup)
        changes.append(f"Backed up existing pyproject.toml to {backup.name}")

    pyproject_path.write_text(new_content)
    changes.append("Created/updated pyproject.toml with modern configuration")

    return changes


def migrate_taskfile(
    project_path: Path, analysis: dict, dry_run: bool = False
) -> list[str]:
    """Create or migrate to Taskfile.yaml."""
    changes = []
    taskfile_path = project_path / "Taskfile.yaml"

    if analysis["has_taskfile"]:
        changes.append("Taskfile already exists - skipping")
        return changes

    new_content = generate_taskfile(analysis, project_path)

    if dry_run:
        changes.append("Would create Taskfile.yaml")
        if analysis["has_makefile"]:
            changes.append("Would deprecate Makefile (rename to Makefile.old)")
        return changes

    taskfile_path.write_text(new_content)
    changes.append("Created Taskfile.yaml")

    # Rename old Makefile if present
    if analysis["has_makefile"]:
        makefile = project_path / "Makefile"
        makefile_old = project_path / "Makefile.old"
        makefile.rename(makefile_old)
        changes.append("Renamed Makefile to Makefile.old")

    return changes


def migrate_github_actions(
    project_path: Path, analysis: dict, dry_run: bool = False, force: bool = False
) -> list[str]:
    """Create or update GitHub Actions workflow."""
    changes = []
    workflows_dir = project_path / ".github" / "workflows"
    ci_path = workflows_dir / "ci.yml"

    # Check if CI is already using modern setup-uv@v4
    if ci_path.exists() and not force:
        ci_content = ci_path.read_text()
        if "setup-uv@v4" in ci_content:
            changes.append("GitHub Actions already uses setup-uv@v4 - skipping (use --force to overwrite)")
            return changes

    new_content = generate_github_actions(analysis)

    if dry_run:
        if analysis["has_github_actions"]:
            changes.append("Would update GitHub Actions CI workflow")
        else:
            changes.append("Would create GitHub Actions CI workflow")
        return changes

    workflows_dir.mkdir(parents=True, exist_ok=True)

    if ci_path.exists():
        backup = ci_path.with_suffix(".yml.bak")
        shutil.copy(ci_path, backup)
        changes.append("Backed up existing ci.yml")

    ci_path.write_text(new_content)
    changes.append("Created/updated GitHub Actions CI workflow with setup-uv@v4")

    return changes


def create_envrc(
    project_path: Path, analysis: dict, dry_run: bool = False
) -> list[str]:
    """Create .envrc for direnv support."""
    changes = []
    envrc_path = project_path / ".envrc"

    if envrc_path.exists():
        changes.append(".envrc already exists - skipping")
        return changes

    if dry_run:
        changes.append("Would create .envrc for direnv support")
        return changes

    envrc_path.write_text(generate_envrc())
    changes.append("Created .envrc for direnv support")

    return changes


def create_pre_commit_config(
    project_path: Path, analysis: dict, dry_run: bool = False
) -> list[str]:
    """Create .pre-commit-config.yaml if not present."""
    changes = []
    config_path = project_path / ".pre-commit-config.yaml"

    if config_path.exists():
        changes.append(".pre-commit-config.yaml already exists - skipping")
        return changes

    if dry_run:
        changes.append("Would create .pre-commit-config.yaml")
        return changes

    config_path.write_text(generate_pre_commit_config())
    changes.append("Created .pre-commit-config.yaml")

    return changes


def update_gitignore(
    project_path: Path, analysis: dict, dry_run: bool = False
) -> list[str]:
    """Update or create .gitignore."""
    changes = []
    gitignore_path = project_path / ".gitignore"

    # Entries to ensure are present
    uv_entries = [
        "# uv",
        ".venv/",
        "uv.lock",
        "",
        "# Task",
        ".task/",
    ]

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        missing_entries = []

        for entry in uv_entries:
            if entry and entry not in content:
                missing_entries.append(entry)

        if missing_entries:
            if dry_run:
                changes.append(f"Would add {len(missing_entries)} entries to .gitignore")
            else:
                content += "\n" + "\n".join(uv_entries) + "\n"
                gitignore_path.write_text(content)
                changes.append("Updated .gitignore with uv and Task entries")
    else:
        if dry_run:
            changes.append("Would create comprehensive .gitignore")
        else:
            gitignore_path.write_text(generate_gitignore())
            changes.append("Created comprehensive .gitignore")

    return changes


def cleanup_old_files(
    project_path: Path, analysis: dict, dry_run: bool = False
) -> list[str]:
    """Remove or archive obsolete files."""
    changes = []
    obsolete_files = [
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements_dev.txt",
        "dev-requirements.txt",
        "MANIFEST.in",
    ]

    archive_dir = project_path / ".migration_archive"

    for file in obsolete_files:
        file_path = project_path / file
        if file_path.exists():
            if dry_run:
                changes.append(f"Would archive obsolete file: {file}")
            else:
                archive_dir.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(archive_dir / file))
                changes.append(f"Archived {file} to .migration_archive/")

    return changes


def create_migration_summary(
    project_path: Path, analysis: dict, changes: list[str], dry_run: bool = False
) -> list[str]:
    """Create a summary of the migration."""
    result_changes = []
    summary_path = project_path / "MIGRATION_SUMMARY.md"

    changes_list = "\n".join(f"- {change}" for change in changes)

    summary_content = f"""# Migration to Modern UV Toolchain

## Migration Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Information
- **Project Name**: {analysis['project_name']}
- **Package Name**: {analysis['package_name']}
- **Version**: {analysis['version']}

## Changes Made
{changes_list}

## New Toolchain

### Package Management
- **uv**: Fast Python package installer and resolver
- Run `uv sync` to install dependencies

### Task Runner
- **Taskfile**: Modern task runner replacing Make
- Run `task --list` to see available tasks

### Code Quality
- **ruff**: Fast Python linter and formatter (replaces black, isort, flake8)
- **mypy**: Static type checking
- **deptry**: Dependency issue detection
- **pre-commit**: Git hooks for code quality

### CI/CD
- **GitHub Actions**: Using `astral-sh/setup-uv@v4`
- Matrix testing: Python 3.11, 3.12

## Quick Start

```bash
# Install dependencies
uv sync

# Set up development environment
task setup

# Run tests
task test

# Run all quality checks
task quality

# Format and fix code
task fix

# Run full CI locally
task ci
```

## Common Tasks

| Task | Command | Description |
|------|---------|-------------|
| Install deps | `uv sync` | Install all dependencies |
| Format code | `task format` | Format with ruff |
| Lint code | `task lint` | Check with ruff |
| Type check | `task typecheck` | Check with mypy |
| Run tests | `task test` | Run pytest |
| Coverage | `task test-cov` | Tests with coverage |
| All checks | `task quality` | Run all quality checks |
| CI pipeline | `task ci` | Full CI pipeline |

## Archived Files

Old configuration files have been moved to `.migration_archive/` for reference.
You can safely delete this directory after verifying the migration.

## Rollback

If needed, restore from backup:
```bash
# Backup was created at: {project_path.name}_backup_*
```
"""

    if dry_run:
        result_changes.append("Would create MIGRATION_SUMMARY.md")
    else:
        summary_path.write_text(summary_content)
        result_changes.append("Created MIGRATION_SUMMARY.md")

    return result_changes


# =============================================================================
# CLI Commands
# =============================================================================


@app.command()
def migrate(
    project_path: Path = typer.Argument(..., help="Path to project to migrate"),
    backup: bool = typer.Option(True, help="Create backup before migration"),
    dry_run: bool = typer.Option(False, help="Preview changes without applying"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update of already-modern files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Migrate a Python project to modern uv-based toolchain."""
    setup_logger(verbose)

    logger.info(f"Analyzing project at {project_path}")

    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        raise typer.Exit(1)

    # Analyze the project
    analysis = analyze_project(project_path)
    show_analysis(analysis)

    if not dry_run and not Confirm.ask("\nProceed with migration?"):
        logger.info("Migration cancelled")
        raise typer.Exit(0)

    if backup and not dry_run:
        backup_path = create_backup(project_path)
        console.print(f"\n[green]✓ Backup created at {backup_path}[/green]")

    # Migration steps - some support force flag
    all_changes = []

    console.print()

    # Steps that support force flag
    force_steps = [
        ("Update pyproject.toml", lambda p, a, d: migrate_pyproject(p, a, d, force=force)),
        ("Setup GitHub Actions", lambda p, a, d: migrate_github_actions(p, a, d, force=force)),
    ]

    # Steps that don't need force flag
    normal_steps = [
        ("Create Taskfile.yaml", migrate_taskfile),
        ("Create .envrc", create_envrc),
        ("Create pre-commit config", create_pre_commit_config),
        ("Update .gitignore", update_gitignore),
        ("Archive old files", cleanup_old_files),
    ]

    for step_name, step_func in force_steps + normal_steps:
        try:
            if dry_run:
                logger.info(f"[DRY RUN] {step_name}")
            else:
                logger.info(f"Executing: {step_name}")

            changes = step_func(project_path, analysis, dry_run)
            all_changes.extend(changes)

            if not dry_run and changes:
                for change in changes:
                    console.print(f"  [green]✓[/green] {change}")

        except Exception as e:
            logger.error(f"Failed: {step_name} - {e}")
            if not dry_run:
                raise

    # Create summary
    summary_changes = create_migration_summary(
        project_path, analysis, all_changes, dry_run=dry_run
    )
    all_changes.extend(summary_changes)

    # Final output
    console.print()
    if dry_run:
        console.print(Panel(
            "\n".join(f"• {c}" for c in all_changes),
            title="[yellow]Planned Changes (Dry Run)[/yellow]",
            border_style="yellow",
        ))
        console.print(f"\n[yellow]Total planned changes: {len(all_changes)}[/yellow]")
        console.print("\nRun without --dry-run to apply changes.")
    else:
        console.print(Panel(
            "[bold green]Migration completed successfully![/bold green]\n\n"
            "Next steps:\n"
            "1. Run [cyan]uv sync[/cyan] to install dependencies\n"
            "2. Run [cyan]task setup[/cyan] to set up development environment\n"
            "3. Run [cyan]task test[/cyan] to verify tests pass\n"
            "4. Review MIGRATION_SUMMARY.md for details",
            title="Success",
            border_style="green",
        ))


@app.command()
def check(
    project_path: Path = typer.Argument(..., help="Path to project to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Analyze a project and check if migration is needed."""
    setup_logger(verbose)

    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        raise typer.Exit(1)

    analysis = analyze_project(project_path)
    show_analysis(analysis)

    # Determine migration needs
    needs_migration = []
    already_modern = []

    # Check pyproject.toml and build backend
    if not analysis["has_pyproject"]:
        needs_migration.append("No pyproject.toml - will be created")
    elif analysis["build_backend"] == "hatchling.build":
        already_modern.append("pyproject.toml uses hatchling")
    else:
        needs_migration.append(f"Build backend is {analysis['build_backend']} - will migrate to hatchling")

    # Check Taskfile
    if not analysis["has_taskfile"]:
        needs_migration.append("No Taskfile - will be created")
    else:
        already_modern.append("Taskfile already present")

    # Check code quality tools
    if not analysis["uses_ruff"]:
        needs_migration.append("Ruff not configured - will be added")
    else:
        already_modern.append("Ruff configured")

    if not analysis["uses_black"]:
        needs_migration.append("Black not configured - will be added")
    else:
        already_modern.append("Black configured")

    if not analysis["uses_mypy"]:
        needs_migration.append("Mypy not configured - will be added")
    else:
        already_modern.append("Mypy configured")

    # Check pre-commit
    if not analysis["uses_pre_commit"]:
        needs_migration.append("Pre-commit not configured - will be created")
    else:
        already_modern.append("Pre-commit configured")

    # Check .envrc
    envrc_path = project_path / ".envrc"
    if not envrc_path.exists():
        needs_migration.append("No .envrc - will be created for direnv support")
    else:
        already_modern.append(".envrc present")

    # Check GitHub Actions
    if not analysis["has_github_actions"]:
        needs_migration.append("No GitHub Actions - will be created")
    else:
        # Check if CI uses modern setup-uv
        ci_path = project_path / ".github" / "workflows" / "ci.yml"
        if ci_path.exists():
            ci_content = ci_path.read_text()
            if "setup-uv@v4" in ci_content:
                already_modern.append("GitHub Actions uses setup-uv@v4")
            elif "setup-uv" in ci_content:
                needs_migration.append("GitHub Actions uses older setup-uv - will be updated")
            else:
                needs_migration.append("GitHub Actions doesn't use uv - will be updated")
        else:
            already_modern.append("GitHub Actions present")

    # Check for legacy files
    legacy_files = ["setup.py", "setup.cfg", "requirements.txt", "MANIFEST.in"]
    found_legacy = [f for f in legacy_files if (project_path / f).exists()]
    if found_legacy:
        needs_migration.append(f"Legacy files found: {', '.join(found_legacy)} - will be archived")

    console.print()
    if already_modern:
        console.print("[bold green]Already Modern:[/bold green]")
        for item in already_modern:
            console.print(f"  ✓ {item}")

    if needs_migration:
        console.print("\n[bold yellow]Migration Needed:[/bold yellow]")
        for item in needs_migration:
            console.print(f"  • {item}")
        console.print(f"\n[cyan]Run 'python migrate_to_uv.py migrate {project_path}' to proceed.[/cyan]")
        console.print("[dim]Use --dry-run to preview changes first.[/dim]")
    else:
        console.print("\n[green]✓ Project is fully up-to-date with modern toolchain![/green]")


if __name__ == "__main__":
    app()
