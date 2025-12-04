"""Tests for template management functionality."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest
import yaml

from pytemplate.template_manager import TemplateManager, TemplateResolver


class TestTemplateResolver:
    """Test TemplateResolver functionality."""

    def test_init_with_default_config(self, temp_config_dir: Path):
        """Test TemplateResolver initialization with default config."""
        # Create a temporary template paths file
        template_paths_file = temp_config_dir / "template_paths.yaml"
        template_data = {
            "project_templates": {"pyproject": "templates/pyproject-template"},
            "config_templates": {"lib": "templates/configs/lib.yaml.template"},
        }

        with open(template_paths_file, "w") as f:
            yaml.dump(template_data, f)

        # Mock the TEMPLATE_PATHS_FILE constant to point to our temp file
        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", template_paths_file):
            resolver = TemplateResolver()
            assert resolver.config_path is not None
            assert resolver.base_dir is not None

    def test_init_with_custom_config(self, temp_config_dir: Path):
        """Test TemplateResolver initialization with custom config path."""
        config_path = temp_config_dir / "custom_template_paths.yaml"
        config_data = {
            "project_templates": {"pyproject": "templates/pyproject-template"},
            "config_templates": {"lib": "templates/configs/lib.yaml.template"},
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
            "project_templates": {"pyproject": "templates/pyproject-template"},
            "config_templates": {"lib": "templates/configs/lib.yaml.template"},
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
        config_data = {"project_templates": {"pyproject": "templates/pyproject-template"}}

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError, match="Template type 'invalid_type' not found"):
                resolver.get_template_path("invalid_type", "pyproject")

    def test_get_template_path_invalid_name(self, temp_config_dir: Path):
        """Test getting template path with invalid template name."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {"project_templates": {"pyproject": "templates/pyproject-template"}}

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError, match="Template 'invalid_name' not found"):
                resolver.get_template_path("project_templates", "invalid_name")

    def test_resolve_github_template_path(self, temp_config_dir: Path):
        """Test resolving GitHub template paths."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {"project_templates": {"pylibrary": "gh:fpgmaas/cookiecutter-uv"}}

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            template_path = resolver.get_template_path("project_templates", "pylibrary")
            assert str(template_path) == "gh:fpgmaas/cookiecutter-uv"

    def test_load_template_paths_file_not_found(self, temp_config_dir: Path):
        """Test handling when template paths file is not found."""
        # Point to a non-existent file
        non_existent_file = temp_config_dir / "non_existent.yaml"

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", non_existent_file):
            with pytest.raises(FileNotFoundError):
                TemplateResolver()

    def test_load_template_paths_invalid_yaml(self, temp_config_dir: Path):
        """Test handling when template paths file contains invalid YAML."""
        # Create a file with invalid YAML
        invalid_yaml_file = temp_config_dir / "invalid.yaml"
        with open(invalid_yaml_file, "w") as f:
            f.write("invalid: yaml: [")  # Malformed YAML

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", invalid_yaml_file):
            with pytest.raises(yaml.YAMLError):
                TemplateResolver()

    def test_init_template_structure(self, temp_config_dir: Path):
        """Test initializing template directory structure."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "project_templates": {"pyproject": "templates/pyproject-template"},
            "config_templates": {"lib": "templates/configs/lib.yaml.template"},
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
        config_data = {"dev_templates": {"cursor": {"rules": "templates/shared/cursor_rules.md"}}}

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
        config_data = {"project_templates": {"pyproject": "templates/pyproject-template"}}

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
            "project_templates": {"pyproject": "templates/pyproject-template"},
            "shared": "templates/shared",
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
        # Create a template paths file first
        template_paths_file = temp_config_dir / "template_paths.yaml"
        template_data = {"project_templates": {"pyproject": "templates/pyproject-template"}}
        with open(template_paths_file, "w") as f:
            yaml.dump(template_data, f)

        # Create a directory where the config file should be, causing creation to fail
        config_path = temp_config_dir / "config.yaml"
        config_path.mkdir()  # Create as directory instead of file

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", template_paths_file):
            with pytest.raises(OSError):  # Should fail to create config due to directory conflict
                TemplateResolver(str(config_path))

    def test_invalid_config_structure(self, temp_config_dir: Path):
        """Test handling of invalid configuration structure."""
        config_path = temp_config_dir / "template_paths.yaml"
        # Create config with invalid structure (missing required keys)
        config_data = {"invalid_structure": "value"}

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            with pytest.raises(ValueError):
                resolver.get_template_path("nonexistent_type", "template")

    def test_load_config_with_non_dict_entries(self, temp_config_dir: Path):
        """Test loading config with non-dict entries (like comments/metadata)."""
        config_path = temp_config_dir / "template_paths.yaml"
        config_data = {
            "comment": "This is a comment",  # Non-dict entry
            "project_scaffolds": {"test": "templates/test"},
        }

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with mock.patch("pytemplate.template_manager.TEMPLATE_PATHS_FILE", config_path):
            resolver = TemplateResolver()
            # Should handle non-dict entries gracefully
            assert "project_scaffolds" in resolver.config
            assert "comment" in resolver.config

    def test_init_template_structure_with_nested_templates(self, temp_config_dir: Path):
        """Test initializing template structure with nested template paths."""
        # TODO: Requires mocking BASE_DIR to properly test nested template initialization
        pytest.skip("Generated stub - needs BASE_DIR mocking for nested templates")
