# Gap Analysis: Current Template vs cookiecutter-uv

## Overview
This document analyzes the differences between our current pyproject-template and the cookiecutter-uv template target.

## Feature Comparison Table

| Feature | Current Template | cookiecutter-uv | Gap | Priority |
|---------|-----------------|-----------------|-----|----------|
| **Build System** | setuptools + setuptools_scm | hatchling (pyproject.toml) | Need to migrate | High |
| **Package Manager** | pip + requirements | uv with lock file | Need to adopt uv | High |
| **Python Versions** | 3.11+ | 3.9-3.13 | Broader support in target | Low |
| **Project Layout** | Flat layout only | src/flat configurable | Add src layout option | Medium |
| **Configuration** | Dynaconf + .env | Simple .env | **Need to preserve Dynaconf** | Critical |
| **Logging** | Loguru with rotation | Standard logging | **Need to preserve Loguru** | Critical |
| **CLI Framework** | Typer with Rich | None/basic | **Need to add Typer** | Critical |
| **Testing** | pytest + coverage | pytest + codecov + tox-uv | Add tox-uv, codecov | Medium |
| **Linting** | ruff + black separate | ruff only (format + lint) | Consolidate to ruff | Low |
| **Type Checking** | mypy strict | mypy (optional) | Keep strict mypy | Medium |
| **Documentation** | mkdocs + pdoc | mkdocs only | Remove pdoc | Low |
| **Pre-commit** | Yes | Yes | Compatible | None |
| **CI/CD** | None | GitHub Actions | **Need to add** | High |
| **Docker** | Dockerfile included | Docker/Podman optional | Compatible | Low |
| **Publishing** | Manual | Auto PyPI via GitHub | **Need to add** | Medium |
| **Dependency Analysis** | None | deptry | Add deptry | Low |
| **Multi-Python Testing** | None | tox-uv | **Need to add** | Medium |

## Critical Gaps to Address

### 1. Custom Features Not in cookiecutter-uv (Must Add)
- **Dynaconf Configuration System**: Our centralized configuration management
- **Loguru Logging**: Advanced logging with rotation and compression
- **Typer CLI Framework**: Command-line interface structure
- **Rich Integration**: Terminal formatting and display
- **Pydantic**: Data validation (core dependency)

### 2. Missing Modern Features (Must Adopt)
- **GitHub Actions CI/CD**: Automated testing and deployment
- **tox-uv**: Multi-version Python testing
- **Auto-publishing to PyPI**: Release automation
- **codecov Integration**: Coverage reporting
- **deptry**: Dependency analysis

### 3. Build System Migration
- **From**: setuptools + setuptools_scm
- **To**: hatchling build backend
- **Impact**: Update pyproject.toml structure, entry points

### 4. Package Management Migration
- **From**: pip install with requirements files
- **To**: uv sync with uv.lock
- **Impact**: All installation commands, CI/CD scripts, documentation

## Customization Strategy

### Phase 1: Fork and Basic Setup
1. Fork cookiecutter-uv repository
2. Add our custom dependencies to template
3. Configure cookiecutter.json with our variables

### Phase 2: Feature Integration
1. Add Dynaconf configuration module
2. Integrate Loguru logging setup
3. Add Typer CLI structure template
4. Include Rich formatting support
5. Add Pydantic to core dependencies

### Phase 3: Template Variables
```json
{
  // Existing cookiecutter-uv variables
  "project_name": "",
  "project_slug": "",
  "python_version": ["3.11", "3.9", "3.10", "3.12", "3.13"],
  "project_layout": ["src", "flat"],
  
  // Our custom additions
  "use_dynaconf": ["y", "n"],
  "use_loguru": ["y", "n"],
  "use_typer_cli": ["y", "n"],
  "use_rich": ["y", "n"],
  "include_claude_rules": ["y", "n"],
  "author": "",
  "email": "",
  "github_username": ""
}
```

### Phase 4: Post-Generation Hooks
Create hooks to:
1. Set up Dynaconf configuration files if selected
2. Create Loguru config module if selected
3. Generate Typer CLI boilerplate if selected
4. Add CLAUDE.md rules if selected
5. Configure proper .gitignore entries

## Migration Benefits

### Gains from cookiecutter-uv
1. Modern uv package management (faster, more reliable)
2. Automated CI/CD with GitHub Actions
3. Multi-Python version testing with tox-uv
4. Automated PyPI publishing
5. Better dependency analysis with deptry
6. Configurable project layout (src/flat)
7. Consolidated ruff for formatting and linting

### Preserved Custom Value
1. Dynaconf configuration management
2. Loguru advanced logging
3. Typer CLI framework
4. Rich terminal UI
5. Strict type checking
6. Comprehensive testing setup

## Risk Assessment

### Low Risk
- Pre-commit hooks (compatible)
- Documentation system (mkdocs already supported)
- Testing framework (pytest compatible)
- Linting consolidation (ruff handles both)

### Medium Risk
- Build system change (requires testing)
- Package manager migration (training needed)
- CI/CD setup (new workflows to maintain)

### High Risk
- Loss of custom features if not properly integrated
- Breaking changes in dependency management
- Developer adoption of uv commands

## Recommendations

1. **Priority 1**: Create customized fork with Dynaconf, Loguru, and Typer
2. **Priority 2**: Add GitHub Actions workflows for CI/CD
3. **Priority 3**: Implement tox-uv for multi-version testing
4. **Priority 4**: Create comprehensive migration tooling
5. **Priority 5**: Develop training materials for uv usage

## Next Steps

1. Fork cookiecutter-uv repository
2. Create feature branch for customizations
3. Add custom modules and dependencies
4. Test with pilot projects
5. Document all changes
6. Create migration scripts