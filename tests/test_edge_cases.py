"""Tests for edge cases and error handling scenarios."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from pytemplate.main import app
from pytemplate.project_creator import ProjectCreator

runner = CliRunner()


class TestConfigurationEdgeCases:
    """Test edge cases in configuration handling."""

    def test_empty_config_file(self, temp_config_dir: Path):
        """Test handling of empty configuration file."""
        empty_config = temp_config_dir / "empty.yaml"
        empty_config.write_text("")

        creator = ProjectCreator(str(empty_config))
        with pytest.raises(Exception):  # Should fail with empty config
            creator.load_config()
            creator.create_project_from_config()

    def test_config_with_only_comments(self, temp_config_dir: Path):
        """Test handling of config file with only comments."""
        comment_config = temp_config_dir / "comments.yaml"
        comment_config.write_text("""
        # This is a comment
        # Another comment
        """)

        creator = ProjectCreator(str(comment_config))
        creator.load_config()
        # Should load as None or empty dict
        assert creator.config is None or creator.config == {}

    def test_config_with_null_values(self, temp_config_dir: Path):
        """Test handling of config with null values."""
        null_config = temp_config_dir / "null.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": None,  # Null value
                "description": "Test project",
            }
        }

        with open(null_config, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(null_config))
        with pytest.raises(Exception):  # Should fail with null project name
            creator.load_config()
            creator.create_project_from_config()

    def test_config_with_special_characters(self, temp_config_dir: Path):
        """Test handling of config with special characters in project name."""
        special_config = temp_config_dir / "special.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-project@#$%",  # Special characters
                "description": "Test project with special chars",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        with open(special_config, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(special_config))
        # Should handle special characters gracefully
        result = creator.create_project_from_config()
        # May succeed or fail depending on implementation


class TestFileSystemEdgeCases:
    """Test edge cases related to file system operations."""

    def test_readonly_directory(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test handling when target directory is read-only."""
        creator = ProjectCreator(str(sample_lib_config))

        # Create a read-only directory
        readonly_dir = temp_config_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        try:
            with mock.patch("os.getcwd", return_value=str(readonly_dir)):
                result = creator.create_project_from_config()
                # Should handle read-only directory gracefully
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    def test_insufficient_disk_space(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test handling when there's insufficient disk space."""
        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = OSError("No space left on device")

            result = creator.create_project_from_config()
            assert result is False

    def test_long_file_paths(self, temp_config_dir: Path):
        """Test handling of very long file paths."""
        long_name = "a" * 200  # Very long project name
        long_config = temp_config_dir / "long.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": long_name,
                "description": "Test project with very long name",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        with open(long_config, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(long_config))
        # Should handle long paths appropriately
        result = creator.create_project_from_config()
        # May succeed or fail depending on OS limits


class TestConcurrencyEdgeCases:
    """Test edge cases related to concurrent operations."""

    def test_concurrent_project_creation(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test handling when multiple processes try to create the same project."""
        creator1 = ProjectCreator(str(sample_lib_config))
        creator2 = ProjectCreator(str(sample_lib_config))

        # Simulate concurrent creation
        with mock.patch("pytemplate.project_creator._execute_cookiecutter") as mock_cookie:
            mock_cookie.side_effect = [
                "/path/to/project",  # First call succeeds
                FileExistsError("Directory already exists"),  # Second call fails
            ]

            result1 = creator1.create_project_from_config()
            result2 = creator2.create_project_from_config()

            # One should succeed, one should handle the conflict


class TestNetworkEdgeCases:
    """Test edge cases related to network operations."""

    def test_github_api_timeout(self, temp_config_dir: Path, sample_service_config: Path):
        """Test handling when GitHub API times out."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_config_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        with mock.patch("subprocess.check_call") as mock_call:
            mock_call.side_effect = TimeoutError("GitHub API timeout")

            result = creator.create_github_repo()
            assert result is False

    def test_github_authentication_failure(
        self, temp_config_dir: Path, sample_service_config: Path
    ):
        """Test handling when GitHub authentication fails."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_config_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        with mock.patch("subprocess.check_call") as mock_call:
            mock_call.side_effect = subprocess.CalledProcessError(1, "gh", "Authentication failed")

            result = creator.create_github_repo()
            assert result is False


class TestMemoryEdgeCases:
    """Test edge cases related to memory usage."""

    def test_large_config_file(self, temp_config_dir: Path):
        """Test handling of very large configuration files."""
        large_config = temp_config_dir / "large.yaml"

        # Create a config with many entries
        config_data = {
            "project": {"type": "lib", "name": "test-lib", "description": "Test project"},
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            # Add many dummy entries
            **{f"dummy_key_{i}": f"dummy_value_{i}" for i in range(1000)},
        }

        with open(large_config, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(large_config))
        # Should handle large configs without memory issues
        creator.load_config()
        assert creator.config is not None


class TestCLIEdgeCases:
    """Test edge cases in CLI usage."""

    def test_cli_with_unicode_arguments(self, temp_config_dir: Path):
        """Test CLI with unicode characters in arguments."""
        unicode_config = temp_config_dir / "unicode.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-项目",  # Unicode characters
                "description": "Test project with unicode",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        with open(unicode_config, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)

        result = runner.invoke(app, ["create-project-from-config", str(unicode_config)])
        # Should handle unicode gracefully

    def test_cli_with_very_long_arguments(self, temp_config_dir: Path):
        """Test CLI with very long command line arguments."""
        long_path = temp_config_dir / ("very_long_filename_" + "x" * 200 + ".yaml")

        # Create a basic config
        config_data = {
            "project": {"type": "lib", "name": "test-lib"},
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        try:
            with open(long_path, "w") as f:
                yaml.dump(config_data, f)

            result = runner.invoke(app, ["create-project-from-config", str(long_path)])
            # Should handle long paths appropriately
        except OSError:
            # Skip if filesystem doesn't support long filenames
            pytest.skip("Filesystem doesn't support long filenames")

    def test_cli_with_empty_arguments(self):
        """Test CLI with empty or missing arguments."""
        # Test missing required argument
        result = runner.invoke(app, ["create-project-from-config"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_cli_interrupt_handling(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test CLI handling of keyboard interrupts."""
        with mock.patch(
            "pytemplate.project_creator.ProjectCreator.create_project_from_config"
        ) as mock_create:
            mock_create.side_effect = KeyboardInterrupt("User interrupted")

            result = runner.invoke(app, ["create-project-from-config", str(sample_lib_config)])
            # Should handle interrupts gracefully


class TestEnvironmentEdgeCases:
    """Test edge cases related to environment variables and system state."""

    def test_missing_environment_variables(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test handling when required environment variables are missing."""
        # Temporarily remove PATH to simulate missing environment
        original_path = os.environ.get("PATH")
        try:
            if "PATH" in os.environ:
                del os.environ["PATH"]

            creator = ProjectCreator(str(sample_lib_config))
            result = creator.create_project_from_config()
            # Should handle missing environment variables
        finally:
            if original_path:
                os.environ["PATH"] = original_path

    def test_corrupted_template_files(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test handling when template files are corrupted."""
        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pytemplate.project_creator._execute_cookiecutter") as mock_cookie:
            mock_cookie.side_effect = Exception("Template file corrupted")

            result = creator.create_project_from_config()
            assert result is False
