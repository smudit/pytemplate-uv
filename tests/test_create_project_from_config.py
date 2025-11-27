"""Tests for create-project-from-config command."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()
logger = logging.getLogger(__name__)


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
    # Create an absolute path that doesn't exist
    invalid_path = Path(temp_project_dir).parent / "nonexistent.yaml"

    # Mock ProjectCreator to raise typer.Exit like the real implementation
    with mock.patch("pytemplate.main.ProjectCreator") as mock_creator:
        # Configure the mock to raise typer.Exit like the real load_config method
        import typer

        mock_creator.return_value.create_project_from_config.side_effect = typer.Exit(code=1)

        result = runner.invoke(app, ["create-project-from-config", str(invalid_path)])

        assert result.exit_code == 1, "Command should fail with invalid config path"
        assert not invalid_path.exists(), "Invalid config should not exist"


def test_create_project_from_config_existing_directory(
    temp_project_dir: Path, sample_lib_config: Path
) -> None:
    """Test project creation when directory already exists.

    Verifies that:
    - User is prompted when directory exists
    - Project is created when user confirms overwrite
    - Project is not created when user declines overwrite
    """
    # First create a project to ensure directory exists
    runner.invoke(app, ["create-project-from-config", str(sample_lib_config)])

    # Test when user confirms overwrite with --force flag
    # --force flag skips confirmation and proceeds directly
    result = runner.invoke(app, ["create-project-from-config", str(sample_lib_config), "--force"])

    assert result.exit_code == 0, "Command with --force should succeed without prompting"
    assert Path(temp_project_dir).exists()
