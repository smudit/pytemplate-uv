---
allowed-tools: Task, Bash, Grep, Read, Edit, Write
argument-hint: [target] [--auto-fix] [--preview]
description: Automatically update tests when code changes are detected
model: sonnet
---

# Test Update Command

Automatically detect code changes and update corresponding tests to maintain synchronization between implementation and test assertions.

## Usage

```bash
/test-update                    # Update tests for changed files
/test-update --auto-fix         # Fix failing tests automatically
/test-update path/to/module.py  # Update specific module tests
/test-update --preview          # Dry-run mode (show what would change)
```

## Instructions

You are a test maintenance specialist. Your task is to keep tests synchronized with implementation changes.

### Step 1: Detect Changed Files

**If no target specified:**
1. Run `git diff --name-only` to find uncommitted changes
2. Run `git diff --cached --name-only` to find staged changes
3. Filter for Python files (*.py) excluding test files

**If target specified:**
- Use the provided file path
- Validate it exists and is a Python file

### Step 2: Identify Affected Tests

For each changed file:
1. Determine the corresponding test file:
   - `ms_ai_assistant/module.py` → `tests/test_module.py`
   - `ms_ai_assistant/package/module.py` → `tests/test_module.py`
2. Check if test file exists
3. If no test exists, note it for later (use `/test-sync --generate-missing`)

### Step 3: Analyze Changes

For each changed file:
1. Read the current implementation
2. Read the corresponding test file
3. Identify what changed:
   - New functions/methods added
   - Function signatures changed (parameters, return types)
   - Function behavior modified
   - Functions removed/renamed

### Step 4: Update Tests

**For each affected test:**

1. **Function signature changes:**
   - Update test calls to match new parameters
   - Update assertions for new return types
   - Add missing parameter tests

2. **New functionality:**
   - Note: "New function `foo()` detected - use /test-sync to generate tests"
   - Don't auto-generate full tests here (that's /test-sync's job)

3. **Removed functionality:**
   - Comment out or remove obsolete tests
   - Add note about removal

4. **Behavior changes:**
   - Update assertion values if they're clearly outdated
   - Flag complex changes that need manual review

### Step 5: Handle --auto-fix Mode

If `--auto-fix` flag is provided:

1. Run `uv run pytest <test_file>` for each affected test
2. For each failing test:
   - Analyze the failure message
   - Determine if it's an auto-fixable issue:
     - ✅ Assertion value mismatch (update expected value)
     - ✅ Missing mock parameters (add them)
     - ✅ Changed function signature (update test call)
     - ❌ Logic errors (flag for manual fix)
     - ❌ Complex failures (flag for manual fix)
3. Apply fixes using Edit tool
4. Re-run tests to verify fixes

### Step 6: Preview Mode (--preview)

If `--preview` flag is provided:
- Show what would be changed WITHOUT making actual changes
- List files that would be updated
- Show proposed changes as diffs
- Provide summary of actions that would be taken

### Step 7: Present Results

```
## Test Update Results

### Files Analyzed
- [changed_file.py] → tests/test_changed_file.py

### Updates Made
✅ Updated test_function_name() - adjusted assertion values
✅ Updated test_another_function() - added new parameter
⚠️  Removed test_old_function() - function no longer exists

### Manual Review Needed
❌ test_complex_function() - behavior change requires manual review
   File: tests/test_module.py:45

### Summary
- Tests updated: 5
- Tests removed: 1
- Manual fixes needed: 1

### Next Steps
- Review manual fix items above
- Run `make test` to verify all tests pass
- Use `/test-sync --generate-missing` for new functions
```

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Simple assertion value changed | ✅ Auto-update (with --auto-fix) |
| Function signature changed | ✅ Auto-update test calls |
| Function removed | ✅ Comment out tests |
| New function added | ⚠️  Note for /test-sync |
| Complex logic change | ❌ Flag for manual review |
| Mock configuration changed | ✅ Auto-update (with --auto-fix) |

## Safety Guardrails

1. **Always read before editing**: Never modify tests without reading them first
2. **Preserve test intent**: Don't change what the test is testing, only how
3. **Flag uncertainty**: When in doubt, flag for manual review
4. **Run verification**: After updates, run affected tests to verify
5. **Backup critical tests**: For complex tests, show diff before applying

## Integration Points

- **Before /git-commit**: Run `/test-update` to sync tests with code changes
- **After refactoring**: Use `/test-update --auto-fix` to update broken tests
- **With /test-sync**: Use /test-update for existing tests, /test-sync for new tests
- **With /review**: Include test update status in code reviews

## Examples

### Example 1: Simple Function Signature Change

```python
# Before (implementation)
def calculate_total(items: list[float]) -> float:
    return sum(items)

# After (implementation)
def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
    return sum(items) * (1 + tax_rate)
```

**Test Update Action:**
```python
# Update test calls to include tax_rate parameter
# Update assertions to account for tax calculation
```

### Example 2: Auto-fix Failing Test

```
# Test failure:
AssertionError: assert 'Hello' == 'Hello, World!'

# Auto-fix action:
Update assertion from assert result == 'Hello' to assert result == 'Hello, World!'
```

## Important Notes

- Use `uv run pytest` for running tests
- Always work in the project's virtual environment
- Don't modify test logic, only test data and calls
- Preserve test coverage - don't delete tests without good reason
- Use Edit tool to make surgical changes, not Write tool
- Focus on keeping tests passing while reflecting code changes
