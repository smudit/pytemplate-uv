from __future__ import annotations

import os
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import typer
import yaml
from cookiecutter.main import cookiecutter

from .constants import TEMPLATE_PATHS_FILE
from .logger import logger
from .template_manager import TemplateManager, TemplateResolver


def _validate_template(template: str, resolver: TemplateResolver) -> Path:
    """Validate and return the path to the specified template.

    Args:
    ----
        template (str): Name of the project template.
        resolver (TemplateResolver): Template resolver instance.

    Returns:
    -------
        Path: Path to the template directory.

    Raises:
    ------
        typer.BadParameter: If template is not found.

    """
    logger.debug(f"Validating template: {template}")
    try:
        template_path = resolver.get_template_path("project_templates", template)
        logger.info(f"Using template path: {template_path}")
        return template_path
    except ValueError as e:
        # Get available templates from config
        available_templates = list(
            resolver.config["template_paths"]["templates"]["project_templates"].keys()
        )

        error_msg = f"Template not found! Available templates: {', '.join(available_templates)}"
        logger.error(error_msg)
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(code=1)


def _get_context() -> dict[str, str]:
    """Retrieve context variables for project template.

    Returns
    -------
        A dictionary of context variables.

    """
    logger.debug("Retrieving context variables for project template")
    context = {
        "author": os.environ.get("USER", "your name"),
        "email": os.environ.get("USER_EMAIL", "your@email.com"),
        "github_username": os.environ.get("GITHUB_USERNAME", "your_username"),
    }
    logger.debug(f"Context variables: {context}")
    return context


def _create_project_with_cookiecutter(
    template_path: Path, context: dict, no_input: bool, overwrite: bool
) -> str:
    logger.debug(f"Creating project with cookiecutter from template: {template_path}")
    logger.debug(f"Context: {context}, no_input: {no_input}, overwrite: {overwrite}")
    return cookiecutter(
        str(template_path),
        no_input=no_input,
        extra_context=context,
        overwrite_if_exists=overwrite,
    )


def create_project(
    project_name: str | None = None,
    template: str = "pyproject",
    no_input: bool = False,
    force: bool = False,
) -> None:
    """Create a new project from a specified template."""
    logger.info(f"Creating new project with template: {template}")
    if project_name:
        logger.info(f"Project name: {project_name}")
    resolver = TemplateResolver()
    template_path = _validate_template(template, resolver)
    context = _get_context()
    if project_name:
        context["project_name"] = project_name

    try:
        # Use cookiecutter directly instead of subprocess
        output_dir = _create_project_with_cookiecutter(template_path, context, no_input, force)

        if project_name:
            full_path = Path(output_dir).resolve()
            logger.info(f"Project created successfully at {full_path}")
        else:
            logger.info("Project created successfully!")

    except Exception as e:
        logger.error(f"Project creation failed: {str(e)}")
        raise typer.Exit(code=1)


