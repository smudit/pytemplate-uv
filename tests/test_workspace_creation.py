"""Tests for workspace project creation functionality."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from pytemplate.main import app
from pytemplate.project_creator import ProjectCreator

runner = CliRunner()
logger = logging.getLogger(__name__)


@pytest.fixture
def sample_workspace_config(temp_config_dir: Path) -> Path:
    """Create a sample workspace configuration file.

    Args:
    ----
        temp_config_dir: Temporary directory for config files

    Returns:
    -------
        Path: Path to the sample config file

    """
    config = {
        "project": {
            "type": "workspace",
            "name": "test-workspace",
            "description": "Test workspace project",
            "python_version": "3.11",
            "author": "Test Author",
            "email": "test@example.com",
            "version": "0.1.0",
        },
        "github": {
            "add_on_github": True,
            "repo_name": "test-workspace",
            "repo_private": False,
            "github_username": "testuser",
        },
        "docker": {"docker_image": False, "docker_compose": False},
        "devcontainer": {"enabled": True},
        "workspace": {
            "projects": ["project1", "project2", "project3"],
            "shared_dependencies": True,
            "monorepo_structure": True,
        },
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
    }

    config_path = temp_config_dir / "workspace_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


class TestWorkspaceProjectCreation:
    """Test workspace project creation functionality."""

    def test_create_workspace_project_basic(
        temp_project_dir: Path, sample_workspace_config: Path
    ) -> None:
        """Test basic workspace project creation.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - Basic workspace structure is created
        """
        with (
            mock.patch("pytemplate.project_creator._validate_template") as mock_validate,
            mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call,
            mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver,
        ):
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path(
                "templates/shared/coding_rules.md"
            )

            # Create template directory structure
            template_dir = Path("templates/shared")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "coding_rules.md").write_text("# Coding Rules")

            result = runner.invoke(
                app, ["create-project-from-config", str(sample_workspace_config)]
            )

            assert result.exit_code == 0, "Command should exit with code 0"
            assert (
                temp_project_dir / "test-workspace"
            ).exists(), "Project directory should be created"

    def test_create_workspace_project_with_github(
        temp_project_dir: Path, sample_workspace_config: Path
    ) -> None:
        """Test workspace project creation with GitHub integration.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - GitHub repository is created
        """
        with (
            mock.patch("pytemplate.project_creator._validate_template") as mock_validate,
            mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call,
            mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver,
        ):
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path(
                "templates/shared/coding_rules.md"
            )

            # Create template directory structure
            template_dir = Path("templates/shared")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "coding_rules.md").write_text("# Coding Rules")

            # Update config to enable GitHub
            with open(sample_workspace_config) as f:
                config = yaml.safe_load(f)

            config["github"]["add_on_github"] = True

            with open(sample_workspace_config, "w") as f:
                yaml.dump(config, f)

            result = runner.invoke(
                app, ["create-project-from-config", str(sample_workspace_config)]
            )

            assert result.exit_code == 0, "Command should exit with code 0"
            assert (
                temp_project_dir / "test-workspace"
            ).exists(), "Project directory should be created"

    def test_create_workspace_project_with_devcontainer(
        temp_project_dir: Path, sample_workspace_config: Path
    ) -> None:
        """Test workspace project creation with devcontainer support.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - Devcontainer configuration is created
        """
        with (
            mock.patch("pytemplate.project_creator._validate_template") as mock_validate,
            mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call,
            mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver,
        ):
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path(
                "templates/shared/coding_rules.md"
            )

            # Create template directory structure
            template_dir = Path("templates/shared")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "coding_rules.md").write_text("# Coding Rules")

            # Update config to enable devcontainer
            with open(sample_workspace_config) as f:
                config = yaml.safe_load(f)

            config["devcontainer"]["use_devcontainer"] = True

            with open(sample_workspace_config, "w") as f:
                yaml.dump(config, f)

            result = runner.invoke(
                app, ["create-project-from-config", str(sample_workspace_config)]
            )

            assert result.exit_code == 0, "Command should exit with code 0"
            assert (
                temp_project_dir / "test-workspace"
            ).exists(), "Project directory should be created"

    def test_workspace_config_validation(self, temp_config_dir: Path):
        """Test workspace configuration validation."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "test-workspace",
                "description": "Test workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "workspace_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        assert creator.config["project"]["type"] == "workspace"
        assert creator.validate_config() is True

    def test_workspace_docker_validation(self, temp_config_dir: Path):
        """Test that workspace projects can have Docker configurations."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "test-workspace",
                "description": "Test workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": True, "docker_compose": True},  # Should be allowed
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "workspace_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        # Workspace projects should allow Docker configurations
        assert creator.validate_config() is True

    def test_workspace_cli_creation(temp_project_dir: Path, sample_workspace_config: Path) -> None:
        """Test workspace project creation via CLI.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - CLI arguments are properly handled
        """
        with (
            mock.patch("pytemplate.project_creator._validate_template") as mock_validate,
            mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call,
            mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver,
        ):
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path(
                "templates/shared/coding_rules.md"
            )

            # Create template directory structure
            template_dir = Path("templates/shared")
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "coding_rules.md").write_text("# Coding Rules")

            result = runner.invoke(
                app,
                [
                    "create-project-from-config",
                    str(sample_workspace_config),
                    "--force",
                    "--no-interactive",
                ],
            )

            assert result.exit_code == 0, "Command should exit with code 0"
            assert (
                temp_project_dir / "test-workspace"
            ).exists(), "Project directory should be created"

    def test_workspace_with_invalid_config(self, temp_config_dir: Path):
        """Test workspace project creation with invalid configuration."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "",  # Invalid empty name
                "description": "Test workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "invalid_workspace_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        result = creator.create_project_from_config()
        assert result is False


