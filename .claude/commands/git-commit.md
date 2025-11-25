---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*), Bash(make test:*), Bash(uv run pytest:*)
argument-hint: [message] | --no-verify | --amend | --skip-tests
description: Create well-formatted commits with conventional commit format, emoji, and comprehensive quality gates (Tests + Ruff + Mypy)
model: haiku
---

# Smart Git Commit (Tests + Ruff + Mypy)

Create well-formatted commit: $ARGUMENTS

## Current Repository State

- Git status: !git status --porcelain
- Current branch: !git branch --show-current
- Staged changes: !git diff --cached --stat
- Unstaged changes: !git diff --stat
- Recent commits: !git log --oneline -5

## What This Command Does

1. Unless specified with `--no-verify` or `--skip-tests`, automatically runs comprehensive quality gates:
   - **Tests**: `make test` to ensure all tests pass (skip with `--skip-tests`)
   - **Test Coverage Check**: Verifies changed files have corresponding tests
   - **Ruff (lint)**: `ruff check .` to ensure code quality and catch errors
   - **Ruff (format check)**: `ruff format --check .` to verify formatting
   - **Mypy (type check)**: `mypy .` to enforce static typing
2. Performs test impact analysis for changed files
3. Checks which files are staged with `git status`
3. If 0 files are staged, automatically adds all modified and new files with `git add`
4. Performs a comprehensive `git diff` analysis to understand changes:
   - **Content Analysis**: Examines actual code changes to determine commit type
   - **Scope Detection**: Automatically extracts scope from file paths
   - **Change Categorization**: Smart detection based on keywords and patterns
5. Analyzes the diff to determine if multiple distinct logical changes are present
6. If multiple distinct changes are detected, suggests breaking the commit into multiple smaller commits
7. For each commit, generates an intelligent commit message:
   - **Type**: Determined by content analysis (not just file names)
   - **Scope**: Auto-detected from file paths (e.g., `src/auth/login.py` → `(auth)`)
   - **Subject**: Concise, descriptive summary
   - **Body**: Detailed bullet points explaining what changed and why
   - **Footer**: Issue references and breaking change notes

> **Notes**
>
> - Configure Ruff and Mypy in `pyproject.toml` (preferred) or in `.ruff.toml` / `mypy.ini` as appropriate.
> - To auto-format before checking, run `ruff format .` locally (not part of `--verify` checks to keep CI reproducible).

## Intelligent Message Generation

### Automatic Scope Detection

The command automatically extracts scope from file paths using these patterns:

| File Path | Detected Scope |
|-----------|---------------|
| `src/components/UserCard.tsx` | `(components)` |
| `api/auth/login.py` | `(auth)` |
| `tests/unit/test_utils.py` | `(tests)` |
| `docs/api/README.md` | `(docs)` |
| `config/settings.yaml` | `(config)` |
| `.github/workflows/ci.yml` | `(ci)` |
| `database/migrations/001.sql` | `(database)` |
| `frontend/pages/index.tsx` | `(frontend)` |
| `backend/services/user.py` | `(backend)` |

### Smart Change Categorization

The command analyzes **content**, not just file names, to determine commit type:

**Bug Fix Detection** (`fix:`):
- Keywords: `fix`, `bug`, `resolve`, `issue`, `error`, `crash`, `patch`
- Patterns: Exception handling, null checks, boundary conditions
- Example: Adding missing null check → `🐛 fix: prevent null reference error`

**Feature Detection** (`feat:`):
- New files or functions
- Keywords: `add`, `implement`, `create`, `introduce`, `new`
- Patterns: New classes, endpoints, components
- Example: New auth endpoint → `✨ feat: add JWT authentication endpoint`

**Performance Detection** (`perf:`):
- Keywords: `optimize`, `speed`, `performance`, `cache`, `lazy`
- Patterns: Algorithm improvements, caching, query optimization
- Example: Adding cache → `⚡️ perf: implement Redis caching for user queries`

