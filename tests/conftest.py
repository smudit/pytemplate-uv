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
        "project_type": "lib",
        "name": "test-lib",
        "description": "Test library project",
        "author": "Test Author",
        "python_version": "3.9",
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
    config = {
        "template_paths": {
            "templates": {
                "python": {
                    "pyproject": str(temp_templates_dir / "pyproject-template"),
                    "fastapi": str(temp_templates_dir / "fastapi-template"),
                }
            }
        }
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
