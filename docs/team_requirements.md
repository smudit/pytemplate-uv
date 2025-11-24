# Team-Specific Requirements Document

## Core Requirements Not in cookiecutter-uv

### 1. Configuration Management
**Requirement**: Centralized, environment-aware configuration  
**Current Solution**: Dynaconf with YAML/env file support  
**Why Critical**: 
- Multiple deployment environments (dev/staging/prod)
- Secrets management separation
- Dynamic configuration reloading
- Team standard across all projects

### 2. Advanced Logging
**Requirement**: Production-grade logging with rotation and archival  
**Current Solution**: Loguru with automatic rotation and compression  
**Why Critical**:
- Debug production issues with historical logs
- Automatic log management (rotation/compression)
- Structured logging with colors for development
- Performance monitoring via log analysis

### 3. CLI Framework
**Requirement**: User-friendly command-line interfaces  
**Current Solution**: Typer with Rich integration  
**Why Critical**:
- Many internal tools are CLI-based
- Rich help text and validation
- Consistent CLI patterns across projects
- Better developer experience

### 4. Data Validation
**Requirement**: Runtime data validation and serialization  
**Current Solution**: Pydantic v2  
**Why Critical**:
- API request/response validation
- Configuration validation
- Data transformation pipelines
- Type safety at runtime

### 5. CLAUDE.md Integration
**Requirement**: AI-assisted development guidelines  
**Current Solution**: CLAUDE.md file with coding rules  
**Why Critical**:
- Standardized AI assistant interactions
- Consistent code generation
- Team coding standards enforcement
- Improved AI pair programming

## Development Workflow Requirements

### 1. Makefile Commands
**Required Commands**:
```bash
make lint      # Run all linting checks
make format    # Auto-format code
make test      # Run test suite with coverage
make docs      # Generate documentation
make clean     # Clean build artifacts
make build     # Build distribution packages
```

### 2. Pre-commit Hooks
**Required Hooks**:
- Code formatting (ruff)
- Import sorting (ruff/isort)
- Type checking (mypy)
- Security scanning
- Large file prevention
- Trailing whitespace

### 3. Testing Standards
**Requirements**:
- Minimum 80% code coverage
- Test report in terminal
- Parallel test execution
- Fixture sharing
- Parameterized tests support

### 4. Documentation
**Requirements**:
- Auto-generated API docs from docstrings
- Google-style docstring format
- README with quick start
- Configuration examples
- Deployment guides

## Infrastructure Requirements

### 1. Docker Support
**Requirements**:
- Multi-stage builds
- Non-root user execution
- Health checks
- Minimal image size
- Security scanning

### 2. CI/CD Pipeline
**Requirements**:
- Automated testing on PR
- Security vulnerability scanning
- Code coverage reporting
- Automated version bumping
- Release notes generation
- PyPI publishing on tag

### 3. Multi-Environment Support
**Requirements**:
- Development environment setup
- Testing environment isolation
- Production deployment configs
- Environment-specific secrets

## Security Requirements

### 1. Secrets Management
**Requirements**:
- Never commit secrets
- .secrets.yaml in .gitignore
- Environment variable support
- Vault integration capability

### 2. Dependency Security
**Requirements**:
- Regular vulnerability scanning
- Dependency update automation
- License compliance checking
- SBOM generation

## Performance Requirements

### 1. Package Management
**Requirements**:
- Fast dependency installation
- Reproducible builds
- Dependency caching
- Minimal docker layers

### 2. Development Speed
**Requirements**:
- Hot reload support
- Fast test execution
- Quick linting/formatting
- Efficient builds

## Compliance Requirements

### 1. Code Quality
**Requirements**:
- Type hints mandatory
- Docstrings for public APIs
- Maximum line length: 88
- Import organization
- No commented code

### 2. Version Control
**Requirements**:
- Semantic versioning
- Changelog maintenance
- Git tag on release
- Branch protection rules

## Tool Preferences

### Must Have
1. uv for package management (adopting from cookiecutter-uv)
2. Dynaconf for configuration
3. Loguru for logging
4. Typer for CLI
5. Pydantic for validation
6. pytest for testing
7. ruff for linting/formatting
8. mypy for type checking

### Nice to Have
1. tox-uv for multi-version testing
2. codecov for coverage reporting
3. deptry for dependency analysis
4. MkDocs for documentation
5. GitHub Actions for CI/CD

## Migration Non-Negotiables

1. **No Loss of Functionality**: All current features must work
2. **Backward Compatibility**: Existing projects can migrate smoothly
3. **Documentation**: Complete migration guide required
4. **Training**: Team training on new tools (especially uv)
5. **Support Period**: 6-month transition with dual support

## Success Criteria

1. All new projects use the new template
2. 80% of active projects migrated within 3 months
3. No increase in build/test times
4. Developer satisfaction score > 4/5
5. Zero production incidents due to migration

## Customization Priority

### Phase 1 (Week 2) - Critical
- Dynaconf integration
- Loguru setup
- Typer CLI structure
- Core dependencies

### Phase 2 (Week 2-3) - Important
- CLAUDE.md integration
- Makefile commands
- Pre-commit hooks
- Testing setup

### Phase 3 (Week 3) - Enhancement
- GitHub Actions workflows
- Docker optimization
- Documentation generation
- Publishing automation