**Refactoring Detection** (`refactor:`):
- Keywords: `refactor`, `restructure`, `reorganize`, `extract`, `simplify`
- Patterns: Moving code, renaming, extracting methods
- Example: Extract method → `♻️ refactor: extract validation logic into separate module`

### Enhanced Message Body Generation

The command generates detailed commit bodies with:

1. **What changed** - Bullet points of specific changes
2. **Why it changed** - Context and reasoning
3. **Impact** - What this affects
4. **References** - Related issues/PRs

Example generated message:
```
🐛 fix(auth): resolve token expiration handling issue

- Fix incorrect timestamp comparison causing premature logout
- Add proper timezone handling for token expiry checks
- Update refresh token logic to prevent race conditions
- Add comprehensive error logging for debugging

This resolves the issue where users were being logged out
randomly due to timezone mismatches between client and server.

Closes #156
```

## Best Practices for Commits

- **Verify before committing**: Ensure code is linted (Ruff) and types pass (Mypy)
- **Atomic commits**: Each commit should contain related changes that serve a single purpose
- **Split large changes**: If changes touch multiple concerns, split them into separate commits
- **Conventional commit format**: Use the format `<type>: <description>` where type is one of:
  - feat: A new feature
  - fix: A bug fix
  - docs: Documentation changes
  - style: Code style changes (formatting, etc)
  - refactor: Code changes that neither fix bugs nor add features
  - perf: Performance improvements
  - test: Adding or fixing tests
  - chore: Changes to the build process, tools, etc.
- **Present tense, imperative mood**: Write commit messages as commands (e.g., "add feature" not "added feature")
- **Concise first line**: Keep the first line under 72 characters
- **Emoji**: Each commit type is paired with an appropriate emoji

**Core Emojis:**
  - ✨ feat: New feature
  - 🐛 fix: Bug fix
  - 📝 docs: Documentation
  - 💄 style: Formatting/style
  - ♻️ refactor: Code refactoring
  - ⚡️ perf: Performance improvements
  - ✅ test: Tests
  - 🔧 chore: Tooling, configuration

**See `.claude/references/commit-emojis.md` for complete emoji reference and usage examples.**

## Guidelines for Splitting Commits

When analyzing the diff, consider splitting commits based on these criteria:

1. **Different concerns**: Changes to unrelated parts of the codebase
2. **Different types of changes**: Mixing features, fixes, refactoring, etc.
3. **File patterns**: Changes to different types of files (e.g., source code vs documentation)
4. **Logical grouping**: Changes that would be easier to understand or review separately
5. **Size**: Very large changes that would be clearer if broken down

## Examples

### Enhanced Examples with Intelligent Generation

#### Example 1: Bug Fix with Auto-detected Scope
```bash
# Files changed: backend/services/auth.py, backend/utils/tokens.py

# Command analyzes content and generates:
🐛 fix(backend): resolve JWT token validation issue

- Fix incorrect signature verification in token validator
- Add proper error handling for expired tokens
- Update token refresh logic to handle edge cases
- Add logging for debugging token failures

This fixes the critical issue where valid tokens were being
rejected after server restart due to incorrect key loading.

Closes #234
```

#### Example 2: New Feature with Multiple Components
```bash
# Files changed: src/components/Dashboard.tsx, api/metrics.py, tests/test_metrics.py

# Command generates:
✨ feat(metrics): implement real-time analytics dashboard

- Add new Dashboard component with live data updates
- Create metrics API endpoint with WebSocket support
- Implement data aggregation service for performance metrics
- Add comprehensive unit tests for metrics calculation
- Include error boundaries for graceful fallback

Provides users with real-time visibility into system performance
and usage patterns, addressing the monitoring requirements.

Relates to #156, #178
```

