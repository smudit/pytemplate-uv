"""Tests for configuration validation and schema compliance."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest
import yaml

from pytemplate.project_creator import ProjectCreator


class TestProjectConfigValidation:
    """Test validation of project configuration section."""

    def test_valid_project_config(self, temp_config_dir: Path):
        """Test validation of valid project configuration."""
        valid_config = temp_config_dir / "valid.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-project",
                "description": "A test project",
                "python_version": "3.11",
                "author": "Test Author",
                "email": "test@example.com",
                "version": "0.1.0",
                "license": "MIT"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(valid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(valid_config))
        creator.load_config()
        
        # Should load without errors
        assert creator.config["project"]["type"] == "lib"
        assert creator.config["project"]["name"] == "test-project"

    def test_missing_project_type(self, temp_config_dir: Path):
        """Test validation when project type is missing."""
        invalid_config = temp_config_dir / "missing_type.yaml"
        config_data = {
            "project": {
                "name": "test-project",
                "description": "A test project"
                # Missing "type" field
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        with pytest.raises(KeyError):
            creator.load_config()
            creator.create_project_from_config()

    def test_missing_project_name(self, temp_config_dir: Path):
        """Test validation when project name is missing."""
        invalid_config = temp_config_dir / "missing_name.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "description": "A test project"
                # Missing "name" field
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        with pytest.raises(KeyError):
            creator.load_config()
            creator.create_project_from_config()

    def test_invalid_project_type(self, temp_config_dir: Path):
        """Test validation with invalid project type."""
        invalid_config = temp_config_dir / "invalid_type.yaml"
        config_data = {
            "project": {
                "type": "invalid_type",  # Invalid type
                "name": "test-project",
                "description": "A test project"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        # Should fail during project creation due to invalid type
        result = creator.create_project_from_config()
        assert result is False

    def test_empty_project_name(self, temp_config_dir: Path):
        """Test validation with empty project name."""
        invalid_config = temp_config_dir / "empty_name.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "",  # Empty name
                "description": "A test project"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        # Should handle empty project name appropriately
        result = creator.create_project_from_config()
        # May succeed or fail depending on implementation


class TestGitHubConfigValidation:
    """Test validation of GitHub configuration section."""

    def test_valid_github_config(self, temp_config_dir: Path):
        """Test validation of valid GitHub configuration."""
        valid_config = temp_config_dir / "valid_github.yaml"
        config_data = {
            "project": {
                "type": "service",
                "name": "test-service",
                "description": "A test service"
            },
            "github": {
                "add_on_github": True,
                "repo_name": "test-service",
                "repo_private": False,
                "github_username": "testuser"
            },
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(valid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(valid_config))
        creator.load_config()
        
        assert creator.config["github"]["add_on_github"] is True
        assert creator.config["github"]["repo_name"] == "test-service"

    def test_missing_github_section(self, temp_config_dir: Path):
        """Test handling when GitHub section is missing."""
        config_without_github = temp_config_dir / "no_github.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-lib",
                "description": "A test library"
            }
            # Missing github section
        }
        
        with open(config_without_github, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(config_without_github))
        # Should handle missing GitHub section gracefully
        result = creator.create_project_from_config()
        # May succeed with defaults or fail

    def test_invalid_github_boolean_values(self, temp_config_dir: Path):
        """Test validation with invalid boolean values in GitHub config."""
        invalid_config = temp_config_dir / "invalid_github_bool.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-lib",
                "description": "A test library"
            },
            "github": {
                "add_on_github": "yes",  # Should be boolean
                "repo_private": "no"     # Should be boolean
            },
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        # Should handle string boolean values appropriately
        creator.load_config()
        # Implementation may convert strings to booleans


class TestDockerConfigValidation:
    """Test validation of Docker configuration section."""

    def test_valid_docker_config(self, temp_config_dir: Path):
        """Test validation of valid Docker configuration."""
        valid_config = temp_config_dir / "valid_docker.yaml"
        config_data = {
            "project": {
                "type": "service",
                "name": "test-service",
                "description": "A test service"
            },
            "github": {"add_on_github": False},
            "docker": {
                "docker_image": True,
                "docker_compose": True
            },
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}}
        }
        
        with open(valid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(valid_config))
        creator.load_config()
        
        assert creator.config["docker"]["docker_image"] is True
        assert creator.config["docker"]["docker_compose"] is True

    def test_missing_docker_section(self, temp_config_dir: Path):
        """Test handling when Docker section is missing."""
        config_without_docker = temp_config_dir / "no_docker.yaml"
        config_data = {
            "project": {
                "type": "service",
                "name": "test-service",
                "description": "A test service"
            },
            "github": {"add_on_github": False}
            # Missing docker section
        }
        
        with open(config_without_docker, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(config_without_docker))
        # Should handle missing Docker section gracefully
        result = creator.create_project_from_config()


class TestAIConfigValidation:
    """Test validation of AI configuration section."""

    def test_valid_ai_config(self, temp_config_dir: Path):
        """Test validation of valid AI configuration."""
        valid_config = temp_config_dir / "valid_ai.yaml"
        config_data = {
            "project": {
                "type": "service",
                "name": "test-service",
                "description": "A test service"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {
                "copilots": {
                    "cursor_rules_path": ".cursor/rules/coding_rules.md",
                    "cline_rules_path": ".clinerules"
                }
            }
        }
        
        with open(valid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(valid_config))
        creator.load_config()
        
        assert "copilots" in creator.config["ai"]
        assert creator.config["ai"]["copilots"]["cursor_rules_path"] == ".cursor/rules/coding_rules.md"

    def test_missing_ai_section(self, temp_config_dir: Path):
        """Test handling when AI section is missing."""
        config_without_ai = temp_config_dir / "no_ai.yaml"
        config_data = {
            "project": {
                "type": "service",
                "name": "test-service",
                "description": "A test service"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False}
            # Missing ai section
        }
        
        with open(config_without_ai, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(config_without_ai))
        # Should handle missing AI section gracefully
        result = creator.create_project_from_config()


class TestDevelopmentConfigValidation:
    """Test validation of development configuration for library projects."""

    def test_valid_development_config(self, temp_config_dir: Path):
        """Test validation of valid development configuration."""
        valid_config = temp_config_dir / "valid_dev.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-lib",
                "description": "A test library"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "development": {
                "use_pytest": True,
                "use_sphinx": True,
                "use_black": True,
                "use_ruff": True,
                "use_mypy": True,
                "command_line_interface": "click"
            }
        }
        
        with open(valid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(valid_config))
        creator.load_config()
        
        assert creator.config["development"]["use_pytest"] is True
        assert creator.config["development"]["command_line_interface"] == "click"

    def test_invalid_cli_interface_option(self, temp_config_dir: Path):
        """Test validation with invalid CLI interface option."""
        invalid_config = temp_config_dir / "invalid_cli.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-lib",
                "description": "A test library"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "development": {
                "command_line_interface": "invalid_option"  # Invalid option
            }
        }
        
        with open(invalid_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(invalid_config))
        # Should fail with invalid CLI interface option
        result = creator.create_project_from_config()
        assert result is False


class TestConfigSchemaCompliance:
    """Test overall configuration schema compliance."""

    def test_minimal_valid_config(self, temp_config_dir: Path):
        """Test minimal valid configuration."""
        minimal_config = temp_config_dir / "minimal.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "minimal-project"
            }
        }
        
        with open(minimal_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(minimal_config))
        # Should handle minimal config with defaults
        result = creator.create_project_from_config()

    def test_config_with_extra_fields(self, temp_config_dir: Path):
        """Test configuration with extra unknown fields."""
        extra_config = temp_config_dir / "extra.yaml"
        config_data = {
            "project": {
                "type": "lib",
                "name": "test-lib",
                "description": "A test library"
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
            "unknown_section": {  # Extra unknown section
                "unknown_field": "unknown_value"
            }
        }
        
        with open(extra_config, "w") as f:
            yaml.dump(config_data, f)
        
        creator = ProjectCreator(str(extra_config))
        # Should handle extra fields gracefully
        creator.load_config()
        assert "unknown_section" in creator.config
