# Migration Plan: pytemplate → cookiecutter-uv

## Project Overview
**Migration Goal**: Transition from current `pytemplate/templates/pyproject-template/` to `cookiecutter-uv` template  
**Timeline**: 5 weeks  
**Start Date**: TBD  
**Migration Lead**: TBD  

## Week 1: Preparation & Analysis

### Tasks
- [ ] Create git branch `legacy-template-backup` for current template
- [ ] Archive current template structure in `archive/` directory
- [ ] Document all custom modifications in current template
- [ ] Complete gap analysis between current and target template
- [ ] Identify team-specific requirements not covered by cookiecutter-uv
- [ ] List all projects currently using the template

### Deliverables
- Backup of current template
- Gap analysis document
- List of affected projects
- Team requirements document

## Week 2: Customization & Development

### Tasks
- [ ] Fork cookiecutter-uv repository
- [ ] Add Dynaconf configuration system to forked template
- [ ] Integrate Loguru logging setup
- [ ] Port Typer CLI structure from current template
- [ ] Add CLAUDE.md coding rules integration
- [ ] Configure custom cookiecutter variables
- [ ] Create post-generation hooks for custom features

### Custom Features to Add
```python
# cookiecutter.json modifications
{
  "use_dynaconf": ["y", "n"],
  "use_loguru": ["y", "n"],
  "use_typer_cli": ["y", "n"],
  "include_claude_rules": ["y", "n"]
}
```

### Deliverables
- Forked and customized cookiecutter-uv template
- Post-generation hooks for custom features
- Updated cookiecutter.json configuration

## Week 3: Testing & Validation

### Test Projects
1. **Basic Project Generation**
   - [ ] Generate project with minimal features
   - [ ] Generate project with all features enabled
   - [ ] Validate uv commands work correctly
   
2. **Feature Testing**
   - [ ] Test Dynaconf integration
   - [ ] Test Loguru logging
   - [ ] Test Typer CLI structure
   - [ ] Test pre-commit hooks
   - [ ] Test GitHub Actions workflows
   - [ ] Test MkDocs documentation generation

3. **Migration Testing**
   - [ ] Select 3 pilot projects for migration testing
   - [ ] Run migration script on pilot projects
   - [ ] Validate CI/CD pipelines
   - [ ] Test Python 3.9-3.13 compatibility

### Test Commands
```bash
# Generate test project
cookiecutter gh:your-org/cookiecutter-uv-custom

# Validate project
cd test-project/
uv venv
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run tox
```

### Deliverables
- Test report for all features
- Migration script validation results
- CI/CD pipeline test results

## Week 4: Documentation & Training