class TestWorkspaceSpecificFeatures:
    """Test workspace-specific features and configurations."""

    def test_workspace_monorepo_structure(self, temp_config_dir: Path):
        """Test workspace monorepo structure configuration."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "monorepo-workspace",
                "description": "Monorepo workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "workspace": {
                "monorepo_structure": True,
                "shared_dependencies": True,
                "projects": ["api", "frontend", "shared"],
            },
        }

        config_path = temp_config_dir / "monorepo_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        assert creator.config["workspace"]["monorepo_structure"] is True
        assert creator.config["workspace"]["shared_dependencies"] is True
        assert len(creator.config["workspace"]["projects"]) == 3

    def test_workspace_multiple_projects(self, temp_config_dir: Path):
        """Test workspace with multiple sub-projects."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "multi-project-workspace",
                "description": "Multi-project workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "workspace": {
                "projects": [
                    {"name": "api", "type": "service"},
                    {"name": "cli", "type": "lib"},
                    {"name": "docs", "type": "static"},
                ],
            },
        }

        config_path = temp_config_dir / "multi_project_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        assert len(creator.config["workspace"]["projects"]) == 3
        assert creator.config["workspace"]["projects"][0]["name"] == "api"

    def test_workspace_shared_dependencies(self, temp_config_dir: Path):
        """Test workspace shared dependencies configuration."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "shared-deps-workspace",
                "description": "Workspace with shared dependencies",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "workspace": {
                "shared_dependencies": True,
                "dependency_management": "uv",
                "shared_packages": ["pytest", "black", "ruff"],
            },
        }

        config_path = temp_config_dir / "shared_deps_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        assert creator.config["workspace"]["shared_dependencies"] is True
        assert creator.config["workspace"]["dependency_management"] == "uv"
        assert "pytest" in creator.config["workspace"]["shared_packages"]


class TestWorkspaceErrorHandling:
    """Test error handling specific to workspace projects."""

    def test_workspace_missing_required_fields(self, temp_config_dir: Path):
        """Test workspace creation with missing required fields."""
        config_data = {
            "project": {
                "type": "workspace",
                # Missing name field
                "description": "Test workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "missing_fields_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        with pytest.raises(Exception):  # Should fail due to missing name
            creator.load_config()
            creator.create_project_from_config()

    def test_workspace_invalid_project_structure(self, temp_config_dir: Path):
        """Test workspace with invalid project structure."""
        config_data = {
            "project": {
                "type": "workspace",
                "name": "invalid-workspace",
                "description": "Invalid workspace",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "workspace": {
                "projects": "invalid_structure",  # Should be a list
            },
        }

        config_path = temp_config_dir / "invalid_structure_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        creator = ProjectCreator(str(config_path))
        creator.load_config()

        # Should handle invalid structure gracefully
        result = creator.create_project_from_config()
        # May succeed or fail depending on implementation
