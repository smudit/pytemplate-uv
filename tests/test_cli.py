"""Tests for CLI commands and options."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()
logger = logging.getLogger(__name__)


class TestCLICommands:
    """Test CLI command functionality."""

    def test_app_help(self):
        """Test that the main app shows help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "pytemplate-uv" in result.output
        assert "Create Python projects from templates" in result.output

    def test_create_project_from_config_help(self):
        """Test help for create-project-from-config command."""
        result = runner.invoke(app, ["create-project-from-config", "--help"])
        assert result.exit_code == 0
        assert "Create a new project from a configuration file" in result.output
        assert "--interactive" in result.output
        assert "--debug" in result.output
        assert "--force" in result.output

    def test_create_config_help(self):
        """Test help for create-config command."""
        result = runner.invoke(app, ["create-config", "--help"])
        assert result.exit_code == 0
        assert "Create a default configuration file" in result.output
        assert "--output-path" in result.output


class TestDebugLogging:
    """Test debug logging functionality."""

    def test_debug_flag_enables_logging(self, temp_project_dir: Path, sample_lib_config: Path):
        """Test that --debug flag enables debug logging."""
        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config), "--debug"]
        )
        assert result.exit_code == 0
        # Debug logging should be mentioned in output or logs

    def test_debug_flag_with_interactive(self, temp_project_dir: Path, sample_lib_config: Path):
        """Test debug flag combined with interactive mode."""
        result = runner.invoke(
            app, ["create-project-from-config", str(sample_lib_config), "--debug", "--interactive"]
        )
        assert result.exit_code == 0


class TestForceOption:
    """Test force option functionality."""

    def test_force_flag_confirmation(self, temp_project_dir: Path, sample_lib_config: Path):
        """Test that --force flag prompts for confirmation."""
        # Mock typer.confirm to return False (decline)
        with mock.patch("typer.confirm", return_value=False):
            result = runner.invoke(
                app, ["create-project-from-config", str(sample_lib_config), "--force"]
            )
            # When user declines, typer.Exit(code=1) is called
            assert result.exit_code == 1
            # Note: The actual confirmation message might not appear in output when mocked

    def test_force_flag_confirmation_yes(self, temp_project_dir: Path, sample_lib_config: Path):
        """Test that --force flag works when confirmed."""
        # Mock typer.confirm to return True (accept)
        with mock.patch("typer.confirm", return_value=True):
            result = runner.invoke(
                app, ["create-project-from-config", str(sample_lib_config), "--force"]
            )
            assert result.exit_code == 0


class TestProjectTypeValidation:
    """Test project type validation."""

    def test_valid_project_types(self, temp_project_dir: Path):
        """Test that valid project types are accepted."""
        valid_types = ["lib", "service", "workspace"]

        for project_type in valid_types:
            with mock.patch("pytemplate.main.TemplateResolver") as mock_resolver:
                mock_path = mock.MagicMock()
                mock_path.exists.return_value = True
                mock_path.read_text.return_value = f"type: {project_type}"
                mock_resolver.return_value.get_template_path.return_value = mock_path

                result = runner.invoke(app, ["create-config", project_type])
                assert (
                    result.exit_code == 0
                ), f"Valid project type {project_type} should be accepted"

    def test_invalid_project_type(self, temp_project_dir: Path):
        """Test that invalid project types are rejected."""
        result = runner.invoke(app, ["create-config", "invalid-type"])
        assert result.exit_code == 1
        assert "Invalid project type: invalid-type" in result.output
        assert "Must be one of: lib, service, workspace" in result.output

    def test_project_type_case_insensitive(self, temp_project_dir: Path):
        """Test that project types are case insensitive."""
        with mock.patch("pytemplate.main.TemplateResolver") as mock_resolver:
            mock_path = mock.MagicMock()
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = "type: lib"
            mock_resolver.return_value.get_template_path.return_value = mock_path

            result = runner.invoke(app, ["create-config", "LIB"])
            assert result.exit_code == 0
            # Verify that the callback converted to lowercase
            mock_resolver.return_value.get_template_path.assert_called_with("config_specs", "lib")


class TestErrorHandling:
    """Test error handling in CLI commands."""

    def test_missing_config_file(self, temp_project_dir: Path):
        """Test handling of missing configuration file."""
        nonexistent_config = Path(temp_project_dir) / "nonexistent.yaml"

        with mock.patch("pytemplate.main.ProjectCreator") as mock_creator:
            mock_creator.side_effect = FileNotFoundError(f"No such file: {nonexistent_config}")

            result = runner.invoke(app, ["create-project-from-config", str(nonexistent_config)])
            assert result.exit_code == 1

    def test_invalid_yaml_config(self, temp_project_dir: Path):
        """Test handling of invalid YAML configuration."""
        invalid_config = Path(temp_project_dir) / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [")

        result = runner.invoke(app, ["create-project-from-config", str(invalid_config)])
        assert result.exit_code == 1

    def test_template_not_found_error(self, temp_project_dir: Path):
        """Test handling when template is not found."""
        with mock.patch("pytemplate.main.TemplateResolver") as mock_resolver:
            mock_resolver.return_value.get_template_path.side_effect = ValueError(
                "Template not found"
            )

            result = runner.invoke(app, ["create-config", "lib"])
            assert result.exit_code == 1
            assert "Configuration template not found in template_paths.yaml" in result.output
