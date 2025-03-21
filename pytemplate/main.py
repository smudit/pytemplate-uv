"""Command-line interface for creating Python projects from templates."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from .constants import CONFIG_DIR, DEFAULT_USER_CONFIG_DIR, ENV_BASE_DIR
from .logger import logger
from .project_creator import ProjectCreator, create_project
from .template_manager import TemplateManager, TemplateResolver

app = typer.Typer(
    name="pytemplate-uv",
    help="Create Python projects from templates using uv package manager",
    add_completion=True,
    rich_help_panel=True,
)

templates_app = typer.Typer(
    name="templates",
    help="Manage project templates",
    rich_help_panel=True,
)

app.add_typer(templates_app, name="templates")


@app.command()
def create_project_cli(
    project_name: str = typer.Argument(None, help="Name of the project"),
    template: str = typer.Option(
        "pyproject",
        "--template",
        "-t",
        help="Template to use for project creation",
        show_default=True,
    ),
    no_input: bool = typer.Option(
        False, "--no-input", "-y", help="Skip prompts and use default values", show_default=True
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing project directory", show_default=True
    ),
) -> None:
    """Create a new project from a specified template."""
    if force:
        confirm = typer.confirm(
            "Are you sure you want to overwrite the existing project directory?"
        )
        if not confirm:
            logger.info("Operation cancelled.")
            raise typer.Exit()
    create_project(project_name, template, no_input, force)


def path_callback(value: str) -> Path:
    return Path(value)


@app.command()
def create_project_from_config(
    config_path: Annotated[
        Path, typer.Argument(help="Path to the configuration YAML file", callback=path_callback)
    ],
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Enable interactive mode for configuration customization"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing project directory", show_default=True
    ),
) -> None:
    """Create a new project from a configuration file with addons like Docker, devcontainer etc."""
    if debug:
        # Enable debug logging for the entire package
        logger.enable("pytemplate")
        logger.debug("Debug logging enabled")

    if force:
        confirm = typer.confirm(
            "Are you sure you want to overwrite the existing project directory?"
        )
        if not confirm:
            logger.info("Operation cancelled.")
            raise typer.Exit()

    creator = ProjectCreator(config_path, interactive)
    if not creator.create_project_from_config(force=force):
        raise typer.Exit(code=1)
    logger.info("Project creation completed")


def validate_project_type(project_type: str) -> None:
    """Validate the project type."""
    if project_type not in ["lib", "service", "workspace"]:
        logger.error(f"Invalid project type: {project_type}")
        typer.echo(f"Invalid project type: {project_type}. Must be one of: lib, service, workspace")
        raise typer.Exit(code=1)


@app.command()
def create_config(
    project_type: str = typer.Argument(
        ..., help="Type of project (lib/service/workspace)", callback=lambda x: x.lower()
    ),
    output_path: str = typer.Option(
        "project_config.yaml", help="Path where the configuration file will be saved"
    ),
) -> None:
    """Create a default configuration file for the specified project type."""
    validate_project_type(project_type)

    config_template = CONFIG_DIR / f"{project_type}.yaml.template"
    output_path = Path(output_path)

    try:
        if config_template.exists():
            output_path.write_text(config_template.read_text())
            logger.success(f"Created {project_type} configuration from template at: {output_path}")
        else:
            logger.error(f"Configuration template not found: {config_template}")
            raise typer.Exit(code=1) from None
    except Exception as e:
        logger.error(f"Failed to create configuration file: {e}")
        raise typer.Exit(code=1) from e


@templates_app.command("init")
def init_templates(
    base_dir: str | None = typer.Option(
        None,
        "--base-dir",
        "-d",
        help=f"Base directory for templates (default: {DEFAULT_USER_CONFIG_DIR})",
    ),
) -> None:
    """Initialize template directory structure."""
    try:
        if base_dir:
            os.environ[ENV_BASE_DIR] = base_dir

        resolver = TemplateResolver()
        manager = TemplateManager(resolver)

        # Initialize directory structure
        resolver.init_template_structure()
        logger.info("Template directory structure initialized successfully")
        logger.info(f"Base directory: {resolver.base_dir}")

    except Exception as e:
        logger.error(f"Failed to initialize template structure: {e}")
        raise typer.Exit(code=1)


@templates_app.command("list")
def list_templates() -> None:
    """List available templates and their locations."""
    try:
        resolver = TemplateResolver()
        templates = resolver.config["template_paths"]["templates"]

        # Create a simple text-based table for logging
        logger.info("Available templates:")
        logger.info("=" * 80)
        logger.info(f"{'Category':<20} {'Name':<30} {'Path':<30}")
        logger.info("-" * 80)

        for category, category_templates in templates.items():
            for name, path in category_templates.items():
                if isinstance(path, dict):
                    # Handle nested templates
                    for subname, subpath in path.items():
                        full_path = str(resolver.base_dir / subpath)
                        logger.info(f"{category:<20} {f'{name}/{subname}':<30} {full_path:<30}")
                else:
                    full_path = str(resolver.base_dir / path)
                    logger.info(f"{category:<20} {name:<30} {full_path:<30}")

        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise typer.Exit(code=1)


@templates_app.command("copy")
def copy_templates(
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Specific template category to copy. Use with --category/-c flag (e.g. -c project_templates or -c config_templates)",
    ),
) -> None:
    """Copy templates to local directory."""
    try:
        resolver = TemplateResolver()
        manager = TemplateManager(resolver)

        if category:
            logger.info(f"Copying templates for category: {category}")
        else:
            logger.info("Copying all templates")

        manager.copy_templates(category)
        logger.info("Templates copied successfully")

    except Exception as e:
        logger.error(f"Failed to copy templates: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
