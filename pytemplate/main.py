"""Command-line interface for creating Python projects from templates."""

from __future__ import annotations

from pathlib import Path

import typer

from .logger import logger
from .project_creator import ProjectCreator, create_project

app = typer.Typer(
    name="pytemplate-uv",
    help="Create Python projects from templates using uv package manager",
    add_completion=True,
    rich_help_panel=True,
)

# Define the directory containing the configuration templates as a global variable.
# This way, the path is not hardcoded deep inside a function.
CONFIG_TEMPLATES_DIR = Path(__file__).parent.parent / "config_templates"


@app.command()
def create_project_cli(
    project_name: str = typer.Argument(None, help="Name of the project"),
    template: str = typer.Option(
        "pyproject", "--template", "-t", help="Template to use for project creation"
    ),
    no_input: bool = typer.Option(
        False, "--no-input", "-y", help="Skip prompts and use default values"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing project directory"),
):
    """Create a new project from a specified template."""
    create_project(project_name, template, no_input, force)


@app.command()
def create_project_from_config(
    config_path: str = typer.Argument(..., help="Path to the configuration YAML file"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Enable interactive mode for configuration customization"
    ),
) -> None:
    """Create a new project from a configuration file with addons like Docker, devcontainer etc."""
    creator = ProjectCreator(config_path, interactive)
    if not creator.create_project_from_config():
        raise typer.Exit(code=1)
    logger.success("Project created successfully!")
    typer.echo("Project created successfully!")


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
    if project_type not in ["lib", "service", "workspace"]:
        logger.error(f"Invalid project type: {project_type}")
        typer.echo(f"Invalid project type: {project_type}. Must be one of: lib, service, workspace")
        raise typer.Exit(code=1)

    # Use the variable CONFIG_TEMPLATES_DIR to build the configuration template path.
    config_template = CONFIG_TEMPLATES_DIR / f"{project_type}.yaml"
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


if __name__ == "__main__":
    app()
