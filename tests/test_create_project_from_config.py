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

    # Mock both ProjectCreator and logger
    with (
        mock.patch("pytemplate.main.ProjectCreator") as mock_creator,
        mock.patch("pytemplate.main.logger") as mock_logger,
    ):
        # Configure the mock to raise FileNotFoundError
        mock_creator.return_value.create_project_from_config.side_effect = FileNotFoundError(
            f"[Errno 2] No such file or directory: '{invalid_path}'"
        )

        # Configure logger to capture error messages
        mock_logger.error.return_value = None

        result = runner.invoke(app, ["create-project-from-config", str(invalid_path)])

        assert result.exit_code == 1, "Command should fail with invalid config path"
        assert "Config file not found" in result.output, "Error message should be shown"
        assert not invalid_path.exists(), "Invalid config should not exist"

        # Verify logger was called with error message
        mock_logger.error.assert_called_with(
            f"Config file not found: [Errno 2] No such file or directory: '{invalid_path}'"
        )


def test_create_project_from_config_existing_directory(
    temp_project_dir: Path, sample_lib_config: Path
) -> None:
    """Test project creation when directory already exists.

    Verifies that:
    - User is prompted when directory exists
    - Project is created when user confirms overwrite
    - Project is not created when user declines overwrite
    """
    from unittest import mock
    
    # First create a project to ensure directory exists
    runner.invoke(app, ["create-project-from-config", str(sample_lib_config)])

    # Test when user confirms overwrite
    with mock.patch("typer.confirm", return_value=True):
        result_yes = runner.invoke(
            app,
            ["create-project-from-config", str(sample_lib_config)]
        )

        assert result_yes.exit_code == 0, "Command should succeed when user confirms overwrite"
        assert Path(temp_project_dir).exists()

    # Test when user declines overwrite
    with mock.patch("typer.confirm", return_value=False):
        result_no = runner.invoke(
            app,
            ["create-project-from-config", str(sample_lib_config)]
        )

        assert result_no.exit_code == 1, "Command should exit with code 1 when user declines overwrite"
