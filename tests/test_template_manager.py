"""Tests for template management functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml

from pytemplate.template_manager import TemplateManager, TemplateResolver


class TestTemplateResolver:
    """Test TemplateResolver functionality."""

    def test_init_with_default_config(self):
        """Test TemplateResolver initialization with default config."""
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE") as mock_file:
            mock_file.open.return_value.__enter__.return_value.read.return_value = """
            project_templates:
              pyproject: templates/pyproject-template
            config_templates:
              lib: templates/configs/lib.yaml.template
            """
            
            resolver = TemplateResolver()
            assert resolver.config_path is not None
            assert resolver.base_dir is not None

    def test_init_with_custom_config(self, temp_config_dir: Path):
        """Test TemplateResolver initialization with custom config path."""
        config_path = temp_config_dir / "custom_template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            },
            "config_templates": {
                "lib": "templates/configs/lib.yaml.template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver(str(config_path))
            assert resolver.config_path == config_path

    def test_get_template_path_valid(self, temp_config_dir: Path):
        """Test getting valid template path."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            },
            "config_templates": {
                "lib": "templates/configs/lib.yaml.template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            template_path = resolver.get_template_path("project_templates", "pyproject")
            assert "pyproject-template" in str(template_path)

    def test_get_template_path_invalid_type(self, temp_config_dir: Path):
        """Test getting template path with invalid template type."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError, match="Template type 'invalid_type' not found"):
                resolver.get_template_path("invalid_type", "pyproject")

    def test_get_template_path_invalid_name(self, temp_config_dir: Path):
        """Test getting template path with invalid template name."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError, match="Template 'invalid_name' not found"):
                resolver.get_template_path("project_templates", "invalid_name")

    def test_resolve_github_template_path(self, temp_config_dir: Path):
        """Test resolving GitHub template paths."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pylibrary": "gh:ionelmc/cookiecutter-pylibrary"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            template_path = resolver.get_template_path("project_templates", "pylibrary")
            assert str(template_path) == "gh:ionelmc/cookiecutter-pylibrary"

    def test_load_template_paths_file_not_found(self):
        """Test handling when template paths file is not found."""
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE") as mock_file:
            mock_file.open.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                TemplateResolver()

    def test_load_template_paths_invalid_yaml(self):
        """Test handling when template paths file contains invalid YAML."""
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE") as mock_file:
            mock_file.open.return_value.__enter__.return_value.read.return_value = "invalid: yaml: ["
            mock_file.open.side_effect = yaml.YAMLError("Invalid YAML")
            
            with pytest.raises(yaml.YAMLError):
                TemplateResolver()

    def test_init_template_structure(self, temp_config_dir: Path):
        """Test initializing template directory structure."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            },
            "config_templates": {
                "lib": "templates/configs/lib.yaml.template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            # This should not raise an exception
            resolver.init_template_structure()

    def test_get_relative_path_nested_templates(self, temp_config_dir: Path):
        """Test getting relative path for nested template structures."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "dev_templates": {
                "cursor": {
                    "rules": "templates/shared/cursor_rules.md"
                }
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            # Test that nested structures are handled properly
            with pytest.raises(ValueError):  # Should fail for nested access
                resolver.get_template_path("dev_templates", "cursor")


class TestTemplateManager:
    """Test TemplateManager functionality."""

    def test_init(self, temp_config_dir: Path):
        """Test TemplateManager initialization."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            manager = TemplateManager(resolver)
            assert manager.resolver == resolver

    def test_template_manager_with_resolver(self, temp_config_dir: Path):
        """Test TemplateManager with a valid resolver."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {
                "pyproject": "templates/pyproject-template"
            },
            "shared": "templates/shared"
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            manager = TemplateManager(resolver)
            
            # Test that manager can access resolver methods
            template_path = manager.resolver.get_template_path("project_templates", "pyproject")
            assert "pyproject-template" in str(template_path)


class TestErrorHandling:
    """Test error handling in template management."""

    def test_config_creation_failure(self, temp_config_dir: Path):
        """Test handling when config file creation fails."""
        # Create a directory where the config file should be, causing creation to fail
        config_path = temp_config_dir / "template_paths.yaml"
        config_path.mkdir()  # Create as directory instead of file
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            with pytest.raises(Exception):  # Should fail to create config
                TemplateResolver()

    def test_invalid_config_structure(self, temp_config_dir: Path):
        """Test handling of invalid configuration structure."""
        config_path = temp_config_dir / "template_paths.yaml"
        # Create config with invalid structure (missing required keys)
        config_data = {
            "invalid_structure": "value"
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError):
                resolver.get_template_path("nonexistent_type", "template")
