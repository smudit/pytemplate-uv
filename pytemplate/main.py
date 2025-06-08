"""Command-line interface for creating Python projects from templates."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .logger import logger
from .project_creator import ProjectCreator

# Use TemplateResolver to get config template
from .template_manager import TemplateResolver

app = typer.Typer(
    name="pytemplate-uv",
    help="Create Python projects from templates using uv package manager",
    add_completion=True,
    rich_help_panel=True,
)


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
            raise typer.Exit(code=1)

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
    output_path = Path(output_path)

    try:
        resolver = TemplateResolver()

        try:
            config_template_path = resolver.get_template_path("config_templates", project_type)

            if config_template_path.exists():
                output_path.write_text(config_template_path.read_text())
                logger.success(
                    f"Created {project_type} configuration from template at: {output_path}"
                )
            else:
                logger.error(f"Configuration template not found: {config_template_path}")
                raise typer.Exit(code=1) from None

        except ValueError as ve:
            logger.error(f"Configuration template not found in template_paths.yaml: {ve}")
            raise typer.Exit(code=1) from ve

    except Exception as e:
        logger.error(f"Failed to create configuration file: {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
