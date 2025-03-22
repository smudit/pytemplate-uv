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
            "author": "Test Author",
            "email": "test@example.com",
            "version": "0.1.0",
            "license": "MIT",
        },
        "github": {
            "add_on_github": False,
            "repo_name": "test-lib",
            "repo_private": False,
            "github_username": "testuser",
        },
        "development": {
            "use_pytest": True,
            "test_matrix_separate_coverage": False,
            "test_matrix_configurator": False,
            "use_sphinx": True,
            "sphinx_theme": "sphinx-rtd-theme",
            "sphinx_doctest": False,
            "sphinx_docs_hosting": "readthedocs.io",
            "use_black": True,
            "use_ruff": True,
            "use_mypy": True,
            "use_pre_commit": True,
            "use_codecov": True,
            "use_coveralls": False,
            "use_scrutinizer": False,
            "use_codacy": False,
            "use_codeclimate": False,
            "command_line_interface": "no",
            "command_line_bin_name": "",
            "pypi_badge": True,
            "pypi_disable_upload": False,
        },
        "docker": {"docker_image": False, "docker_compose": False},
        "devcontainer": {"enabled": False},
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
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
    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = (
            "gh:ionelmc/cookiecutter-pylibrary"
        )

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
    - Project structure matches custom configuration
    """
    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = (
            "gh:ionelmc/cookiecutter-pylibrary"
        )

        # Modify config to use custom settings
        with open(sample_lib_config_with_dev_settings) as f:
            config = yaml.safe_load(f)

        config["development"].update(
            {
                "use_sphinx": False,
                "use_black": False,
                "use_ruff": False,
                "command_line_interface": "click",
                "command_line_bin_name": "mycli",
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
        assert not (
            project_path / "docs"
        ).exists(), "docs directory should not exist when sphinx is disabled"

        # Verify CLI setup
        cli_file = project_path / "src" / "test_lib" / "cli.py"
        assert cli_file.exists(), "CLI file should exist when command_line_interface is set"


def test_create_lib_with_invalid_settings(
    temp_project_dir: Path,
    sample_lib_config_with_dev_settings: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test library project creation with invalid settings."""
    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = (
            "gh:ionelmc/cookiecutter-pylibrary"
        )

        # Modify config with invalid settings
        with open(sample_lib_config_with_dev_settings) as f:
            config = yaml.safe_load(f)

        config["development"]["command_line_interface"] = "invalid_option"

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
        assert any("Invalid command line interface option: invalid_option" in msg for msg in errors)
        assert any("Valid options are: no, click, argparse, plain" in msg for msg in errors)


def test_create_lib_template_resolution(
    temp_project_dir: Path, sample_lib_config_with_dev_settings: Path
) -> None:
    """Test library template resolution.

    Verifies that:
    - Correct template is used
    - Template path is properly resolved
    """
    with mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
        mock_resolver.return_value.get_template_path.return_value = (
            "gh:ionelmc/cookiecutter-pylibrary"
        )

        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config_with_dev_settings)]
        )

        assert result.exit_code == 0, "Command should exit with code 0"
        mock_resolver.return_value.get_template_path.assert_called_with(
            "project_templates", "pylibrary"
        )
