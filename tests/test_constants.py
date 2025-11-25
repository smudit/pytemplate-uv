"""Tests for pytemplate.constants module.

This module tests the constants and path resolution logic.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from pytemplate.constants import (
    BASE_DIR,
    PACKAGE_ROOT,
    TEMPLATE_PATHS_FILE,
    SecurityError,
    _find_template_paths_file,
    _get_base_dir,
)


class TestSecurityError:
    """Tests for SecurityError exception."""

    def test_security_error_can_be_raised(self) -> None:
        """Test that SecurityError can be instantiated and raised."""
        with pytest.raises(SecurityError, match="test message"):
            raise SecurityError("test message")

    def test_security_error_is_exception(self) -> None:
        """Test that SecurityError is a subclass of Exception."""
        assert issubclass(SecurityError, Exception)


class TestFindTemplatePathsFile:
    """Tests for _find_template_paths_file function."""

    def test_find_template_paths_file_in_package_directory(self, tmp_path: Path) -> None:
        """Test finding template_paths.yaml in package directory (development mode)."""
        # Arrange: Create a mock template_paths.yaml in parent directory
        template_file = tmp_path / "template_paths.yaml"
        template_file.write_text("test: value")

        # Act & Assert: Mock PACKAGE_ROOT to point to our test directory
        with patch("pytemplate.constants.PACKAGE_ROOT", tmp_path / "pytemplate"):
            result = _find_template_paths_file()
            # The function should return the parent directory path
            assert result == tmp_path / "template_paths.yaml"

    def test_find_template_paths_file_in_installed_location(self, tmp_path: Path) -> None:
        """Test finding template_paths.yaml in installed location."""
        pytest.skip("Generated stub - implementation needed for installed location test")

    def test_find_template_paths_file_returns_default_when_not_found(self) -> None:
        """Test that function returns default path when file doesn't exist."""
        pytest.skip("Generated stub - implementation needed for default path test")


class TestGetBaseDir:
    """Tests for _get_base_dir function."""

    def test_get_base_dir_with_templates_in_package_directory(self, tmp_path: Path) -> None:
        """Test getting base directory when templates exist in package directory (development)."""
        # Arrange: Create templates directory in parent
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Act & Assert: Mock PACKAGE_ROOT
        with patch("pytemplate.constants.PACKAGE_ROOT", tmp_path / "pytemplate"):
            result = _get_base_dir()
            # Should return parent directory containing templates
            assert result == tmp_path

    def test_get_base_dir_with_templates_in_installed_location(self, tmp_path: Path) -> None:
        """Test getting base directory when templates exist in installed location."""
        pytest.skip("Generated stub - implementation needed for installed location test")

    def test_get_base_dir_returns_default_when_templates_not_found(self) -> None:
        """Test that function returns default path when templates directory doesn't exist."""
        pytest.skip("Generated stub - implementation needed for default directory test")


class TestModuleLevelConstants:
    """Tests for module-level constants."""

    def test_package_root_is_path(self) -> None:
        """Test that PACKAGE_ROOT is a Path object."""
        assert isinstance(PACKAGE_ROOT, Path)
        assert PACKAGE_ROOT.name == "pytemplate"

    def test_template_paths_file_is_path(self) -> None:
        """Test that TEMPLATE_PATHS_FILE is a Path object."""
        assert isinstance(TEMPLATE_PATHS_FILE, Path)

    def test_base_dir_is_path(self) -> None:
        """Test that BASE_DIR is a Path object."""
        assert isinstance(BASE_DIR, Path)

    def test_base_dir_contains_templates_directory(self) -> None:
        """Test that BASE_DIR points to a directory containing templates."""
        # In the actual project, BASE_DIR should point to a location with templates
        templates_path = BASE_DIR / "templates"
        assert templates_path.exists(), f"Templates directory not found at {templates_path}"