### Documentation Tasks
- [ ] Create comprehensive migration guide
- [ ] Update README with new template usage
- [ ] Document breaking changes
- [ ] Create uv command cheat sheet
- [ ] Develop training materials
- [ ] Create troubleshooting guide
- [ ] Set up support channel (#template-migration)

### Training Materials
1. **Quick Start Guide**
   - Basic uv commands
   - Project setup workflow
   - Development workflow

2. **Migration Guide**
   - Step-by-step migration process
   - Common issues and solutions
   - Rollback procedures

3. **Video Tutorials**
   - Template usage walkthrough
   - Migration process demonstration
   - CI/CD setup guide

### Deliverables
- Complete documentation set
- Training materials
- Support channel setup
- FAQ document

## Week 5: Rollout & Migration

### Rollout Strategy
1. **Phase 1: New Projects (Immediate)**
   - All new projects use cookiecutter-uv template
   - Provide support for early adopters
   
2. **Phase 2: Active Projects (Week 5-8)**
   - Migrate high-priority active development projects
   - Provide hands-on support during migration
   
3. **Phase 3: Maintenance Projects (Week 9-12)**
   - Migrate medium-priority maintenance mode projects
   - Automated migration with minimal support
   
4. **Phase 4: Legacy Projects (Month 4+)**
   - Evaluate need for migration
   - Archive or migrate as needed

### Migration Execution
- [ ] Deploy new template to production
- [ ] Begin new project creation with new template
- [ ] Start pilot project migrations
- [ ] Monitor and collect feedback
- [ ] Address urgent issues
- [ ] Update documentation based on feedback

### Deliverables
- New template in production
- Successful pilot migrations
- Feedback collection system
- Issue tracking setup

## Post-Migration (Week 6+)

### Monitoring & Support
- [ ] Daily monitoring for first week
- [ ] Weekly team check-ins for first month
- [ ] Collect and address feedback
- [ ] Track migration metrics
- [ ] Update documentation based on learnings

### Continuous Improvement
- [ ] Set up monthly sync with upstream cookiecutter-uv
- [ ] Implement team feedback
- [ ] Optimize migration scripts
- [ ] Update training materials

### Deprecation
- [ ] Mark old template as deprecated (Month 1)
- [ ] Set sunset date (Month 6)
- [ ] Final migration push (Month 5)
- [ ] Archive old template (Month 6)

## Risk Management

### Identified Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Learning curve for uv** | Medium | High | Comprehensive training, cheat sheets, support channel |
| **Tool compatibility issues** | Low | Medium | Maintain pip fallback instructions |
| **Loss of custom features** | High | Low | Custom fork with all features integrated |
| **CI/CD pipeline failures** | High | Medium | Thorough testing, gradual rollout |
| **Project migration failures** | High | Low | Backup strategy, rollback procedures |

## Success Metrics

### Key Performance Indicators
- [ ] 100% new projects using new template (Week 5)
- [ ] 80% active projects migrated (Month 3)
- [ ] <5% rollback rate
- [ ] >90% developer satisfaction score
- [ ] <10% increase in build times
- [ ] Zero critical production incidents

### Monitoring Dashboard
- Template usage statistics
- Migration progress tracker
- Issue/incident tracker
- Developer feedback scores
- Build performance metrics

## Migration Script

```python
#!/usr/bin/env python3
"""
Automated migration script for converting projects from 
pytemplate to cookiecutter-uv template structure.
"""

import shutil
import subprocess
from pathlib import Path
import toml
import typer
from loguru import logger

app = typer.Typer()

@app.command()
def migrate(
    project_path: Path = typer.Argument(..., help="Path to project to migrate"),
    backup: bool = typer.Option(True, help="Create backup before migration"),
    dry_run: bool = typer.Option(False, help="Preview changes without applying")
):
    """Migrate a project from old template to cookiecutter-uv."""
    
    logger.info(f"Starting migration for {project_path}")
    
    if backup and not dry_run:
        backup_path = create_backup(project_path)
        logger.success(f"Backup created at {backup_path}")
    
    # Migration steps
    steps = [
        update_pyproject_toml,
        migrate_makefile,
        setup_github_actions,
        migrate_documentation,
        update_gitignore,
        cleanup_old_files
    ]
    
    for step in steps:
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would execute: {step.__name__}")
            else:
                step(project_path)
                logger.success(f"✓ Completed: {step.__name__}")
        except Exception as e:
            logger.error(f"✗ Failed: {step.__name__} - {e}")
            if not dry_run:
                raise
    
    if not dry_run:
        logger.success(f"Migration complete for {project_path.name}")
    else:
        logger.info("Dry run complete - no changes made")

def create_backup(project_path: Path) -> Path:
    """Create backup of project before migration."""
    backup_path = project_path.parent / f"{project_path.name}_backup"
    shutil.copytree(project_path, backup_path)
    return backup_path

def update_pyproject_toml(project_path: Path):
    """Update pyproject.toml for uv/hatchling."""
    pyproject_path = project_path / "pyproject.toml"
    config = toml.load(pyproject_path)
    
    # Update build system
    config["build-system"] = {
        "requires": ["hatchling"],
        "build-backend": "hatchling.build"
    }
    
    # Consolidate ruff configuration
    if "tool.ruff" in config:
        config["tool.ruff"]["format"] = {"quote-style": "double"}
        config.pop("tool.black", None)
    
    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

def migrate_makefile(project_path: Path):
    """Update Makefile for uv commands."""
    makefile_path = project_path / "Makefile"
    if not makefile_path.exists():
        return
    
    replacements = {
        "pip install": "uv sync",
        "python -m": "uv run python -m",
        "pytest": "uv run pytest",
        "black": "uv run ruff format",
        "mypy": "uv run mypy"
    }
    
    content = makefile_path.read_text()
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    makefile_path.write_text(content)

def setup_github_actions(project_path: Path):
    """Add GitHub Actions workflows."""
    workflows_dir = project_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy workflows from template
    # Implementation depends on template location

def migrate_documentation(project_path: Path):
    """Migrate from pdoc to MkDocs."""
    # Create mkdocs.yml
    # Move documentation files
    # Update README links
    pass

def update_gitignore(project_path: Path):
    """Update .gitignore for uv."""
    gitignore = project_path / ".gitignore"
    additions = [
        "\n# uv",
        ".venv/",
        "uv.lock"
    ]
    
    with open(gitignore, "a") as f:
        f.write("\n".join(additions))

def cleanup_old_files(project_path: Path):
    """Remove obsolete files from old template."""
    obsolete_files = [
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt"
    ]
    
    for file in obsolete_files:
        file_path = project_path / file
        if file_path.exists():
            file_path.unlink()

if __name__ == "__main__":
    app()
```

## Command Reference

### Old Template Commands
```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Development
make lint
make format
make test
python -m mypy .
```

### New Template Commands
```bash
# Setup
uv venv
source .venv/bin/activate
uv sync

# Development
uv run ruff check .
uv run ruff format .
uv run pytest
uv run mypy .
uv run tox

# Build & Publish
uv build
uv publish
```

## Contact & Support

- **Migration Lead**: TBD
- **Support Channel**: #template-migration
- **Documentation**: [Internal Wiki]
- **Issue Tracking**: GitHub Issues
- **Office Hours**: Tuesdays & Thursdays, 2-3 PM

## Appendix

### Resource Links
- [cookiecutter-uv Repository](https://github.com/fpgmaas/cookiecutter-uv)
- [uv Documentation](https://docs.astral.sh/uv/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Hatchling Documentation](https://hatch.pypa.io/)

### Migration Checklist

#### Pre-Migration
- [ ] Management approval
- [ ] Team notification
- [ ] Resource allocation
- [ ] Timeline confirmation

#### Week 1
- [ ] Template backup created
- [ ] Gap analysis complete
- [ ] Requirements documented

#### Week 2  
- [ ] Template forked
- [ ] Customizations complete
- [ ] Variables configured

#### Week 3
- [ ] Test projects validated
- [ ] Migration script tested
- [ ] CI/CD verified

#### Week 4
- [ ] Documentation complete
- [ ] Training delivered
- [ ] Support channel active

#### Week 5
- [ ] Template deployed
- [ ] Pilot migrations successful
- [ ] Feedback collected

#### Post-Migration
- [ ] Monitoring active
- [ ] Issues resolved
- [ ] Metrics tracked
- [ ] Old template deprecated