class ProjectCreator:
    def __init__(self, config_path: str, interactive: bool = False):
        """Initialize a new instance of ProjectCreator.

        Args:
        ----
            config_path (str): Path to the YAML configuration file.
            interactive (bool, optional): If True, enable interactive mode (default is False).

        """
        logger.debug(
            f"Initializing ProjectCreator with config_path: {config_path}, interactive: {interactive}"
        )
        self.config_path = Path(config_path)
        self.interactive = interactive
        self.config: dict[str, Any] = {}
        self.project_path: Path | None = None

        # Initialize template management
        self.template_resolver = TemplateResolver(TEMPLATE_PATHS_FILE)
        self.template_manager = TemplateManager(self.template_resolver)
        logger.debug("ProjectCreator initialization complete")

    def load_config(self) -> bool:
        """Load and validate configuration from YAML file.

        Returns
        -------
            bool: True if config was loaded and validated successfully, False otherwise.

        """
        logger.debug(f"Loading config from: {self.config_path}")
        try:
            self.config = yaml.safe_load(self.config_path.read_text())
            logger.debug(f"Config loaded successfully with {len(self.config)} sections")
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {e}")
            raise typer.Exit(f"Config file not found: {str(e)}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise typer.Exit(f"Error parsing YAML: {str(e)}")

        if not self.validate_config():
            logger.error("Invalid configuration")
            raise typer.Exit("Invalid configuration")

        logger.info("Configuration loaded and validated successfully")
        return True

    def _validate_project_name(self) -> bool:
        """Validate the project name for allowed characters and length."""
        project_name = self.config["project"]["name"]
        logger.debug(f"Validating project name: {project_name}")

        # Check length
        if len(project_name) < 1 or len(project_name) > 100:
            logger.error("Project name must be between 1 and 100 characters")
            return False

        # Check for valid characters (letters, numbers, underscore, hyphen)
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            logger.error("Project name can only contain letters, numbers, underscores, and hyphens")
            return False

        logger.debug("Project name validation successful")
        return True

    def validate_config(self) -> bool:
        """Validate the configuration structure."""
        logger.debug("Starting configuration validation")
        if not self._validate_required_sections():
            return False

        if not self._validate_project_type():
            return False

        if not self._validate_docker_settings():
            return False

        if not self._validate_project_name():
            return False

        logger.debug("Configuration validation completed successfully")
        return True

    def _validate_required_sections(self) -> bool:
        required_sections = ["project", "github", "docker", "devcontainer"]
        logger.debug(f"Validating required sections: {required_sections}")
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required section: {section}")
                return False

        # Ensure the ai section exists with defaults if not present
        if "ai" not in self.config:
            logger.debug("AI section not found, adding with default configuration")
            self.config["ai"] = {"copilots": {}}

        logger.debug("Required sections validation successful")
        return True

    def _validate_project_type(self) -> bool:
        project_type = self.config["project"]["type"]
        logger.debug(f"Validating project type: {project_type}")
        if project_type not in ["lib", "workspace", "service"]:
            logger.error("Invalid project type")
            return False
        logger.debug("Project type validation successful")
        return True

    def _validate_docker_settings(self) -> bool:
        project_type = self.config["project"]["type"]
        logger.debug(f"Validating Docker settings for project type: {project_type}")
        if project_type == "lib" and (
            self.config["docker"]["docker_image"] or self.config["docker"]["docker_compose"]
        ):
            logger.error("Libraries should not have Docker configurations")
            return False

        if project_type == "service" and not self.config["docker"]["docker_image"]:
            logger.error("Service projects require Docker image configuration")
            return False
        logger.debug("Docker settings validation successful")
        return True

    def create_project_from_config(self, force: bool = False) -> bool:
        """Create and initialize project addons like docker, devcontainer etc."""
        logger.info("Starting project creation from configuration")
        try:
            # Load and validate config first
            self.load_config()

            project_type = self.config["project"]["type"]
            project_name = self.config["project"]["name"]
            logger.info(f"Creating {project_type} project: {project_name}")

            # For library projects, first create the Python package structure
            if project_type == "lib":
                logger.info("Creating library project structure...")
                template_path = self.template_resolver.get_template_path(
                    "project_templates", "pyproject"
                )
                context = {
                    "project_name": project_name,
                    **_get_context(),
                }

                output_dir = _create_project_with_cookiecutter(
                    template_path, context, not self.interactive, force
                )

                self.project_path = Path(output_dir)
                logger.info(f"Created Python package structure at: {self.project_path}")

                # For lib projects, we're done unless GitHub repo is needed
                if self.config["github"]["add_on_github"]:
                    logger.info("GitHub repository creation requested")
                    if not self.create_github_repo():
                        return False
                logger.info(f"Project created successfully at {self.project_path}")
                return True

            # For non-lib project types (service, workspace), add project structure and addons
            context = {
                "project_name": project_name,
                "project_type": project_type,
                "description": self.config["project"].get("description", ""),
                "version": self.config.get("version", "0.1.0"),
                "python_version": self.config["project"].get("python_version", "3.11"),
                "github": self.config["github"],
                "docker": self.config["docker"],
                "devcontainer": self.config["devcontainer"],
                "service_ports": self.config.get("service_ports", {"ports": ["8000"]}),
            }
            logger.debug(f"Project context: {context}")

            # Get template path for addons and normalize it
            template_path = self.template_resolver.get_template_path(
                "project_templates", "pyproject"
            )

            # Add non-package addons using cookiecutter
            output_dir = _create_project_with_cookiecutter(
                template_path, context, not self.interactive, force
            )

            self.project_path = Path(output_dir)

            # Initialize GitHub repository if requested
            if self.config.get("github", {}).get("add_on_github"):
                logger.info("GitHub repository creation requested")
                if not self.create_github_repo():
                    return False
            if self.config.get("ai", {}).get("copilots"):
                logger.info("AI copilot templates requested")
                if not self.copy_ai_templates():
                    return False
            logger.info(f"Project created successfully at {self.project_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create project addons: {str(e)}")
            return False

    def create_github_repo(self) -> bool:
        """Create a GitHub repository using the GitHub CLI (gh) command.

        Reads the github configuration to determine if the repository should be private.
        Changes to the project directory before running the command and changes back after.
        """

        @contextmanager
        def change_directory(path: Path):
            current_dir = os.getcwd()
            os.chdir(path)
            try:
                yield
            finally:
                os.chdir(current_dir)

        logger.info("Starting GitHub repository creation")
        if not self.project_path:
            logger.error("Project path not set")
            return False

        github_config = self.config.get("github", {})
        repo_name = github_config.get("repo_name", "")
        logger.debug(f"Repository name: {repo_name}")

        if not re.fullmatch(r"^[a-z0-9-_]{1,100}$", repo_name.lower()):
            raise ValueError(
                f"Invalid repository name: {repo_name} - must be 1-100 chars a-z, 0-9, -, _"
            )
        is_private = github_config.get("repo_private", False)
        private_flag = "--private" if is_private else "--public"
        logger.debug(f"Repository visibility: {'private' if is_private else 'public'}")

        try:
            with change_directory(self.project_path):
                logger.info(f"Changed to project directory: {self.project_path}")

                if not (self.project_path / ".git").exists():
                    logger.info("Initializing git repository...")
                    subprocess.check_call(["git", "init"])
                    subprocess.check_call(["git", "add", "."])
                    subprocess.check_call(["git", "commit", "-m", "Initial commit"])

                cmd = ["gh", "repo", "create", repo_name, private_flag, "--source=.", "--push"]
                logger.info(f"Running GitHub command: {' '.join(cmd)}")

                subprocess.check_call(cmd)
                logger.info("GitHub repository created and code pushed successfully")
                return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run GitHub command: {e}")
            return False

    def copy_ai_templates(self) -> bool:
        """Copy AI-related template files based on configuration.

        Returns
        -------
            bool: True if copy operation was successful, False otherwise.

        """
        logger.info("Starting AI template copy operation")
        if not self.project_path:
            logger.error("Project path not set")
            return False

        try:
            ai_config = self.config.get("ai", {})
            copilots_config = ai_config.get("copilots", {})
            if not copilots_config:
                logger.debug("No AI copilot configuration found, skipping template copy")
                return True

            # Try to get the path to coding_rules.md template
            try:
                rules_template = self.template_resolver.get_template_path(
                    "shared", "coding_rules.md"
                )
                logger.debug(f"Found coding rules template at: {rules_template}")

                # Skip the entire process if template file doesn't exist
                if not rules_template.exists():
                    logger.warning("Coding rules template not found, skipping AI rules creation")
                    return True

                rules_content = rules_template.read_text()
                logger.debug("Successfully read coding rules template content")

                # Copy rules for cursor if configured
                cursor_rules_path = copilots_config.get("cursor_rules_path")
                if cursor_rules_path:
                    rules_dir = self.project_path / cursor_rules_path
                    rules_dir.parent.mkdir(parents=True, exist_ok=True)
                    rules_dir.write_text(rules_content)
                    logger.info(f"Copied coding rules to {cursor_rules_path}")

                # Copy rules for cline if configured
                cline_rules_path = copilots_config.get("cline_rules_path")
                if cline_rules_path:
                    rules_file = self.project_path / cline_rules_path
                    rules_file.parent.mkdir(parents=True, exist_ok=True)
                    rules_file.write_text(rules_content)
                    logger.info(f"Copied coding rules to {cline_rules_path}")

            except (ValueError, FileNotFoundError):
                logger.warning("Could not find coding rules template, skipping AI rules creation")
                # Don't create any rules files if template not found
                return True

            logger.info("AI template copy operation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to copy AI templates: {str(e)}")
            return False
