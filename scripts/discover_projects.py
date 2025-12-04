#!/usr/bin/env python3
"""
Project Discovery Script

Discovers projects using the old template and generates a migration inventory.
Searches for template markers (Dynaconf, Loguru, Typer) in local directories
or GitHub organization repositories.

Usage:
    # Local directory search
    python discover_projects.py local /path/to/projects

    # GitHub organization search (requires gh CLI)
    python discover_projects.py github your-org

    # Output to file
    python discover_projects.py local /path/to/projects --output inventory.yaml
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Note: Install typer and rich for better output: uv add typer rich")

# Template markers to search for
TEMPLATE_MARKERS = [
    "from dynaconf import",
    "from loguru import",
    "import typer",
    "from config import settings",
    "setup_logger",
    "Dynaconf(",
]

# Files that indicate old template
OLD_TEMPLATE_FILES = [
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "requirements-dev.txt",
]

# Files that indicate new template
NEW_TEMPLATE_FILES = [
    "uv.lock",
]


@dataclass
class ProjectInfo:
    """Information about a discovered project."""

    name: str
    path: str
    status: str = "unknown"  # active, maintenance, legacy
    last_modified: str = ""
    python_version: str = ""
    has_tests: bool = False
    has_ci: bool = False
    uses_old_template: bool = False
    uses_new_template: bool = False
    template_markers: list = field(default_factory=list)
    migration_priority: str = "medium"
    notes: str = ""


def run_command(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_file_exists(project_path: Path, filename: str) -> bool:
    """Check if a file exists in the project."""
    return (project_path / filename).exists()


def search_for_markers(project_path: Path) -> list[str]:
    """Search project for template markers."""
    found_markers = []

    # Search Python files
    for py_file in project_path.rglob("*.py"):
        # Skip venv and cache directories
        if any(
            part in py_file.parts
            for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
        ):
            continue

        try:
            content = py_file.read_text(errors="ignore")
            for marker in TEMPLATE_MARKERS:
                if marker in content and marker not in found_markers:
                    found_markers.append(marker)
        except Exception:
            continue

    return found_markers


def get_last_commit_date(project_path: Path) -> str:
    """Get the date of the last git commit."""
    code, stdout, _ = run_command(
        ["git", "log", "-1", "--format=%Y-%m-%d"], cwd=str(project_path)
    )
    if code == 0 and stdout.strip():
        return stdout.strip()
    return ""


def get_python_version(project_path: Path) -> str:
    """Extract Python version from pyproject.toml or setup files."""
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            # Look for requires-python
            for line in content.split("\n"):
                if "requires-python" in line.lower():
                    # Extract version
                    if ">=" in line:
                        version = line.split(">=")[1].strip().strip('"').strip("'")
                        return version.split(",")[0].strip()
        except Exception:
            pass
    return ""


def determine_status(last_modified: str) -> str:
    """Determine project status based on last modification date."""
    if not last_modified:
        return "unknown"

    try:
        last_date = datetime.strptime(last_modified, "%Y-%m-%d")
        days_ago = (datetime.now() - last_date).days

        if days_ago < 30:
            return "active"
        elif days_ago < 180:
            return "maintenance"
        else:
            return "legacy"
    except Exception:
        return "unknown"


def analyze_project(project_path: Path) -> ProjectInfo | None:
    """Analyze a single project directory."""
    if not project_path.is_dir():
        return None

    # Must have pyproject.toml or setup.py to be a Python project
    if not (
        check_file_exists(project_path, "pyproject.toml")
        or check_file_exists(project_path, "setup.py")
    ):
        return None

    info = ProjectInfo(name=project_path.name, path=str(project_path))

    # Check for template markers
    info.template_markers = search_for_markers(project_path)

    # If no markers found, probably not using our template
    if not info.template_markers:
        return None

    # Check for old vs new template indicators
    info.uses_old_template = any(
        check_file_exists(project_path, f) for f in OLD_TEMPLATE_FILES
    )
    info.uses_new_template = any(
        check_file_exists(project_path, f) for f in NEW_TEMPLATE_FILES
    )

    # Get additional info
    info.last_modified = get_last_commit_date(project_path)
    info.status = determine_status(info.last_modified)
    info.python_version = get_python_version(project_path)
    info.has_tests = check_file_exists(project_path, "tests") or check_file_exists(
        project_path, "test"
    )
    info.has_ci = check_file_exists(project_path, ".github/workflows")

    # Determine migration priority
    if info.uses_new_template:
        info.migration_priority = "none"
        info.notes = "Already using new template"
    elif info.status == "active":
        info.migration_priority = "high"
    elif info.status == "maintenance":
        info.migration_priority = "medium"
    else:
        info.migration_priority = "low"

    return info


def discover_local(base_path: Path, max_depth: int = 2) -> list[ProjectInfo]:
    """Discover projects in local directories."""
    projects = []

    # Check if base_path itself is a project
    info = analyze_project(base_path)
    if info:
        projects.append(info)

    # Search subdirectories
    if max_depth > 0:
        for item in base_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Check this directory
                info = analyze_project(item)
                if info:
                    projects.append(info)

                # Recurse into subdirectories
                if max_depth > 1:
                    for subitem in item.iterdir():
                        if subitem.is_dir() and not subitem.name.startswith("."):
                            info = analyze_project(subitem)
                            if info:
                                projects.append(info)

    return projects


def discover_github(org: str, limit: int = 100) -> list[ProjectInfo]:
    """Discover projects in a GitHub organization."""
    projects = []

    # Get list of repos
    code, stdout, stderr = run_command(
        ["gh", "repo", "list", org, "--limit", str(limit), "--json", "name,url"]
    )

    if code != 0:
        print(f"Error listing repos: {stderr}")
        print("Make sure you have gh CLI installed and authenticated")
        return []

    try:
        repos = json.loads(stdout)
    except json.JSONDecodeError:
        print("Error parsing GitHub response")
        return []

    print(f"Found {len(repos)} repositories in {org}")

    for repo in repos:
        name = repo["name"]
        print(f"  Checking {name}...", end=" ")

        # Search for markers in repo
        found_markers = []
        for marker in TEMPLATE_MARKERS[:3]:  # Check first 3 markers only (API limits)
            code, stdout, _ = run_command(
                [
                    "gh",
                    "api",
                    f"search/code?q={marker}+repo:{org}/{name}",
                    "--jq",
                    ".total_count",
                ]
            )
            if code == 0 and stdout.strip() != "0":
                found_markers.append(marker)

        if found_markers:
            print("uses template")
            info = ProjectInfo(
                name=name,
                path=f"https://github.com/{org}/{name}",
                template_markers=found_markers,
                notes="Discovered via GitHub search",
            )
            projects.append(info)
        else:
            print("skip")

    return projects


def output_table(projects: list[ProjectInfo]) -> None:
    """Output projects as a rich table."""
    if not HAS_RICH:
        # Fallback to simple output
        print("\nDiscovered Projects:")
        print("-" * 80)
        for p in projects:
            status_icon = (
                "🟢" if p.status == "active" else "🟡" if p.status == "maintenance" else "🔴"
            )
            template_status = "✅ New" if p.uses_new_template else "⚠️ Old" if p.uses_old_template else "❓"
            print(f"{status_icon} {p.name} [{p.migration_priority}] {template_status}")
        return

    console = Console()
    table = Table(title="Discovered Projects Using Template")

    table.add_column("Project", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Last Modified")
    table.add_column("Template")
    table.add_column("Priority", style="yellow")
    table.add_column("Tests", style="green")
    table.add_column("CI", style="blue")

    for p in projects:
        status_icon = (
            "🟢 Active" if p.status == "active"
            else "🟡 Maint" if p.status == "maintenance"
            else "🔴 Legacy"
        )
        template_status = (
            "✅ New" if p.uses_new_template
            else "⚠️ Old" if p.uses_old_template
            else "❓ Unknown"
        )
        priority_style = (
            "[red]HIGH[/red]" if p.migration_priority == "high"
            else "[yellow]MEDIUM[/yellow]" if p.migration_priority == "medium"
            else "[green]LOW[/green]" if p.migration_priority == "low"
            else "[dim]NONE[/dim]"
        )

        table.add_row(
            p.name,
            status_icon,
            p.last_modified or "N/A",
            template_status,
            priority_style,
            "✓" if p.has_tests else "✗",
            "✓" if p.has_ci else "✗",
        )

    console.print(table)


def output_yaml(projects: list[ProjectInfo], output_path: Path) -> None:
    """Output projects as YAML file."""
    lines = ["# Project Migration Inventory", f"# Generated: {datetime.now().isoformat()}", ""]

    # Group by priority
    by_priority = {"high": [], "medium": [], "low": [], "none": []}
    for p in projects:
        by_priority.get(p.migration_priority, by_priority["medium"]).append(p)

    lines.append("high_priority:")
    for p in by_priority["high"]:
        lines.extend(_project_to_yaml(p))

    lines.append("\nmedium_priority:")
    for p in by_priority["medium"]:
        lines.extend(_project_to_yaml(p))

    lines.append("\nlow_priority:")
    for p in by_priority["low"]:
        lines.extend(_project_to_yaml(p))

    lines.append("\nalready_migrated:")
    for p in by_priority["none"]:
        lines.extend(_project_to_yaml(p))

    output_path.write_text("\n".join(lines))
    print(f"\nInventory written to: {output_path}")


def _project_to_yaml(p: ProjectInfo) -> list[str]:
    """Convert project info to YAML lines."""
    return [
        f"  - name: {p.name}",
        f"    path: {p.path}",
        f"    status: {p.status}",
        f"    last_modified: {p.last_modified}",
        f"    python_version: {p.python_version}",
        f"    has_tests: {str(p.has_tests).lower()}",
        f"    has_ci: {str(p.has_ci).lower()}",
        f"    uses_old_template: {str(p.uses_old_template).lower()}",
        f"    uses_new_template: {str(p.uses_new_template).lower()}",
        f"    markers: {p.template_markers}",
        f"    notes: {p.notes}",
        "",
    ]


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    target = sys.argv[2]
    output_file = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = Path(sys.argv[idx + 1])

    if mode == "local":
        base_path = Path(target).expanduser().resolve()
        if not base_path.exists():
            print(f"Error: Path does not exist: {base_path}")
            sys.exit(1)

        print(f"Scanning {base_path} for projects...")
        projects = discover_local(base_path)

    elif mode == "github":
        print(f"Scanning GitHub organization: {target}")
        projects = discover_github(target)

    else:
        print(f"Unknown mode: {mode}")
        print("Use 'local' or 'github'")
        sys.exit(1)

    if not projects:
        print("No projects found using the template.")
        sys.exit(0)

    print(f"\nFound {len(projects)} project(s) using the template\n")

    # Output results
    output_table(projects)

    if output_file:
        output_yaml(projects, output_file)

    # Summary
    needs_migration = [p for p in projects if p.migration_priority in ("high", "medium", "low")]
    already_done = [p for p in projects if p.migration_priority == "none"]

    print(f"\nSummary:")
    print(f"  Need migration: {len(needs_migration)}")
    print(f"  Already migrated: {len(already_done)}")
    print(f"  High priority: {len([p for p in projects if p.migration_priority == 'high'])}")
    print(f"  Medium priority: {len([p for p in projects if p.migration_priority == 'medium'])}")
    print(f"  Low priority: {len([p for p in projects if p.migration_priority == 'low'])}")


if __name__ == "__main__":
    main()
