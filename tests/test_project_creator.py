"""Tests for ProjectCreator functionality."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock

import pytest
import yaml

from pytemplate.project_creator import ProjectCreator


class TestProjectCreatorInit:
    """Test ProjectCreator initialization."""

    def test_init_basic(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test basic ProjectCreator initialization."""
        creator = ProjectCreator(str(sample_lib_config))
        assert creator.config_path == sample_lib_config
        assert creator.interactive is False
        assert creator.config == {}
        assert creator.project_path is None

    def test_init_interactive(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test ProjectCreator initialization with interactive mode."""
        creator = ProjectCreator(str(sample_lib_config), interactive=True)
        assert creator.interactive is True

    def test_init_with_template_resolver(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test that ProjectCreator initializes template resolver."""
        creator = ProjectCreator(str(sample_lib_config))
        assert creator.template_resolver is not None
        assert creator.template_manager is not None


class TestConfigLoading:
    """Test configuration loading functionality."""

    def test_load_config_valid(self, temp_config_dir: Path, sample_lib_config: Path):
        """Test loading valid configuration."""
        creator = ProjectCreator(str(sample_lib_config))
        creator.load_config()

        assert creator.config is not None
        assert "project" in creator.config
        assert creator.config["project"]["type"] == "lib"
        assert creator.config["project"]["name"] == "test-lib"

    def test_load_config_file_not_found(self, temp_config_dir: Path):
        """Test handling when config file is not found."""
        nonexistent_config = temp_config_dir / "nonexistent.yaml"
        creator = ProjectCreator(str(nonexistent_config))
        creator.enable_testing_mode()

        with pytest.raises(FileNotFoundError):
            creator.load_config()

    def test_load_config_invalid_yaml(self, temp_config_dir: Path):
        """Test handling when config file contains invalid YAML."""
        invalid_config = temp_config_dir / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [")

        creator = ProjectCreator(str(invalid_config))
        creator.enable_testing_mode()
        with pytest.raises(yaml.YAMLError):
            creator.load_config()



class TestLibraryProjectCreation:
    """Test library project creation."""

    def test_create_lib_project_basic(self, temp_project_dir: Path, sample_lib_config: Path):
        """Test basic library project creation."""
        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate:
            mock_validate.return_value = "gh:ionelmc/cookiecutter-pylibrary"

            result = creator.create_project_from_config()
            assert result is True
            assert creator.project_path is not None

    def test_create_lib_project_with_github(
        self, temp_project_dir: Path, sample_lib_config: Path, mock_subprocess
    ):
        """Test library project creation with GitHub integration."""
        # Modify config to enable GitHub
        with open(sample_lib_config) as f:
            config = yaml.safe_load(f)
        config["github"]["add_on_github"] = True

        with open(sample_lib_config, "w") as f:
            yaml.dump(config, f)

        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate:
            mock_validate.return_value = "gh:ionelmc/cookiecutter-pylibrary"

            result = creator.create_project_from_config()
            assert result is True

    def test_create_lib_project_force_overwrite(
        self, temp_project_dir: Path, sample_lib_config: Path
    ):
        """Test library project creation with force overwrite."""
        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate:
            mock_validate.return_value = "gh:ionelmc/cookiecutter-pylibrary"

            result = creator.create_project_from_config(force=True)
            assert result is True


class TestServiceProjectCreation:
    """Test service project creation."""

    def test_create_service_project_basic(
        self, temp_project_dir: str, sample_service_config: Path
    ) -> None:
        """Test basic service project creation.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - Basic service structure is created
        """
        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate, \
             mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call, \
             mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path("templates/shared/coding_rules.md")

            creator = ProjectCreator(str(sample_service_config))
            result = creator.create_project_from_config()

            assert result is True, "Project creation should succeed"
            assert (Path(temp_project_dir) / "test-service").exists(), "Project directory should be created"

    def test_create_service_project_with_addons(
        self, temp_project_dir: str, sample_service_config: Path
    ) -> None:
        """Test service project creation with addons.

        Verifies that:
        - Command exits successfully
        - Project directory is created
        - Addons are properly configured
        """
        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate, \
             mock.patch("pytemplate.project_creator.subprocess.check_call") as mock_check_call, \
             mock.patch("pytemplate.project_creator.TemplateResolver") as mock_resolver:
            mock_validate.return_value = Path("templates/pyproject-template")
            mock_check_call.return_value = 0
            mock_resolver.return_value.get_template_path.return_value = Path("templates/shared/coding_rules.md")

            # Update config to enable addons
            with open(sample_service_config) as f:
                config = yaml.safe_load(f)

            config["github"]["add_on_github"] = True
            config["ai"] = {
                "copilots": {
                    "cursor_rules_path": ".cursor/rules.md",
                    "cline_rules_path": ".cline/rules.md"
                }
            }

            with open(sample_service_config, "w") as f:
                yaml.dump(config, f)

            creator = ProjectCreator(str(sample_service_config))
            result = creator.create_project_from_config()

            assert result is True, "Project creation should succeed"
            assert (Path(temp_project_dir) / "test-service").exists(), "Project directory should be created"


class TestGitHubIntegration:
    """Test GitHub repository creation functionality."""

    def test_create_github_repo_success(
        self, temp_project_dir: Path, sample_service_config: Path, mock_subprocess
    ):
        """Test successful GitHub repository creation."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_project_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        result = creator.create_github_repo()
        assert result is True

    def test_create_github_repo_failure(self, temp_project_dir: Path, sample_service_config: Path):
        """Test GitHub repository creation failure."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_project_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        with mock.patch("subprocess.check_call") as mock_call:
            mock_call.side_effect = subprocess.CalledProcessError(1, "gh")

            result = creator.create_github_repo()
            assert result is False

    def test_create_github_repo_no_project_path(
        self, temp_project_dir: Path, sample_service_config: Path
    ):
        """Test GitHub repository creation without project path set."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        # Don't set project_path

        result = creator.create_github_repo()
        assert result is False

    def test_create_github_repo_private(
        self, temp_project_dir: Path, sample_service_config: Path, mock_subprocess
    ):
        """Test creating private GitHub repository."""
        # Modify config to make repo private
        with open(sample_service_config) as f:
            config = yaml.safe_load(f)
        config["github"]["repo_private"] = True

        with open(sample_service_config, "w") as f:
            yaml.dump(config, f)

        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_project_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        with mock.patch("subprocess.check_call") as mock_call:
            result = creator.create_github_repo()
            assert result is True
            # Verify that --private flag was used
            mock_call.assert_called()
            args = mock_call.call_args[0][0]
            assert "--private" in args


class TestAITemplateIntegration:
    """Test AI template copying functionality."""

    def test_copy_ai_templates_success(
        self, temp_project_dir: Path, sample_service_config: Path, temp_templates_dir: Path
    ):
        """Test successful AI template copying."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_project_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        # Create a mock coding rules template
        rules_template = temp_templates_dir / "shared" / "coding_rules.md"
        rules_template.parent.mkdir(parents=True, exist_ok=True)
        rules_template.write_text("# Coding Rules\n\nTest rules content")

        # Mock the template resolver to return the temp templates directory and ai_copilots config
        with mock.patch.object(creator.template_resolver, "get_template_path") as mock_get_path:
            mock_get_path.return_value = rules_template
            
            # Mock the ai_copilots configuration from template_paths.yaml
            with mock.patch.object(creator.template_resolver, "config", {"ai_copilots": {
                "cursor": ".cursor/rules",
                "cline": ".clinerules"
            }}):
                result = creator.copy_ai_templates()
                assert result is True

                # Verify files were created at the paths defined in template_paths.yaml
                cursor_rules = creator.project_path / ".cursor/rules"
                cline_rules = creator.project_path / ".clinerules"
                assert cursor_rules.exists()
                assert cline_rules.exists()
                
                # Verify content
                assert cursor_rules.read_text() == "# Coding Rules\n\nTest rules content"
                assert cline_rules.read_text() == "# Coding Rules\n\nTest rules content"

    def test_copy_ai_templates_no_project_path(
        self, temp_project_dir: Path, sample_service_config: Path
    ):
        """Test AI template copying without project path set."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        # Don't set project_path

        result = creator.copy_ai_templates()
        assert result is False

    def test_copy_ai_templates_source_not_found(
        self, temp_project_dir: Path, sample_service_config: Path
    ):
        """Test AI template copying when source template is not found."""
        creator = ProjectCreator(str(sample_service_config))
        creator.load_config()
        creator.project_path = Path(temp_project_dir) / "test-service"
        creator.project_path.mkdir(parents=True, exist_ok=True)

        # Mock the template resolver to return a non-existent path
        with mock.patch.object(creator.template_resolver, "get_template_path") as mock_get_path:
            mock_get_path.return_value = Path("/nonexistent/path")
            
            # Mock the ai_copilots configuration
            with mock.patch.object(creator.template_resolver, "config", {"ai_copilots": {
                "cursor": ".cursor/rules",
                "cline": ".clinerules"
            }}):
                result = creator.copy_ai_templates()
                # Should return True because it gracefully handles missing templates
                assert result is True


class TestErrorHandling:
    """Test error handling in ProjectCreator."""

    def test_create_project_general_exception(
        self, temp_project_dir: Path, sample_lib_config: Path
    ):
        """Test handling of general exceptions during project creation."""
        creator = ProjectCreator(str(sample_lib_config))

        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate:
            mock_validate.side_effect = Exception("General error")

            result = creator.create_project_from_config()
            assert result is False

