"""Pytest configuration and fixtures for pytemplate-uv."""

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def temp_project_dir() -> str:
    """Create a temporary directory for project creation.

    Returns
    -------
        str: Path to the temporary directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)


@pytest.fixture
def project_templates_path() -> Path:
    """Get the path to project templates.

    Returns
    -------
        Path: Path to the templates directory

    """
    return Path(__file__).parent.parent / "templates"


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for configuration files.

    Yields
    ------
        Path: Path to temporary config directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        yield temp_dir


@pytest.fixture
def sample_lib_config(temp_config_dir: Path) -> Path:
    """Create a sample library configuration file.

    Args:
    ----
        temp_config_dir: Temporary directory for config files

    Returns:
    -------
        Path: Path to the sample config file

    """
    config = {
        "project": {
            "type": "lib",
            "name": "test-lib",
            "description": "Test library project",
            "python_version": "3.9",
        },
        "github": {"add_on_github": False, "repo_name": "test-lib", "repo_private": False},
        "docker": {"docker_image": False, "docker_compose": False},
        "devcontainer": {"enabled": False},
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
    }

    config_path = temp_config_dir / "lib_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture
def temp_templates_dir(temp_config_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary templates directory with basic structure.

    Args:
    ----
        temp_config_dir: Temporary directory for templates

    Yields:
    ------
        Path: Path to temporary templates directory

    """
    templates_dir = temp_config_dir / "templates"
    templates_dir.mkdir()

    # Create basic template structure
    (templates_dir / "pyproject-template").mkdir()
    (templates_dir / "fastapi-template").mkdir()
    (templates_dir / "shared").mkdir()

    # Create shared coding rules template
    (templates_dir / "shared" / "coding_rules.md").write_text("""
    # Coding Rules for Tests
    1. Use type hints
    2. Write unit tests
    3. Follow PEP8
    """)

    # Create mock template files instead of using actual cookiecutter templates
    pyproject_dir = templates_dir / "pyproject-template"
    (pyproject_dir / "cookiecutter.json").write_text("""
    {
        "project_name": "test-pyproject",
        "package_name": "test_pyproject",
        "description": "Test PyProject",
        "author": "Test Author",
        "envfile": ".env"
    }
    """)

    # Create the {{cookiecutter.project_name}} directory structure
    cookie_project_dir = pyproject_dir / "{{cookiecutter.project_name}}"
    cookie_project_dir.mkdir(parents=True)

    # Create basic project structure
    (cookie_project_dir / "pyproject.toml").write_text("""
    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "{{cookiecutter.project_name}}"
    version = "0.1.0"
    """)

    # Create package directory
    package_dir = cookie_project_dir / "{{cookiecutter.package_name}}"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("")
    (package_dir / "main.py").write_text("""def main():
        print("Hello from {{cookiecutter.project_name}}")
    """)

    # Create tests directory
    test_dir = cookie_project_dir / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "__init__.py").write_text("")
    (test_dir / "test_main.py").write_text("""def test_placeholder():
        assert True
    """)

    fastapi_dir = templates_dir / "fastapi-template"
    (fastapi_dir / "cookiecutter.json").write_text("""
    {
        "project_name": "test-fastapi",
        "package_name": "test_fastapi",
        "description": "Test FastAPI Project",
        "author": "Test Author",
        "envfile": ".env"
    }
    """)

    # Create the {{cookiecutter.project_name}} directory structure for FastAPI
    fastapi_cookie_dir = fastapi_dir / "{{cookiecutter.project_name}}"
    fastapi_cookie_dir.mkdir(parents=True)

    # Create basic FastAPI project structure
    (fastapi_cookie_dir / "pyproject.toml").write_text("""
    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "{{cookiecutter.project_name}}"
    version = "0.1.0"
    
    [dependencies]
    fastapi = "^0.95.0"
    """)

    # Create package directory for FastAPI
    fastapi_package_dir = fastapi_cookie_dir / "{{cookiecutter.package_name}}"
    fastapi_package_dir.mkdir(parents=True)
    (fastapi_package_dir / "__init__.py").write_text("")
    (fastapi_package_dir / "main.py").write_text("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
    """)

    # Create tests directory for FastAPI
    fastapi_test_dir = fastapi_cookie_dir / "tests"
    fastapi_test_dir.mkdir(parents=True)
    (fastapi_test_dir / "__init__.py").write_text("")
    (fastapi_test_dir / "test_api.py").write_text("""def test_placeholder():
        assert True
    """)

    yield templates_dir

    # Cleanup
    if templates_dir.exists():
        shutil.rmtree(templates_dir)


@pytest.fixture
def mock_template_config(temp_templates_dir: Path) -> Path:
    """Create a mock template configuration file.

    Args:
    ----
        temp_templates_dir: Temporary templates directory

    Returns:
    -------
        Path: Path to the mock config file

    """
    # Use the actual structure from template_paths.yaml
    config = {
        "config_templates": {
            "lib": str(temp_templates_dir / "configs/lib.yaml.template"),
            "service": str(temp_templates_dir / "configs/service.yaml.template"),
            "workspace": str(temp_templates_dir / "configs/workspace.yaml.template"),
        },
        "shared": str(temp_templates_dir / "shared"),
    }

    config_path = temp_templates_dir / "template_paths.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture(autouse=True)
def setup_environment(temp_project_dir: str, mock_template_config: Path) -> None:
    """Set up environment variables for testing.

    Args:
    ----
        temp_project_dir: Temporary directory for project
        mock_template_config: Path to mock template config

    """
    os.environ["TEMPLATE_CONFIG_PATH"] = str(mock_template_config)
    os.environ["PROJECT_BASE_DIR"] = temp_project_dir


@pytest.fixture(autouse=True)
def mock_cookiecutter(monkeypatch):
    """Mock cookiecutter function for testing."""

    def mock_cookie(*args, **kwargs):
        """Create a simple directory structure for testing."""
        output_dir = kwargs.get("output_dir", ".")
        project_name = kwargs.get("extra_context", {}).get("project_name", "test-project")

        # Create output directory
        project_path = Path(output_dir) / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create basic project structure
        (project_path / "pyproject.toml").write_text(
            f'[project]\nname = "{project_name}"\nversion = "0.1.0"\n'
        )

        # Create package directory with the same name
        package_name = project_name.replace("-", "_")
        package_path = project_path / package_name
        package_path.mkdir(parents=True, exist_ok=True)
        (package_path / "__init__.py").write_text("")
        (package_path / "main.py").write_text("def main():\n    print('Hello World')\n")

        # Create tests directory
        test_path = project_path / "tests"
        test_path.mkdir(parents=True, exist_ok=True)
        (test_path / "__init__.py").write_text("")
        (test_path / "test_main.py").write_text("def test_main():\n    assert True\n")

        return str(project_path)

    # Replace cookiecutter with our mock version
    monkeypatch.setattr("pytemplate.project_creator.cookiecutter", mock_cookie)
