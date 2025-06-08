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
        
        # Check if the template path exists
        if not template_path.exists():
            # Try to find the template in the package directory
            package_dir = Path(__file__).parent
            
            # First try with the template name as is
            alternative_path = package_dir / "templates" / f"{template}-template"
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path
                
            # If that doesn't work, try with just the template name
            alternative_path = package_dir / "templates" / template
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path
                
            # If that still doesn't work, try with the full template path name
            template_name = template_path.name
            alternative_path = package_dir / "templates" / template_name
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path
                
            logger.error(f"Template path not found at: {template_path} or alternatives")
            raise ValueError(f"Template path not found: {template_path}")
                
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
    template_path: Path,
    context: dict,
    no_input: bool,
    overwrite: bool,
    template_resolver: TemplateResolver,
) -> str:
    logger.debug(f"Creating project with cookiecutter from template: {template_path}")

    try:
        if context.get("project", {}).get("type") == "lib":
            # Get the library template path from config
            lib_template = template_resolver.get_template_path("project_templates", "pylibrary")
            dev_settings = context.get("development", {})

            # Get repo_name from github config or derive it from project_name
            # This will override the template's default behavior of adding "python-" prefix
            repo_name = context["github"].get("repo_name")
            if not repo_name:
                # If repo_name is not specified, derive it from project_name
                repo_name = context["project"]["name"].replace("_", "-")
                logger.info(f"Derived repo_name from project_name: {repo_name}")

            cookiecutter_context = {
                # Project settings
                "project_name": context["project"]["name"],
                "repo_name": repo_name,  # Explicitly set repo_name to override template's default
                "package_name": context["project"]["name"].replace("-", "_"),
                "full_name": context["project"].get("author", "your name"),
                "email": context["project"].get("email", "your.email@example.com"),
                "github_username": context["github"].get("github_username", "your-github-username"),
                "version": context["project"].get("version", "0.1.0"),
                "license": context["project"].get("license", "MIT"),
                # Development settings mapped from lib.yaml.template
                "test_runner": "pytest" if dev_settings.get("use_pytest", True) else "nose",
                "test_matrix_separate_coverage": dev_settings.get(
                    "test_matrix_separate_coverage", False
                ),
                "test_matrix_configurator": dev_settings.get("test_matrix_configurator", False),
                "sphinx_docs": "yes" if dev_settings.get("use_sphinx", True) else "no",
                "sphinx_theme": dev_settings.get("sphinx_theme", "sphinx-rtd-theme"),
                "sphinx_doctest": "yes" if dev_settings.get("sphinx_doctest", False) else "no",
                "sphinx_docs_hosting": dev_settings.get("sphinx_docs_hosting", "readthedocs.io"),
                "codecov": "yes" if dev_settings.get("use_codecov", True) else "no",
                "coveralls": "yes" if dev_settings.get("use_coveralls", False) else "no",
                "scrutinizer": "yes" if dev_settings.get("use_scrutinizer", False) else "no",
                "codacy": "yes" if dev_settings.get("use_codacy", False) else "no",
                "codeclimate": "yes" if dev_settings.get("use_codeclimate", False) else "no",
                "command_line_interface": dev_settings.get("command_line_interface", "no"),
                "command_line_interface_bin_name": dev_settings.get("command_line_bin_name", ""),
                "pypi_badge": "yes" if dev_settings.get("pypi_badge", True) else "no",
                "pypi_disable_upload": "yes"
                if dev_settings.get("pypi_disable_upload", False)
                else "no",
            }

            return _execute_cookiecutter(lib_template, no_input, cookiecutter_context, overwrite)

        return _execute_cookiecutter(template_path, no_input, context, overwrite)
    except Exception as e:
        if "already exists" in str(e):
            logger.warning("Directory already exists")
            if typer.confirm(
                "\nDirectory already exists. Do you want to overwrite?", default=False
            ):
                logger.info("User confirmed overwrite, retrying...")
                if context.get("project", {}).get("type") == "lib":
                    return _execute_cookiecutter(lib_template, no_input, cookiecutter_context, True)
                return _execute_cookiecutter(template_path, no_input, context, True)
            else:
                logger.info("User chose not to overwrite. Exiting.")
                raise typer.Exit(1)
        raise


def _execute_cookiecutter(
    template_path: Path, no_input: bool, context: dict, overwrite: bool
) -> str:
    """Helper function to execute cookiecutter with consistent parameters."""
    return cookiecutter(
        str(template_path),
        no_input=no_input,
        extra_context=context,
        overwrite_if_exists=overwrite,
    )


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

    def _validate_development_settings(self) -> bool:
        """Validate development settings."""
        dev_settings = self.config.get("development", {})
        cli_interface = dev_settings.get("command_line_interface", "no")
        valid_cli_options = ["no", "click", "argparse", "plain"]

        if cli_interface not in valid_cli_options:
            logger.error(f"Invalid command line interface option: {cli_interface}")
            logger.error(f"Valid options are: {', '.join(valid_cli_options)}")
            return False

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

        if not self._validate_development_settings():
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

            # For library projects, use the pylibrary template
            if project_type == "lib":
                logger.info("Creating library project structure...")
                template_path = _validate_template("pylibrary", self.template_resolver)
                context = {
                    "project_name": project_name,
                    **_get_context(),
                    **self.config,  # Include all config settings
                }

                output_dir = _create_project_with_cookiecutter(
                    template_path, context, not self.interactive, force, self.template_resolver
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
                "author": self.config["project"].get("author", ""),
                "email": self.config["project"].get("email", ""),
                "version": self.config.get("version", "0.1.0"),
                "python_version": self.config["project"].get("python_version", "3.11"),
                "github": self.config["github"],
                "docker": self.config["docker"],
                "devcontainer": self.config["devcontainer"],
                "service_ports": self.config.get("service_ports", {"ports": ["8000"]}),
            }
            logger.debug(f"Project context: {context}")

            # Get template path for addons and validate it
            template_path = _validate_template("pyproject", self.template_resolver)

            # Add non-package addons using cookiecutter
            output_dir = _create_project_with_cookiecutter(
                template_path, context, not self.interactive, force, self.template_resolver
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
                    logger.info("Initializing git repository with main branch...")
                    subprocess.check_call(
                        ["git", "init", "-b", "main"]
                    )  # Initialize with main branch
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
                rules_template = self.template_resolver.get_template_path("shared", "coding_rules")
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
