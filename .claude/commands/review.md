---
allowed-tools: Task, Bash, Grep, Read
argument-hint: [target] [--quick|--deep|--ai] [--uncommitted] [--with-tests|--test-only]
description: Unified code review with smart mode selection, comprehensive analysis, and test impact assessment
model: sonnet
---

# Unified Code Review

Intelligent code review with automatic or manual mode selection based on scope and requirements.

**Usage:**
```bash
/review [target] [--quick|--deep|--ai] [--uncommitted] [--with-tests|--test-only]
```

## Review Modes

### Quick Mode (`--quick`)
- Fast, focused quality check
- Automated linting (ruff, mypy)
- Basic code scan for common issues
- Best for: Active development, rapid feedback
- Time: ~30 seconds

### Deep Mode (`--deep`)
- Comprehensive agent-based review
- Uses `changes-reviewer` agent
- Focus on bugs, logic errors, security
- Best for: Pre-commit, PR preparation
- Time: 1-3 minutes

### AI Mode (`--ai`)
- Uses codex skill with GPT models
- Detailed analysis and suggestions
- Saves review to docs/code_reviews/
- Best for: Major changes, architecture review
- Time: 2-5 minutes

### Auto Mode (default)
- Automatically selects best mode based on:
  - Number of lines changed
  - Number of files affected
  - Complexity of changes
- Decision matrix:
  - **< 50 lines, single file** → Quick
  - **50-200 lines** → Deep
  - **> 200 lines, multiple files** → AI

## Arguments

- `[target]`: File path, directory, or commit hash (optional)
- `--quick`: Force quick review mode
- `--deep`: Force deep review mode (agent-based)
- `--ai`: Force AI review mode (codex)
- `--uncommitted`: Review only uncommitted changes (git diff HEAD)
- `--with-tests`: Include test impact analysis (coverage delta, missing tests)
- `--test-only`: Only analyze test impact (skip code review)

## Examples

```bash
# Auto-select mode for uncommitted changes
/review --uncommitted

# Quick review of specific file
/review src/auth.py --quick

# Deep review of directory
/review src/services/ --deep

# AI review of recent commit
/review HEAD~1 --ai

# Review with test impact analysis
/review --uncommitted --with-tests

# Only analyze test impact (skip code review)
/review --uncommitted --test-only

# Deep review with test analysis
/review src/models/user.py --deep --with-tests
```

## Workflow

### Step 1: Determine Scope

Parse arguments to identify:
- Target: file, directory, commit, or uncommitted changes
- Mode: quick, deep, ai, or auto
- Run `git diff --stat` if reviewing uncommitted changes

### Step 2: Mode Selection (if auto)

If no mode specified, analyze scope:

```bash
git diff --stat | tail -1
# Example: "3 files changed, 127 insertions(+), 45 deletions(-)"
```

**Decision Logic:**
- Extract line count and file count
- If `lines < 50 AND files = 1` → Quick
- If `50 <= lines <= 200` → Deep
- If `lines > 200 OR files > 3` → AI
- Inform user of selected mode and reasoning

### Step 3: Execute Review

#### Quick Mode Execution

1. **Run automated checks in parallel:**
   ```bash
   make lint
   make format-check
   uv run mypy [target]
   ```

2. **Scan for common issues:**
   - Missing type hints on public functions
   - Missing/incomplete docstrings
   - Bare except clauses
   - Hardcoded values (API keys, magic numbers)
   - Long functions (>50 lines)
   - Unused imports
   - `typing.Any` usage
   - Missing `@logger.catch` on important functions

3. **Present results:**
   ```
   ## Quick Review Results

   ### Automated Checks
   - ✅ Ruff: PASS
   - ⚠️ Mypy: 3 warnings
   - ✅ Format: PASS

   ### Code Issues (file:line)
   - src/auth.py:45 - Missing type hint on login()
   - src/auth.py:67 - Bare except clause
   - src/models.py:23 - Hardcoded API URL

   ### Quick Wins
   1. Add type hints to public functions
   2. Replace bare except with specific exception
   3. Move API URL to config

   ### Recommendation: ✅ PASS (with minor fixes recommended)
   ```

#### Deep Mode Execution

1. **Launch changes-reviewer agent:**
   ```
   Use Task tool with subagent_type='changes-reviewer'
   Prompt: "Review code changes focusing on bugs and logic errors"
   ```

2. **Parse agent output** for issues by severity

3. **Present structured results:**
   ```
   ## Deep Review Results

   🔴 CRITICAL Issues: 0
   🟠 HIGH Issues: 2
   🟡 MEDIUM Issues: 5
   🟢 LOW Issues: 3

   ### HIGH Priority
   - src/auth.py:89 - Null reference: user.email accessed without check
   - src/db.py:134 - Race condition in transaction handling

   [Full details with fixes...]

   ### Recommendation: ⚠️ Fix HIGH issues before merging
   ```

