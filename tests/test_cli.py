"""Tests for the pytemplate-uv CLI."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()
logger = logging.getLogger(__name__)


# create-project-cli command tests
def test_create_project_cli_basic(temp_project_dir: Path) -> None:
    """Test basic project creation with default template.

    Verifies that:
    - Command exits successfully
    - Project directory is created
    - pyproject.toml file exists in project directory
    """
    result = runner.invoke(app, ["create-project-cli", "test-project"])

    assert result.exit_code == 0, "Command should exit with code 0"
    assert Path(temp_project_dir, "test-project").exists(), "Project directory should exist"
    assert Path(
        temp_project_dir, "test-project", "pyproject.toml"
    ).exists(), "pyproject.toml should exist"


def test_create_project_cli_with_template(temp_project_dir: Path) -> None:
    """Test project creation with specific template.

    Verifies that:
    - Command exits successfully with template flag
    - Project directory is created with correct name
    - pyproject.toml exists in template-specific project
    """
    result = runner.invoke(app, ["create-project-cli", "test-fastapi", "--template", "fastapi"])

    assert result.exit_code == 0, "Command should exit with code 0"
    project_dir = Path(temp_project_dir, "test-fastapi")
    assert project_dir.exists(), "Project directory should exist"
    assert (
        project_dir / "pyproject.toml"
    ).exists(), "pyproject.toml should exist in template project"


def test_create_project_cli_no_input(temp_project_dir: Path) -> None:
    """Test project creation with --no-input flag.

    Verifies that:
    - Command exits successfully in non-interactive mode
    - Project directory is created without user input
    - pyproject.toml exists in non-interactive project
    """
    result = runner.invoke(app, ["create-project-cli", "test-project", "--no-input"])

    assert result.exit_code == 0, "Command should exit with code 0 in non-interactive mode"
    assert Path(
        temp_project_dir, "test-project"
    ).exists(), "Project directory should exist without input"
    assert Path(
        temp_project_dir, "test-project", "pyproject.toml"
    ).exists(), "pyproject.toml should exist in non-interactive project"


def test_create_project_cli_force_confirm(temp_project_dir: Path) -> None:
    """Test project creation with --force flag and confirmation.

    Verifies that:
    - Command exits successfully when confirming overwrite
    - User is prompted for confirmation
    - Project is successfully overwritten
    """
    # Create project first time
    runner.invoke(app, ["create-project-cli", "test-project"])

    # Try to create again with force
    result = runner.invoke(
        app,
        ["create-project-cli", "test-project", "--force"],
        input="y\n",  # Confirm overwrite
    )

    assert result.exit_code == 0, "Command should exit with code 0 when confirming overwrite"
    assert (
        "Are you sure you want to overwrite" in result.output
    ), "User should be prompted for confirmation"
    assert Path(temp_project_dir, "test-project").exists(), "Project should exist after overwrite"


def test_create_project_cli_force_cancel(temp_project_dir: Path) -> None:
    """Test project creation with --force flag but cancelled.

    Verifies that:
    - Command exits successfully when cancelling overwrite
    - User is prompted for confirmation
    - Operation is cancelled and project is not overwritten
    """
    # Create project first time
    runner.invoke(app, ["create-project-cli", "test-project"])

    # Try to create again with force but cancel
    result = runner.invoke(
        app,
        ["create-project-cli", "test-project", "--force"],
        input="n\n",  # Cancel overwrite
    )

    assert result.exit_code == 0, "Command should exit with code 0 when cancelling"
    assert "Operation cancelled" in result.output, "Operation should be cancelled"
    assert Path(temp_project_dir, "test-project").exists(), "Original project should still exist"


# create-project-from-config command tests
def test_create_project_from_config(temp_project_dir: Path, sample_lib_config: Path) -> None:
    """Test project creation from config file.

    Verifies that:
    - Command exits successfully when using config file
    - Project creation completion message is shown
    - Project directory is created
    """
    result = runner.invoke(app, ["create-project-from-config", str(sample_lib_config)])

    assert result.exit_code == 0, "Command should exit with code 0 when using config"
    assert "Project creation completed" in result.output, "Completion message should be shown"
    assert Path(temp_project_dir).exists(), "Project directory should exist"


def test_create_project_from_config_interactive(
    temp_project_dir: Path, sample_lib_config: Path
) -> None:
    """Test project creation from config file in interactive mode.

    Verifies that:
    - Command exits successfully in interactive mode
    - Project directory is created
    - Interactive mode completes without errors
    """
    result = runner.invoke(
        app, ["create-project-from-config", str(sample_lib_config), "--interactive"]
    )

    assert result.exit_code == 0, "Command should exit with code 0 in interactive mode"
    assert Path(temp_project_dir).exists(), "Project directory should exist in interactive mode"


def test_create_project_from_config_invalid_path(temp_project_dir: Path) -> None:
    """Test project creation with invalid config path.

    Verifies that:
    - Command fails with invalid config path
    - Appropriate error code is returned
    - Error message is shown
    """
    result = runner.invoke(app, ["create-project-from-config", "nonexistent.yaml"])

    assert result.exit_code == 1, "Command should fail with invalid config path"
    assert "Error" in result.output, "Error message should be shown"
    assert not Path(
        temp_project_dir, "nonexistent.yaml"
    ).exists(), "Invalid config should not exist"


# create-config command tests
@pytest.mark.parametrize("project_type", ["lib", "service", "workspace"])
def test_create_config_valid_types(temp_project_dir: Path, project_type: str) -> None:
    """Test config creation for valid project types.

    Verifies that:
    - Command exits successfully for valid project types
    - Config file is created
    - Config file contains expected content
    """
    result = runner.invoke(app, ["create-config", project_type])

    assert result.exit_code == 0, "Command should exit with code 0 for valid project types"
    config_path = Path(temp_project_dir, "project_config.yaml")
    assert config_path.exists(), "Config file should exist"

    # Verify config contains expected project type
    with open(config_path) as f:
        config = yaml.safe_load(f)
        assert config["project_type"] == project_type, "Config should contain correct project type"


def test_create_config_invalid_type(temp_project_dir: Path) -> None:
    """Test config creation with invalid project type.

    Verifies that:
    - Command fails with invalid project type
    - Appropriate error code is returned
    - Error message is shown
    - No config file is created
    """
    result = runner.invoke(app, ["create-config", "invalid-type"])

    assert result.exit_code == 1, "Command should fail with invalid project type"
    assert "Invalid project type" in result.output, "Error message should be shown"
    assert not Path(
        temp_project_dir, "project_config.yaml"
    ).exists(), "Config file should not be created for invalid type"


def test_create_config_custom_output(temp_project_dir: Path) -> None:
    """Test config creation with custom output path.

    Verifies that:
    - Command exits successfully with custom output path
    - Config file is created at specified location
    - Config file contains valid content
    """
    output_path = "custom_config.yaml"
    result = runner.invoke(app, ["create-config", "lib", "--output-path", output_path])

    assert result.exit_code == 0, "Command should exit with code 0 with custom output path"
    config_path = Path(temp_project_dir, output_path)
    assert config_path.exists(), "Config file should exist at custom location"

    # Verify config contains expected project type
    with open(config_path) as f:
        config = yaml.safe_load(f)
        assert config["project_type"] == "lib", "Config should contain correct project type"


# templates init command tests
def test_templates_init_default(temp_project_dir: Path) -> None:
    """Test template initialization with default base directory.

    Verifies that:
    - Command exits successfully for default initialization
    - Success message is shown
    - Template directory structure is created
    """
    result = runner.invoke(app, ["templates", "init"])

    assert result.exit_code == 0, "Command should exit with code 0 for default initialization"
    assert (
        "Template directory structure initialized successfully" in result.output
    ), "Success message should be shown"
    assert Path(temp_project_dir, "templates").exists(), "Template directory should exist"
    assert Path(
        temp_project_dir, "templates", "template_paths.yaml"
    ).exists(), "Template config file should exist"


def test_templates_init_custom_dir(temp_project_dir: Path, temp_templates_dir: Path) -> None:
    """Test template initialization with custom base directory.

    Verifies that:
    - Command exits successfully with custom directory
    - Custom directory path is shown in output
    - Template directory structure is created in custom location
    """
    result = runner.invoke(app, ["templates", "init", "--base-dir", str(temp_templates_dir)])

    assert result.exit_code == 0, "Command should exit with code 0 with custom directory"
    assert str(temp_templates_dir) in result.output, "Custom directory path should be shown"
    assert temp_templates_dir.exists(), "Custom template directory should exist"
    assert (
        temp_templates_dir / "template_paths.yaml"
    ).exists(), "Template config should exist in custom directory"


def test_templates_init_invalid_dir(temp_project_dir: Path) -> None:
    """Test template initialization with invalid directory.

    Verifies that:
    - Command fails with invalid directory
    - Appropriate error code is returned
    - Error message is shown
    - No template directory is created
    """
    invalid_dir = "/nonexistent/directory"
    result = runner.invoke(app, ["templates", "init", "--base-dir", invalid_dir])

    assert result.exit_code == 1, "Command should fail with invalid directory"
    assert "Error" in result.output, "Error message should be shown"
    assert not Path(invalid_dir).exists(), "Invalid directory should not exist"


# templates list command tests
def test_templates_list(temp_project_dir: Path, mock_template_config: Path) -> None:
    """Test listing available templates.

    Verifies that:
    - Command exits successfully
    - All expected template categories are listed
    - Output contains valid template names
    - Template count matches expected
    """
    result = runner.invoke(app, ["templates", "list"])

    assert result.exit_code == 0, "Command should exit with code 0"
    assert "python" in result.output, "Python template should be listed"
    assert "pyproject" in result.output, "Pyproject template should be listed"
    assert "fastapi" in result.output, "FastAPI template should be listed"
    assert result.output.count("Template:") >= 3, "Should list at least 3 templates"


def test_templates_list_empty(temp_project_dir: Path) -> None:
    """Test listing templates with empty config.

    Verifies that:
    - Command exits successfully with empty config
    - Empty list message is shown
    - No templates are listed
    - Config file is properly created
    """
    empty_config = Path(temp_project_dir) / "empty_config.yaml"
    with open(empty_config, "w") as f:
        yaml.dump({"template_paths": {"templates": {}}}, f)

    os.environ["TEMPLATE_CONFIG_PATH"] = str(empty_config)
    result = runner.invoke(app, ["templates", "list"])

    assert result.exit_code == 0, "Command should exit with code 0 with empty config"
    assert "No templates found" in result.output, "Empty list message should be shown"
    assert result.output.count("Template:") == 0, "No templates should be listed"
    assert empty_config.exists(), "Empty config file should exist"


# templates copy command tests
def test_templates_copy_all(temp_project_dir: Path, temp_templates_dir: Path) -> None:
    """Test copying all templates.

    Verifies that:
    - Command exits successfully
    - Success message is shown
    - All template files are copied
    - Template directory structure is preserved
    """
    result = runner.invoke(app, ["templates", "copy"])

    assert result.exit_code == 0, "Command should exit with code 0"
    assert "Templates copied successfully" in result.output, "Success message should be shown"
    assert (temp_templates_dir / "python").exists(), "Python template should be copied"
    assert (temp_templates_dir / "pyproject").exists(), "Pyproject template should be copied"
    assert (temp_templates_dir / "fastapi").exists(), "FastAPI template should be copied"


def test_templates_copy_category(temp_project_dir: Path, temp_templates_dir: Path) -> None:
    """Test copying templates for specific category.

    Verifies that:
    - Command exits successfully for specific category
    - Category-specific message is shown
    - Only category-specific files are copied
    - Template directory structure is preserved
    """
    result = runner.invoke(app, ["templates", "copy", "--category", "python"])

    assert result.exit_code == 0, "Command should exit with code 0 for specific category"
    assert (
        "Copying templates for category: python" in result.output
    ), "Category message should be shown"
    assert (temp_templates_dir / "python").exists(), "Python template should be copied"
    assert not (
        temp_templates_dir / "pyproject"
    ).exists(), "Pyproject template should not be copied"
    assert not (temp_templates_dir / "fastapi").exists(), "FastAPI template should not be copied"


def test_templates_copy_invalid_category(temp_project_dir: Path) -> None:
    """Test copying templates with invalid category.

    Verifies that:
    - Command fails with invalid category
    - Appropriate error code is returned
    - Error message is shown
    - No templates are copied
    """
    result = runner.invoke(app, ["templates", "copy", "--category", "invalid"])

    assert result.exit_code == 1, "Command should fail with invalid category"
    assert "Error" in result.output, "Error message should be shown"
    assert not (
        temp_project_dir / "invalid"
    ).exists(), "Invalid category templates should not be copied"


def test_help_command() -> None:
    """Test the help command provides useful information.

    Verifies that:
    - Command exits successfully
    - Application description is shown
    - Common options are listed
    - Command usage is shown
    """
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0, "Command should exit with code 0"
    assert (
        "Create Python projects from templates using uv package manager" in result.output
    ), "Application description should be shown"
    assert "--template" in result.output, "Template option should be listed"
    assert "Usage:" in result.output, "Command usage should be shown"