#### Example 3: Performance Improvement
```bash
# Files changed: database/queries/user_queries.py, cache/redis_config.py

# Command detects optimization patterns and generates:
⚡️ perf(database): optimize user query performance

- Implement Redis caching layer for frequent user lookups
- Add database indices on email and username columns
- Batch user queries to eliminate N+1 problem
- Implement query result pagination

Reduces average query time from 850ms to 45ms for user searches,
significantly improving API response times.

Performance impact: 95% reduction in database load
```

### Good Commit Messages (Simple):

- ✨ feat: add user authentication system
- 🐛 fix: resolve memory leak in rendering process
- 📝 docs: update API documentation with new endpoints
- ♻️ refactor: simplify error handling logic in parser
- 🚨 fix: resolve Ruff/Mypy warnings in src/
- 🧑‍💻 chore: improve developer tooling setup process
- 👔 feat: implement business logic for transaction validation
- 🩹 fix: address minor styling inconsistency in header
- 🚑️ fix: patch critical security vulnerability in auth flow
- 🎨 style: reorganize component structure for better readability
- 🔥 fix: remove deprecated legacy code
- 🦺 feat: add input validation for user registration form
- 💚 fix: resolve failing CI pipeline tests
- 📈 feat: implement analytics tracking for user engagement
- 🔒️ fix: strengthen authentication password requirements
- ♿️ feat: improve form accessibility for screen readers

### Example of Splitting Commits:

- First commit: ✨ feat: add new solc version type definitions
- Second commit: 📝 docs: update documentation for new solc versions
- Third commit: 🔧 chore: update pyproject.toml for Ruff/Mypy
- Fourth commit: 🏷️ feat: add type definitions for new API endpoints
- Fifth commit: 🧵 feat: improve concurrency handling in worker threads
- Sixth commit: 🚨 fix: resolve Ruff linting issues in new code
- Seventh commit: ✅ test: add unit tests for new solc version features
- Eighth commit: 🔒️ fix: update dependencies with security vulnerabilities

## Workflow Integration

### Recommended Development Workflow

1. **Make your changes** - Write code, fix bugs, add features
2. **Quick review** (optional) - `/review-unified --quick` for fast feedback
3. **Stage changes** - Let the command auto-stage or manually use `git add`
4. **Smart commit** - `/git-commit` generates intelligent message
5. **Push and PR** - `git push` and create pull request

### Integration with Review Commands

The git-commit command works seamlessly with:

- **`/review-unified --quick`** - Run before committing for quick quality check
- **`/review-unified`** - Automatically selects appropriate review level
- **`changes-reviewer` agent** - For comprehensive review before major commits

Example workflow:
```bash
# After making changes
/review-unified --quick      # Quick quality check
/git-commit                  # Generate smart commit with all enhancements
git push                     # Push to remote
gh pr create                 # Create PR
```

## Command Options

- `--no-verify`: Skip running the pre-commit checks (Ruff and Mypy)
- `--amend`: Amend the previous commit instead of creating new one
- `[message]`: Provide custom message (still adds emoji and formatting)

## Configuration

The command behavior can be customized via settings:

```yaml
# .claude/settings.yaml (if supported)
git_commit:
  auto_scope: true           # Enable automatic scope detection
  detailed_body: true        # Generate detailed commit bodies
  smart_categorization: true # Use content analysis for type
  quality_checks: true       # Run Ruff/Mypy before commit
  emoji: true               # Include emoji in messages
  split_commits: true       # Suggest splitting large changes
```

## Important Notes

- By default, pre-commit checks (Ruff lint + format check, Mypy type check) will run to ensure code quality
- If these checks fail, you'll be asked if you want to proceed with the commit anyway or fix the issues first
- If specific files are already staged, the command will only commit those files
- If no files are staged, it will automatically stage all modified and new files
- The commit message will be constructed based on the changes detected
- Before committing, the command will review the diff to identify if multiple commits would be more appropriate
- If suggesting multiple commits, it will help you stage and commit the changes separately
- Always reviews the commit diff to ensure the message matches the changes
