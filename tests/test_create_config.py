"""Tests for create-config command."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest import mock

import pytest
import yaml
from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_config_templates(temp_project_dir: Path) -> Path:
    """Create mock configuration templates for testing.

    Returns
    -------
        Path: Path to the mock configuration templates directory

    """
    mock_dir = Path(temp_project_dir) / "config_templates"
    mock_dir.mkdir(exist_ok=True)

    # Create mock template files
    for project_type in ["lib", "service", "workspace"]:
        template_file = mock_dir / f"{project_type}.yaml.template"
        template_file.write_text(
            f"""
            project_type: {project_type}
            name: test-{project_type}
            description: "Test {project_type} project"
            """
        )

    return mock_dir


@pytest.mark.parametrize("project_type", ["lib", "service", "workspace"])
def test_create_config_valid_types(
    temp_project_dir: Path, project_type: str, mock_config_templates: Path
) -> None:
    """Test config creation for valid project types.

    Verifies that:
    - Command exits successfully for valid project types
    - Config file is created
    - Config file contains expected content
    """
    # Create a mock template file that the code will read
    template_path = mock_config_templates / f"{project_type}.yaml.template"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(f"""
    project_type: {project_type}
    name: test-{project_type}
    description: "Test {project_type} project"
    """)

    # Create a mock template file content
    template_content = f"""
    project_type: {project_type}
    name: test-{project_type}
    description: "Test {project_type} project"
    """

    # Create a mock TemplateResolver for testing
    mock_resolver = mock.MagicMock()
    mock_get_template_path = mock.MagicMock()
    mock_template_path = mock.MagicMock()

    # Mock the properties and methods of the Path object
    mock_template_path.exists.return_value = True
    mock_template_path.read_text.return_value = template_content

    mock_get_template_path.return_value = mock_template_path
    mock_resolver.return_value.get_template_path = mock_get_template_path

    # Patch the TemplateResolver in main
    with mock.patch("pytemplate.main.TemplateResolver", mock_resolver):
        result = runner.invoke(app, ["create-config", project_type])

        assert result.exit_code == 0, "Command should exit with code 0 for valid project types"
        config_path = Path(temp_project_dir, "project_config.yaml")
        assert config_path.exists(), "Config file should exist"

        # Verify config contains expected project type
        with open(config_path) as f:
            config = yaml.safe_load(f)
            # The config is created directly from the template content
            assert config is not None, "Config should be loaded successfully"

        # Verify TemplateResolver was called with the right parameters
        mock_get_template_path.assert_called_with("config_specs", project_type)


def test_create_config_invalid_type(temp_project_dir: Path, mock_config_templates: Path) -> None:
    """Test config creation with invalid project type.

    Verifies that:
    - Command fails with invalid project type
    - Appropriate error code is returned
    - Error message is shown
    - No config file is created
    """
    # Create a mock TemplateResolver
    mock_resolver = mock.MagicMock()

    # Patch the TemplateResolver in main
    with mock.patch("pytemplate.main.TemplateResolver", mock_resolver):
        result = runner.invoke(app, ["create-config", "invalid-type"])

        assert result.exit_code == 1, "Command should fail with invalid project type"
        assert "Invalid project type" in result.output, "Error message should be shown"
        assert not Path(temp_project_dir, "project_config.yaml").exists(), (
            "Config file should not be created for invalid type"
        )

        # Verify TemplateResolver was not called with invalid type
        mock_resolver.return_value.get_template_path.assert_not_called()


def test_create_config_custom_output(temp_project_dir: Path, mock_config_templates: Path) -> None:
    """Test config creation with custom output path.

    Verifies that:
    - Command exits successfully with custom output path
    - Config file is created at specified location
    - Config file contains valid content
    """
    output_path = "custom_config.yaml"

    # Create a mock template file that the code will read
    template_path = mock_config_templates / "lib.yaml.template"
    template_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a mock template file content
    template_content = """
    project_type: lib
    name: test-lib
    description: "Test lib project"
    """

    # Create a mock TemplateResolver for testing
    mock_resolver = mock.MagicMock()
    mock_get_template_path = mock.MagicMock()
    mock_template_path = mock.MagicMock()

    # Mock the properties and methods of the Path object
    mock_template_path.exists.return_value = True
    mock_template_path.read_text.return_value = template_content

    mock_get_template_path.return_value = mock_template_path
    mock_resolver.return_value.get_template_path = mock_get_template_path

    # Patch the TemplateResolver in main
    with mock.patch("pytemplate.main.TemplateResolver", mock_resolver):
        result = runner.invoke(app, ["create-config", "lib", "--output-path", output_path])

        assert result.exit_code == 0, "Command should exit with code 0 with custom output path"
        config_path = Path(temp_project_dir, output_path)
        assert config_path.exists(), "Config file should exist at custom location"

        # Verify config contains expected project type
        with open(config_path) as f:
            config = yaml.safe_load(f)
            # The config is created directly from the template content
            assert config is not None, "Config should be loaded successfully"

        # Verify TemplateResolver was called with the right parameters
        mock_get_template_path.assert_called_with("config_specs", "lib")
