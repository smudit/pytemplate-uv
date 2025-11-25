#!/usr/bin/env python3
"""
Automated migration script for converting projects from 
pytemplate to cookiecutter-uv template structure.
"""

import argparse
import shutil
import subprocess
import sys
import toml
from pathlib import Path
from typing import Dict, List, Optional

import typer
from loguru import logger
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

app = typer.Typer(
    name="migrate-to-uv",
    help="Migrate existing projects from pytemplate to cookiecutter-uv structure",
)
console = Console()


def setup_logger(verbose: bool = False) -> None:
    """Set up logging."""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stdout, level=level, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


@app.command()
def migrate(
    project_path: Path = typer.Argument(..., help="Path to project to migrate"),
    backup: bool = typer.Option(True, help="Create backup before migration"),
    dry_run: bool = typer.Option(False, help="Preview changes without applying"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Migrate a project from old template to cookiecutter-uv."""
    setup_logger(verbose)
    
    logger.info(f"Starting migration for {project_path}")
    
    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        raise typer.Exit(1)
    
    if not (project_path / "pyproject.toml").exists():
        logger.error(f"No pyproject.toml found in {project_path}")
        raise typer.Exit(1)
    
    # Load current pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    try:
        config = toml.load(pyproject_path)
    except Exception as e:
        logger.error(f"Failed to load pyproject.toml: {e}")
        raise typer.Exit(1)
    
    # Detect current template features
    features = detect_features(project_path, config)
    show_feature_detection(features)
    
    if not dry_run and not Confirm.ask("Proceed with migration?"):
        logger.info("Migration cancelled")
        raise typer.Exit(0)
    
    if backup and not dry_run:
        backup_path = create_backup(project_path)
        logger.success(f"Backup created at {backup_path}")
    
    # Migration steps
    steps = [
        ("Update pyproject.toml for uv/hatchling", update_pyproject_toml),
        ("Migrate Makefile commands", migrate_makefile),
        ("Update .gitignore for uv", update_gitignore),
        ("Cleanup old files", cleanup_old_files),
        ("Setup GitHub Actions", setup_github_actions),
        ("Create migration summary", create_migration_summary),
    ]
    
    changes_made = []
    
    for step_name, step_func in steps:
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would execute: {step_name}")
                # For dry run, just analyze what would change
                result = step_func(project_path, config, features, dry_run=True)
            else:
                logger.info(f"Executing: {step_name}")
                result = step_func(project_path, config, features, dry_run=False)
                logger.success(f"✓ Completed: {step_name}")
            
            if result:
                changes_made.extend(result)
                
        except Exception as e:
            logger.error(f"✗ Failed: {step_name} - {e}")
            if not dry_run:
                raise
    
    # Show summary
    if dry_run:
        show_dry_run_summary(changes_made)
    else:
        show_migration_summary(project_path, changes_made)


def detect_features(project_path: Path, config: Dict) -> Dict[str, bool]:
    """Detect which features the current project uses."""
    features = {
        "uses_dynaconf": False,
        "uses_loguru": False,
        "uses_typer": False,
        "uses_rich": False,
        "has_dockerfile": False,
        "has_makefile": False,
        "has_github_actions": False,
        "has_settings_yaml": False,
        "has_secrets_yaml": False,
        "has_claude_md": False,
        "build_system": config.get("build-system", {}).get("build-backend", "unknown"),
    }
    
    # Check dependencies
    deps = config.get("project", {}).get("dependencies", [])
    dev_deps = []
    
    # Check for dev dependencies in different formats
    if "project" in config and "optional-dependencies" in config["project"]:
        for group in config["project"]["optional-dependencies"].values():
            dev_deps.extend(group)
    
    all_deps = deps + dev_deps
    dep_string = " ".join(all_deps)
    
    features["uses_dynaconf"] = "dynaconf" in dep_string
    features["uses_loguru"] = "loguru" in dep_string
    features["uses_typer"] = "typer" in dep_string
    features["uses_rich"] = "rich" in dep_string
    
    # Check for files
    features["has_dockerfile"] = (project_path / "Dockerfile").exists()
    features["has_makefile"] = (project_path / "Makefile").exists()
    features["has_github_actions"] = (project_path / ".github" / "workflows").exists()
    features["has_settings_yaml"] = (project_path / "settings.yaml").exists()
    features["has_secrets_yaml"] = (project_path / ".secrets.yaml").exists()
    features["has_claude_md"] = (project_path / "CLAUDE.md").exists()
    
    return features


def show_feature_detection(features: Dict[str, bool]) -> None:
    """Show detected features in a table."""
    table = Table(title="Detected Project Features")
    table.add_column("Feature", style="cyan")
    table.add_column("Status", style="green")
    
    for feature, enabled in features.items():
        status = "✓ Detected" if enabled else "✗ Not found"
        color = "green" if enabled else "red"
        table.add_row(feature.replace("_", " ").title(), f"[{color}]{status}[/{color}]")
    
    console.print(table)


def create_backup(project_path: Path) -> Path:
    """Create backup of project before migration."""
    backup_path = project_path.parent / f"{project_path.name}_backup_{int(__import__('time').time())}"
    shutil.copytree(project_path, backup_path)
    return backup_path


def update_pyproject_toml(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Update pyproject.toml for uv/hatchling."""
    changes = []
    pyproject_path = project_path / "pyproject.toml"
    
    # Update build system
    if config.get("build-system", {}).get("build-backend") != "hatchling.build":
        changes.append("Updated build-system to use hatchling")
        if not dry_run:
            config["build-system"] = {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build"
            }
    
    # Consolidate ruff configuration
    if "tool" in config and "black" in config["tool"]:
        changes.append("Removed black configuration (consolidated into ruff)")
        if not dry_run:
            config["tool"].pop("black", None)
    
    # Update dependencies to use uv-compatible versions
    if "project" in config and "dependencies" in config["project"]:
        # Ensure core dependencies are present
        deps = config["project"]["dependencies"]
        
        # Update dependency versions for compatibility
        updated_deps = []
        for dep in deps:
            if dep.startswith("python-dotenv"):
                updated_deps.append("python-dotenv>=1.0.0")
                changes.append("Updated python-dotenv version")
            elif dep.startswith("pydantic") and not ">=2." in dep:
                updated_deps.append("pydantic>=2.6.0")
                changes.append("Updated pydantic to v2")
            else:
                updated_deps.append(dep)
        
        if not dry_run:
            config["project"]["dependencies"] = updated_deps
    
    # Write updated config
    if changes and not dry_run:
        with open(pyproject_path, "w") as f:
            toml.dump(config, f)
    
    return changes


def migrate_makefile(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Update Makefile for uv commands."""
    makefile_path = project_path / "Makefile"
    changes = []
    
    if not makefile_path.exists():
        return changes
    
    replacements = {
        "pip install": "uv sync",
        "python -m pytest": "uv run pytest",
        "python -m mypy": "uv run mypy",
        "python -m ruff": "uv run ruff",
        "python -m black": "uv run ruff format",
    }
    
    if not dry_run:
        content = makefile_path.read_text()
        original_content = content
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                changes.append(f"Updated Makefile: {old} → {new}")
        
        if content != original_content:
            makefile_path.write_text(content)
    else:
        content = makefile_path.read_text()
        for old, new in replacements.items():
            if old in content:
                changes.append(f"Would update Makefile: {old} → {new}")
    
    return changes


def update_gitignore(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Update .gitignore for uv."""
    gitignore_path = project_path / ".gitignore"
    changes = []
    
    uv_entries = [
        "# uv",
        ".venv/",
        "uv.lock",
    ]
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "uv.lock" not in content:
            changes.append("Added uv-specific entries to .gitignore")
            if not dry_run:
                content += "\n" + "\n".join(uv_entries) + "\n"
                gitignore_path.write_text(content)
    
    return changes


def cleanup_old_files(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Remove obsolete files from old template."""
    changes = []
    obsolete_files = [
        "setup.py",
        "setup.cfg", 
        "requirements.txt",
        "requirements-dev.txt",
        "MANIFEST.in",
    ]
    
    for file in obsolete_files:
        file_path = project_path / file
        if file_path.exists():
            changes.append(f"Removed obsolete file: {file}")
            if not dry_run:
                file_path.unlink()
    
    return changes


def setup_github_actions(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Set up GitHub Actions workflow for uv."""
    changes = []
    workflows_dir = project_path / ".github" / "workflows"
    
    if features["has_github_actions"]:
        changes.append("GitHub Actions already exists - manual review recommended")
        return changes
    
    workflow_content = '''name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
        
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
      
    - name: Install dependencies
      run: uv sync --all-extras --dev
      
    - name: Run tests
      run: uv run pytest
      
    - name: Run linting
      run: uv run ruff check .
      
    - name: Run type checking
      run: uv run mypy .
'''
    
    if not dry_run:
        workflows_dir.mkdir(parents=True, exist_ok=True)
        (workflows_dir / "ci.yml").write_text(workflow_content)
        changes.append("Created GitHub Actions CI workflow")
    else:
        changes.append("Would create GitHub Actions CI workflow")
    
    return changes


def create_migration_summary(project_path: Path, config: Dict, features: Dict, dry_run: bool = False) -> List[str]:
    """Create a summary of the migration."""
    changes = []
    summary_path = project_path / "MIGRATION_SUMMARY.md"
    
    summary_content = f"""# Migration to cookiecutter-uv Template

## Migration Date
{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Changes Made

### Build System
- Updated from `{features['build_system']}` to `hatchling.build`
- Package management migrated to `uv`

### Dependencies
- All dependencies now managed via `pyproject.toml`
- Removed legacy `requirements.txt` files

### Development Workflow
- Makefile updated to use `uv run` commands
- Added GitHub Actions CI/CD workflow

### Files Removed
- Legacy setup files (setup.py, setup.cfg, etc.)
- Old requirements files

## Next Steps

1. **Verify Dependencies**: Run `uv sync` to ensure all dependencies install correctly
2. **Test Build**: Run `uv build` to verify the package builds
3. **Run Tests**: Execute `uv run pytest` to ensure tests pass
4. **Update Documentation**: Review and update any build/setup instructions
5. **Team Training**: Familiarize team with uv commands

## uv Commands Cheat Sheet

```bash
# Environment setup
uv venv                    # Create virtual environment
source .venv/bin/activate  # Activate environment
uv sync                    # Install all dependencies

# Development
uv add package-name        # Add new dependency
uv remove package-name     # Remove dependency
uv run pytest            # Run tests
uv run ruff check .       # Lint code
uv run mypy .             # Type checking

# Build & Publish
uv build                  # Build package
uv publish               # Publish to PyPI
```

## Migration Validation

- [ ] Dependencies install correctly with `uv sync`
- [ ] Tests pass with `uv run pytest`
- [ ] Linting passes with `uv run ruff check .`
- [ ] Type checking passes with `uv run mypy .`
- [ ] Package builds with `uv build`
- [ ] CI/CD pipeline works (if applicable)

## Rollback Instructions

If needed, you can rollback using the backup created at:
`{project_path.name}_backup_*`

Copy the backup over the current directory to restore the original state.
"""

    if not dry_run:
        summary_path.write_text(summary_content)
        changes.append("Created migration summary document")
    else:
        changes.append("Would create migration summary document")
    
    return changes


def show_dry_run_summary(changes: List[str]) -> None:
    """Show summary of what would be changed in dry run."""
    if not changes:
        console.print("[yellow]No changes would be made[/yellow]")
        return
    
    table = Table(title="Planned Changes (Dry Run)")
    table.add_column("Change", style="cyan")
    
    for change in changes:
        table.add_row(change)
    
    console.print(table)
    console.print(f"\n[bold green]Total planned changes: {len(changes)}[/bold green]")


def show_migration_summary(project_path: Path, changes: List[str]) -> None:
    """Show final migration summary."""
    console.print(f"\n[bold green]✅ Migration completed for {project_path.name}![/bold green]")
    
    if changes:
        table = Table(title="Changes Made")
        table.add_column("Change", style="green")
        
        for change in changes:
            table.add_row(change)
        
        console.print(table)
    
    console.print("\n[bold cyan]Next steps:[/bold cyan]")
    console.print("1. Run `uv sync` to install dependencies")
    console.print("2. Run `uv run pytest` to test")
    console.print("3. Review MIGRATION_SUMMARY.md for details")


@app.command()
def check(
    project_path: Path = typer.Argument(..., help="Path to project to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Check if project is ready for migration."""
    setup_logger(verbose)
    
    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        raise typer.Exit(1)
    
    pyproject_path = project_path / "pyproject.toml"
    if not pyproject_path.exists():
        logger.error(f"No pyproject.toml found in {project_path}")
        raise typer.Exit(1)
    
    config = toml.load(pyproject_path)
    features = detect_features(project_path, config)
    
    show_feature_detection(features)
    
    # Check readiness
    blockers = []
    warnings = []
    
    if not features["has_makefile"]:
        warnings.append("No Makefile found - you may need to update build commands manually")
    
    if features["build_system"] == "setuptools.build_meta":
        logger.info("✓ Current build system is compatible")
    else:
        warnings.append(f"Unusual build system detected: {features['build_system']}")
    
    if blockers:
        console.print("\n[bold red]Migration Blockers:[/bold red]")
        for blocker in blockers:
            console.print(f"  ❌ {blocker}")
        console.print("\n[red]Please resolve these issues before migration.[/red]")
        raise typer.Exit(1)
    
    if warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  ⚠️  {warning}")
    
    console.print("\n[bold green]✅ Project appears ready for migration![/bold green]")
    console.print("Run `migrate-to-uv migrate <path>` to proceed.")


if __name__ == "__main__":
    app()