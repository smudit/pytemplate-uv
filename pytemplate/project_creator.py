"""Project creator module for handling project creation and configuration."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

import typer
import yaml
from cookiecutter.main import cookiecutter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .logger import logger

console = Console()


def _validate_template(template: str) -> Path:
    """Validate and return the path to the specified template.

    Args:
    ----
        template (str): Name of the project template.

    Returns:
    -------
        Path: Path to the template directory.

    Raises:
    ------
        typer.BadParameter: If template is not found.

    """
    templates_dir = Path(__file__).parent.parent / "templates"
    template_path = templates_dir / f"{template}-template"

    console.print(f"[yellow]Checking template path: {template_path}[/]")

    if not template_path.exists():
        available_templates = [
            d.name.replace("-template", "") for d in templates_dir.glob("*-template") if d.is_dir()
        ]

        error_text = Text("Template not found!", style="bold red")
        suggestion_text = Text(
            f"\nAvailable templates: {', '.join(available_templates)}", style="yellow"
        )

        console.print(Panel(Text.assemble(error_text, suggestion_text), border_style="red"))
        raise typer.BadParameter(f"Template '{template}' not found")

    console.print(f"[green]Using template path: {template_path}[/]")
    return template_path


def _get_context() -> dict[str, str]:
    """Retrieve context variables for project template.

    Returns
    -------
        A dictionary of context variables.

    """
    return {
        "author": os.environ.get("USER", "your name"),
        "email": os.environ.get("USER_EMAIL", "your@email.com"),
        "github_username": os.environ.get("GITHUB_USERNAME", "your_username"),
    }


def _build_cookiecutter_command(
    template_path: Path, context: dict, no_input: bool = False, force: bool = False
) -> list[str]:
    """Build the cookiecutter command with appropriate options.

    Args:
    ----
        template_path (Path): Path to the project template.
        context (dict): Context variables for the template.
        no_input (bool, optional): If True, skip interactive prompts.
        force (bool, optional): If True, overwrite the existing project directory.

    Returns:
    -------
        list[str]: A list of command arguments.

    """
    cookiecutter_cmd = [
        "cookiecutter",
        str(template_path),
        *[f"{k}={v}" for k, v in context.items()],
    ]

    if no_input:
        cookiecutter_cmd.append("--no-input")

    if force:
        cookiecutter_cmd.append("--overwrite-if-exists")

    return cookiecutter_cmd


def create_project(
    project_name: str | None = None,
    template: str = "pyproject",
    no_input: bool = False,
    force: bool = False,
) -> None:
    """Create a new project from a specified template."""
    template_path = _validate_template(template)
    context = _get_context()
    if project_name:
        context["project_name"] = project_name

    cookiecutter_cmd = _build_cookiecutter_command(template_path, context, no_input, force)

    try:
        result = subprocess.run(cookiecutter_cmd, text=True, check=True)
        logger.info("Project created successfully!")
        console.print("[green]Project created successfully![/]")

        if result.stdout:
            console.print(f"[green]{result.stdout.strip()}[/]")

    except subprocess.CalledProcessError as e:
        logger.error("Project creation failed")
        console.print("[red]Project creation failed:[/]")
        console.print(f"Command: {' '.join(e.cmd)}")

        if e.stdout:
            console.print("[yellow]Standard Output:[/]")
            console.print(e.stdout)

        if e.stderr:
            console.print("[red]Error Output:[/]")
            console.print(e.stderr)

        raise typer.Exit(code=1)  # noqa: B904


class ProjectCreator:
    def __init__(self, config_path: str, interactive: bool = False):
        """Initialize a new instance of ProjectCreator.

        Args:
        ----
            config_path (str): Path to the YAML configuration file.
            interactive (bool, optional): If True, enable interactive mode (default is False).

        """
        self.config_path = Path(config_path)
        self.interactive = interactive
        self.config: dict[str, Any] = {}
        self.project_path: Path | None = None

    def load_config(self) -> bool:
        """Load and validate configuration from YAML file.

        Returns
        -------
            bool: True if config was loaded and validated successfully, False otherwise.

        """
        try:
            self.config = yaml.safe_load(self.config_path.read_text())
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {e}")
            raise typer.Exit(f"Config file not found: {str(e)}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise typer.Exit(f"Error parsing YAML: {str(e)}")

        if not self.validate_config():
            logger.error("Invalid configuration")
            raise typer.Exit("Invalid configuration")

        return True

    def _validate_project_name(self) -> bool:
        """Validate the project name for allowed characters and length."""
        project_name = self.config["project"]["name"]

        # Check length
        if len(project_name) < 1 or len(project_name) > 100:
            logger.error("Project name must be between 1 and 100 characters")
            return False

        # Check for valid characters (letters, numbers, underscore, hyphen)
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            logger.error("Project name can only contain letters, numbers, underscores, and hyphens")
            return False

        return True

    def validate_config(self) -> bool:
        """Validate the configuration structure."""
        if not self._validate_required_sections():
            return False

        if not self._validate_project_type():
            return False

        if not self._validate_docker_settings():
            return False

        if not self._validate_project_name():
            return False

        return True

    def _validate_required_sections(self) -> bool:
        required_sections = ["project", "github", "docker", "devcontainer"]
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required section: {section}")
                return False
        return True

    def _validate_project_type(self) -> bool:
        project_type = self.config["project"]["type"]
        if project_type not in ["lib", "workspace", "service"]:
            logger.error("Invalid project type")
            return False
        return True

    def _validate_docker_settings(self) -> bool:
        project_type = self.config["project"]["type"]
        if project_type == "lib" and (
            self.config["docker"]["docker_image"] or self.config["docker"]["docker_compose"]
        ):
            logger.error("Libraries should not have Docker configurations")
            return False

        if project_type == "service" and not self.config["docker"]["docker_image"]:
            logger.error("Service projects require Docker image configuration")
            return False
        return True

    def create_project_from_config(self) -> bool:
        """Create and initialize project addons like docker, devcontainer etc."""
        try:
            # Load and validate config first
            self.load_config()

            project_type = self.config["project"]["type"]
            project_name = self.config["project"]["name"]
            logger.info(f"Creating {project_type} project: {project_name}")

            # For library projects, first create the Python package structure
            if project_type == "lib":
                logger.info("Creating library project structure...")
                create_project(
                    project_name=project_name,
                    template="pyproject",  # _validate_template will append "-template"
                    no_input=not self.interactive,
                    force=True,
                )
                self.project_path = Path(project_name)
                logger.info(f"Created Python package structure at: {self.project_path}")

                # Return early for lib projects since they don't need additional addons
                if self.config["github"]["add_on_github"]:
                    self.create_github_repo()
                return True

                # For non-lib project types (service, workspace), add project structure and addons
                # Prepare cookiecutter context for addons
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

                # Get template path for addons
                template_path = str(Path(__file__).parent.parent / "templates" / "project-template")

                # Add non-package addons using cookiecutter
                output_dir = cookiecutter(
                    template_path,
                    no_input=not self.interactive,
                    extra_context=context,
                    overwrite_if_exists=True,
                )

                self.project_path = Path(output_dir)
                logger.info(f"Project addons created at: {self.project_path}")

            # Initialize GitHub repository if requested
            if self.config["github"]["add_on_github"]:
                self.create_github_repo()

            return True

        except Exception as e:
            logger.error(f"Failed to create project addons: {str(e)}")
            return False

    def create_github_repo(self) -> bool:
        """Create a GitHub repository using the GitHub CLI (gh) command.

        Reads the github configuration to determine if the repository should be private.
        """
        github_config = self.config.get("github", {})
        github_config = self.config.get("github", {})
        repo_name = github_config.get("repo_name", "")
        is_private = github_config.get("repo_private", False)
        private_flag = "--private" if is_private else "--public"

        # Build the GitHub CLI command. Adjust additional flags as needed.
        cmd = ["gh", "repo", "create", repo_name, private_flag, "--source=.", "--push"]
        logger.info(f"Running GitHub command: {' '.join(cmd)}")

        try:
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run GitHub command: {e}")
            return False