#### AI Mode Execution

1. **Invoke codex skill** for comprehensive review
2. **Save output** to `docs/code_reviews/review_DDMMYY-HHMM.md`
3. **Parse and present findings** with file:line references
4. **Create todo list** if fixes are needed (with user approval)

### Step 4: Test Impact Analysis (if --with-tests or --test-only)

If `--with-tests` or `--test-only` is provided, perform comprehensive test analysis:

1. **Identify Changed/New Code:**
   ```bash
   git diff --name-only  # Get changed files
   ```
   - Filter for Python source files (exclude tests/)
   - Identify new functions/classes added
   - Identify modified functions

2. **Analyze Test Coverage Impact:**
   ```bash
   # Get current coverage
   uv run pytest --cov=ms_ai_assistant --cov-report=term-missing -q
   ```

   - Calculate coverage delta (before/after changes)
   - Identify which changed files have tests
   - Identify which changed files lack tests

3. **Check Test Synchronization:**
   For each changed file:
   - Does a corresponding test file exist?
   - Do tests cover the changed functions?
   - Are test assertions up to date?

4. **Present Test Impact Report:**
   ```
   ## Test Impact Analysis

   ### Coverage Delta
   - Before: 24.0%
   - Current: 24.3%
   - Change: +0.3% ✅

   ### Changed Files
   1. ms_ai_assistant/module.py
      - Functions changed: 3
      - Test file: ✅ tests/test_module.py exists
      - Coverage: 75% (needs improvement)
      - Action: Run `/test-update` to sync tests

   2. ms_ai_assistant/new_feature.py (NEW)
      - Functions added: 5
      - Test file: ❌ Missing
      - Coverage: 0%
      - Action: Run `/test-sync --generate-missing`

   ### Tests Needing Update
   ⚠️  tests/test_module.py::test_function_x
      - Function signature changed, test needs parameter update
      - Suggestion: Use `/test-update --auto-fix`

   ### Missing Tests
   ❌ ms_ai_assistant/new_feature.py::calculate_result()
   ❌ ms_ai_assistant/new_feature.py::validate_input()
   ❌ ms_ai_assistant/module.py::new_helper_function()
      - Suggestion: Use `/test-sync --generate-missing`

   ### Test Health Summary
   - Total changed files: 2
   - Files with tests: 1 (50%)
   - Files without tests: 1 (50%)
   - Recommended action: Generate missing tests before commit

   ### Next Steps
   1. Run `/test-sync --generate-missing` for new_feature.py
   2. Run `/test-update` for module.py
   3. Verify tests pass with `make test`
   4. Commit with improved test coverage
   ```

5. **If --test-only mode:**
   - Skip all code review steps
   - Only perform test impact analysis
   - Provide actionable test-related recommendations

### Step 5: Next Steps

Based on review results:
- **Quick PASS**: Ready to proceed
- **Deep with issues**: Suggest fixes or escalate to AI mode
- **AI findings**: Offer to create fix todos or save for later
- **Test issues found**: Suggest running `/test-update` or `/test-sync`

## Integration with Other Commands

- **Before commit**: `/review --uncommitted --quick --with-tests`
- **Before PR**: `/review --uncommitted --deep --with-tests`
- **Major refactor**: `/review src/ --ai --with-tests`
- **Test-only check**: `/review --uncommitted --test-only`
- **After review**: Use `/test-update` or `/test-sync` as suggested, then `/git-commit`

## Test-Aware Workflow

The enhanced review command integrates with the testing workflow:

```
1. Make code changes
2. /review --uncommitted --with-tests
   ↓
3. If test issues found:
   - Missing tests → /test-sync --generate-missing
   - Outdated tests → /test-update --auto-fix
   ↓
4. make test (verify all pass)
   ↓
5. /git-commit
```

## Notes

- Quick mode uses built-in tools (no agent/skill overhead)
- Deep mode focuses on bug detection and logic errors
- AI mode provides most comprehensive analysis but slower
- Auto mode optimizes for speed vs. thoroughness trade-off
- All modes respect `.claudeignore` patterns

## See Also

- `.claude/commands/test-update.md` - Update tests when code changes
- `.claude/commands/test-sync.md` - Synchronize test coverage
- `.claude/commands/git-commit.md` - Create commits with test validation
- `.claude/commands/codex-review.md` - AI-powered review (alternative to --ai mode)
- `.claude/agents/changes-reviewer.md` - Deep review agent details
