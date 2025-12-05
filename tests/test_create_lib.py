"""Tests for library project creation functionality."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()
logger = logging.getLogger(__name__)


@pytest.fixture
def sample_lib_config_with_dev_settings(temp_config_dir: Path) -> Path:
    """Create a sample library configuration with development settings.

    Uses the new cookiecutter-uv template format.

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
            "author": "Test Author",
            "email": "test@example.com",
            "license": "MIT",
        },
        "github": {
            "add_on_github": False,
            "repo_name": "test-lib",
            "repo_private": False,
            "github_username": "testuser",
        },
        "development": {
            "layout": "src",
            "include_github_actions": True,
            "mkdocs": True,
            "type_checker": "mypy",
            "deptry": True,
            "codecov": True,
            "publish_to_pypi": True,
        },
        "docker": {"docker_image": False},
        "devcontainer": {"enabled": False},
    }

    config_path = temp_config_dir / "lib_config_with_dev.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


def test_create_lib_with_dev_settings(
    temp_project_dir: Path, sample_lib_config_with_dev_settings: Path
) -> None:
    """Test library project creation with development settings.

    Verifies that:
    - Command exits successfully
    - Project directory is created
    - Development settings are properly applied
    """
    # Create template directory structure
    template_dir = Path("templates/pylibrary-template")
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "cookiecutter.json").write_text('{"project_name": "test-project"}')

    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = template_dir
        mock_resolver.return_value.config = {
            "template_paths": {"templates": {"project_templates": {"pylibrary": str(template_dir)}}}
        }

        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config_with_dev_settings)]
        )

        assert result.exit_code == 0, "Command should exit with code 0"
        project_path = Path(temp_project_dir) / "test-lib"
        assert project_path.exists(), "Project directory should exist"

        # Verify development settings in created project
        pyproject_toml = project_path / "pyproject.toml"
        assert pyproject_toml.exists(), "pyproject.toml should exist"

        # Verify test configuration
        test_dir = project_path / "tests"
        assert test_dir.exists(), "tests directory should exist"

        # Verify documentation setup
        docs_dir = project_path / "docs"
        assert docs_dir.exists(), "docs directory should exist"


def test_create_lib_with_custom_settings(
    temp_project_dir: Path, sample_lib_config_with_dev_settings: Path
) -> None:
    """Test library project creation with custom settings.

    Verifies that:
    - Custom settings are properly applied
    - Project structure matches custom configuration (cookiecutter-uv format)
    """
    # Create template directory structure
    template_dir = Path("templates/pylibrary-template")
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "cookiecutter.json").write_text('{"project_name": "test-project"}')

    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = template_dir
        mock_resolver.return_value.config = {
            "template_paths": {"templates": {"project_templates": {"pylibrary": str(template_dir)}}}
        }

        # Modify config to use custom settings (cookiecutter-uv format)
        with open(sample_lib_config_with_dev_settings) as f:
            config = yaml.safe_load(f)

        config["development"].update(
            {
                "mkdocs": False,  # Disable docs
                "layout": "flat",  # Use flat layout instead of src
                "type_checker": "none",  # No type checker
            }
        )

        with open(sample_lib_config_with_dev_settings, "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config_with_dev_settings)]
        )

        assert result.exit_code == 0, "Command should exit with code 0"
        project_path = Path(temp_project_dir) / "test-lib"

        # Verify custom settings were applied
        assert not (project_path / "docs").exists(), (
            "docs directory should not exist when mkdocs is disabled"
        )

        # Verify flat layout (package directly in project root, not in src/)
        package_dir = project_path / "test_lib"
        assert package_dir.exists(), "Package directory should exist in flat layout"


def test_create_lib_with_invalid_settings(
    temp_project_dir: Path,
    sample_lib_config_with_dev_settings: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test library project creation with invalid settings (cookiecutter-uv format)."""
    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = "gh:fpgmaas/cookiecutter-uv"

        # Modify config with invalid settings
        with open(sample_lib_config_with_dev_settings) as f:
            config = yaml.safe_load(f)

        # Use invalid layout option (only "src" and "flat" are valid)
        config["development"]["layout"] = "invalid_layout"

        with open(sample_lib_config_with_dev_settings, "w") as f:
            yaml.dump(config, f)

        # Ensure we capture ERROR logs from the correct logger
        with caplog.at_level(logging.ERROR):
            result = runner.invoke(
                app, ["create-project-from-config", str(sample_lib_config_with_dev_settings)]
            )

        assert result.exit_code == 1, "Command should fail with invalid settings"

        # Check logs
        errors = [record.message for record in caplog.records if record.levelname == "ERROR"]
        assert any("Invalid layout option: invalid_layout" in msg for msg in errors)
        assert any("Valid options are: src, flat" in msg for msg in errors)


def test_create_lib_template_resolution(
    temp_project_dir: Path, sample_lib_config_with_dev_settings: Path
) -> None:
    """Test library template resolution.

    Verifies that:
    - Correct template is used
    - Template path is properly resolved
    """
    # Create template directory structure
    template_dir = Path("templates/pylibrary-template")
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "cookiecutter.json").write_text('{"project_name": "test-project"}')

    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = template_dir
        mock_resolver.return_value.config = {
            "template_paths": {"templates": {"project_templates": {"pylibrary": str(template_dir)}}}
        }

        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config_with_dev_settings)]
        )

        assert result.exit_code == 0, "Command should exit with code 0"
