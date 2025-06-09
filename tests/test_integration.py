"""Integration tests for pytemplate-uv end-to-end workflows."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import yaml
from typer.testing import CliRunner

from pytemplate.main import app

runner = CliRunner()


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_complete_lib_project_workflow(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test complete library project creation workflow."""
        # Step 1: Create configuration
        result = runner.invoke(app, ["create-config", "lib", "--output-path", "lib_config.yaml"])
        assert result.exit_code == 0

        config_path = Path(temp_project_dir) / "lib_config.yaml"
        assert config_path.exists()

        # Step 2: Modify configuration for testing
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Ensure we have a valid config structure
        if not config:
            config = {}

        config.update(
            {
                "project": {
                    "type": "lib",
                    "name": "test-integration-lib",
                    "description": "Integration test library",
                    "author": "Test Author",
                    "email": "test@example.com",
                    "version": "0.1.0",
                },
                "github": {"add_on_github": False},
                "docker": {"docker_image": False, "docker_compose": False},
                "devcontainer": {"enabled": False},
                "ai": {"copilots": {}},
            }
        )

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Step 3: Create project from configuration
        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0
        assert "Project creation completed" in result.output

        # Step 4: Verify project structure
        project_path = Path(temp_project_dir) / "test-integration-lib"
        assert project_path.exists()

    def test_complete_service_project_workflow(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test complete service project creation workflow."""
        # Step 1: Create configuration
        result = runner.invoke(
            app, ["create-config", "service", "--output-path", "service_config.yaml"]
        )
        assert result.exit_code == 0

        config_path = Path(temp_project_dir) / "service_config.yaml"
        assert config_path.exists()

        # Step 2: Modify configuration for testing
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config:
            config = {}

        config.update(
            {
                "project": {
                    "type": "service",
                    "name": "test-integration-service",
                    "description": "Integration test service",
                    "author": "Test Author",
                    "email": "test@example.com",
                    "version": "0.1.0",
                },
                "github": {"add_on_github": False},
                "docker": {"docker_image": True, "docker_compose": True},
                "devcontainer": {"enabled": True},
                "ai": {"copilots": {}},
            }
        )

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Step 3: Create project from configuration
        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0
        assert "Project creation completed" in result.output

        # Step 4: Verify project structure
        project_path = Path(temp_project_dir) / "test-integration-service"
        assert project_path.exists()

    def test_complete_workspace_project_workflow(
        self, temp_project_dir: Path, temp_config_dir: Path
    ):
        """Test complete workspace project creation workflow."""
        # Step 1: Create configuration
        result = runner.invoke(
            app, ["create-config", "workspace", "--output-path", "workspace_config.yaml"]
        )
        assert result.exit_code == 0

        config_path = Path(temp_project_dir) / "workspace_config.yaml"
        assert config_path.exists()

        # Step 2: Modify configuration for testing
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config:
            config = {}

        config.update(
            {
                "project": {
                    "type": "workspace",
                    "name": "test-integration-workspace",
                    "description": "Integration test workspace",
                    "author": "Test Author",
                    "email": "test@example.com",
                    "version": "0.1.0",
                },
                "github": {"add_on_github": False},
                "docker": {"docker_image": False, "docker_compose": False},
                "devcontainer": {"enabled": True},
                "ai": {"copilots": {}},
            }
        )

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Step 3: Create project from configuration
        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0
        assert "Project creation completed" in result.output

        # Step 4: Verify project structure
        project_path = Path(temp_project_dir) / "test-integration-workspace"
        assert project_path.exists()


class TestProjectStructureValidation:
    """Test validation of created project structures."""

    def test_lib_project_structure(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test that library projects have the correct structure."""
        config_data = {
            "project": {
                "type": "lib",
                "name": "structure-test-lib",
                "description": "Structure test library",
                "author": "Test Author",
                "email": "test@example.com",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "structure_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0

        project_path = Path(temp_project_dir) / "structure-test-lib"
        if project_path.exists():
            # Check for expected library structure
            expected_files = [
                "pyproject.toml",
                "README.md",
                "tests/__init__.py",
            ]

            for expected_file in expected_files:
                file_path = project_path / expected_file
                assert file_path.exists(), f"Expected file {expected_file} not found"

    def test_service_project_structure(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test that service projects have the correct structure."""
        config_data = {
            "project": {
                "type": "service",
                "name": "structure-test-service",
                "description": "Structure test service",
                "author": "Test Author",
                "email": "test@example.com",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": True, "docker_compose": True},
            "devcontainer": {"enabled": True},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "service_structure_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0

        project_path = Path(temp_project_dir) / "structure-test-service"
        if project_path.exists():
            # Check for expected service structure
            expected_files = [
                "pyproject.toml",
                "README.md",
                "Dockerfile",
                "docker-compose.yml",
                ".devcontainer/devcontainer.json",
            ]

            for expected_file in expected_files:
                file_path = project_path / expected_file
                assert file_path.exists(), f"Expected file {expected_file} not found"


class TestConfigurationTemplateIntegration:
    """Test integration between configuration templates and project creation."""

    def test_config_template_to_project_consistency(self, temp_project_dir: Path):
        """Test that configuration templates produce consistent projects."""
        project_types = ["lib", "service", "workspace"]

        for project_type in project_types:
            # Create config from template
            result = runner.invoke(
                app, ["create-config", project_type, "--output-path", f"{project_type}_config.yaml"]
            )
            assert result.exit_code == 0

            config_path = Path(temp_project_dir) / f"{project_type}_config.yaml"
            assert config_path.exists()

            # Verify config is valid YAML
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert config is not None

            # Modify config for testing
            if not isinstance(config, dict):
                config = {}

            config.update(
                {
                    "project": {
                        "type": project_type,
                        "name": f"test-{project_type}",
                        "description": f"Test {project_type} project",
                    },
                    "github": {"add_on_github": False},
                    "docker": {"docker_image": project_type == "service", "docker_compose": False},
                    "devcontainer": {"enabled": False},
                    "ai": {"copilots": {}},
                }
            )

            with open(config_path, "w") as f:
                yaml.dump(config, f)

            # Create project from config
            result = runner.invoke(app, ["create-project-from-config", str(config_path)])
            assert result.exit_code == 0, f"Failed to create {project_type} project"


class TestErrorRecoveryIntegration:
    """Test error recovery in integrated workflows."""

    def test_recovery_from_invalid_config(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test recovery from invalid configuration."""
        # Create invalid config
        invalid_config = temp_config_dir / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [")

        # Should fail gracefully
        result = runner.invoke(app, ["create-project-from-config", str(invalid_config)])
        assert result.exit_code == 1

        # Should not leave partial files
        assert not any(Path(temp_project_dir).glob("*"))

    def test_recovery_from_missing_template(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test recovery from missing template files."""
        config_data = {
            "project": {
                "type": "lib",
                "name": "missing-template-test",
                "description": "Missing template test",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "missing_template_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Mock template resolver to simulate missing template
        with mock.patch("pytemplate.project_creator._validate_template") as mock_validate:
            mock_validate.side_effect = ValueError("Template not found")

            result = runner.invoke(app, ["create-project-from-config", str(config_path)])
            assert result.exit_code == 1

            # Should not leave partial files
            project_path = Path(temp_project_dir) / "missing-template-test"
            assert not project_path.exists()


class TestCLIIntegration:
    """Test CLI integration and user experience."""

    def test_help_system_integration(self):
        """Test that help system works correctly."""
        # Test main help
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "pytemplate-uv" in result.output

        # Test command help
        result = runner.invoke(app, ["create-config", "--help"])
        assert result.exit_code == 0
        assert "Create a default configuration file" in result.output

        result = runner.invoke(app, ["create-project-from-config", "--help"])
        assert result.exit_code == 0
        assert "Create a new project from a configuration file" in result.output

    def test_cli_option_combinations(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test various CLI option combinations."""
        config_data = {
            "project": {
                "type": "lib",
                "name": "cli-options-test",
                "description": "CLI options test",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "cli_options_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Test debug flag
        result = runner.invoke(app, ["create-project-from-config", str(config_path), "--debug"])
        assert result.exit_code == 0

        # Test interactive flag
        result = runner.invoke(
            app, ["create-project-from-config", str(config_path), "--interactive"]
        )
        assert result.exit_code == 0

        # Test combined flags
        result = runner.invoke(
            app, ["create-project-from-config", str(config_path), "--debug", "--interactive"]
        )
        assert result.exit_code == 0


class TestExternalToolIntegration:
    """Test integration with external tools (when available)."""


    def test_docker_integration_simulation(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test Docker integration (simulated)."""
        config_data = {
            "project": {
                "type": "service",
                "name": "docker-integration-test",
                "description": "Docker integration test",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": True, "docker_compose": True},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        config_path = temp_config_dir / "docker_integration_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        assert result.exit_code == 0

        # Verify Docker files are created
        project_path = Path(temp_project_dir) / "docker-integration-test"
        if project_path.exists():
            assert (project_path / "Dockerfile").exists()
            assert (project_path / "docker-compose.yml").exists()


class TestPerformanceIntegration:
    """Test performance aspects of integrated workflows."""

    def test_multiple_project_creation_performance(
        self, temp_project_dir: Path, temp_config_dir: Path
    ):
        """Test performance when creating multiple projects."""
        import time

        project_count = 5
        start_time = time.time()

        for i in range(project_count):
            config_data = {
                "project": {
                    "type": "lib",
                    "name": f"perf-test-{i}",
                    "description": f"Performance test project {i}",
                },
                "github": {"add_on_github": False},
                "docker": {"docker_image": False, "docker_compose": False},
                "devcontainer": {"enabled": False},
                "ai": {"copilots": {}},
            }

            config_path = temp_config_dir / f"perf_test_{i}.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = runner.invoke(app, ["create-project-from-config", str(config_path)])
            assert result.exit_code == 0

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert (
            total_time < 30
        ), f"Creating {project_count} projects took {total_time:.2f}s, which is too slow"

    def test_large_config_handling_performance(self, temp_project_dir: Path, temp_config_dir: Path):
        """Test performance with large configuration files."""
        import time

        # Create a large but valid configuration
        config_data = {
            "project": {
                "type": "lib",
                "name": "large-config-perf-test",
                "description": "Large config performance test",
            },
            "github": {"add_on_github": False},
            "docker": {"docker_image": False, "docker_compose": False},
            "devcontainer": {"enabled": False},
            "ai": {"copilots": {}},
        }

        # Add many dummy entries
        for i in range(1000):
            config_data[f"dummy_section_{i}"] = {
                f"dummy_key_{j}": f"dummy_value_{j}" for j in range(10)
            }

        config_path = temp_config_dir / "large_config_perf_test.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        start_time = time.time()
        result = runner.invoke(app, ["create-project-from-config", str(config_path)])
        end_time = time.time()

        processing_time = end_time - start_time

        # Should handle large configs efficiently
        assert (
            processing_time < 10
        ), f"Large config processing took {processing_time:.2f}s, which is too slow"
        assert result.exit_code == 0
