---
model: sonnet
---

# Iterative AI-Powered Code Review & Fix Workflow

**Purpose**: Automatically review code for bugs and logical errors, apply fixes, run tests, and iterate until no critical issues remain or max iterations reached.

**Signature**: `/iterative-review [target] [--max-iterations=N] [--uncommitted]`

**Examples**:
- `/iterative-review` - Review all recent uncommitted changes
- `/iterative-review src/module.py` - Review specific file
- `/iterative-review src/` - Review entire directory
- `/iterative-review --uncommitted --max-iterations=5` - Review uncommitted changes with 5 max iterations

---

## Workflow

You are executing an iterative code review and fix workflow. Follow these steps precisely:

### Step 1: Determine Scope

Determine what code to review based on the provided arguments:

1. **If `--uncommitted` flag provided**: Review all uncommitted changes via `git diff HEAD`
2. **If file path provided**: Review the specific file (e.g., `src/module.py`)
3. **If directory provided**: Review all Python files in the directory recursively
4. **If no arguments**: Default to `git diff HEAD` (uncommitted changes)

Use `git status` and `git diff HEAD` to understand what files have changed if reviewing uncommitted changes.

### Step 2: Initialize Tracking

1. **Create iteration tracking variables**:
   - Current iteration = 1
   - Max iterations = value from `--max-iterations` flag (default: 3)
   - Issues found = 0
   - Fixes applied = 0

2. **Create todo list** using TodoWrite with initial setup task

3. **Create report file**: `docs/code_reviews/iterative_review_<DDMMYY>-<HHMM>.md`
   - Use current date/time for filename
   - Initialize with header, scope, and iteration log section

### Step 3: Iteration Loop

Repeat the following steps until no critical issues remain OR max iterations reached:

#### 3.1 AI Review Phase

1. **Invoke changes-reviewer agent** to analyze the code:
   ```
   Task tool with subagent_type='changes-reviewer'
   Prompt: "Review the following code for bugs and logical errors.
   Focus ONLY on:
   - Bugs and logical errors
   - Potential runtime failures
   - Incorrect business logic
   - Error handling issues

   Do NOT report:
   - Style issues (handled by linters)
   - Minor optimizations
   - Documentation improvements

   For each issue found, provide:
   - Severity: CRITICAL, HIGH, MEDIUM, LOW
   - File and line number
   - Description of the bug/error
   - Suggested fix

   Return findings in structured format."
   ```

2. **Parse agent output** into structured issue list:
   - Separate by severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Extract file:line references
   - Extract suggested fixes

3. **Filter for critical/high priority issues only**:
   - Count CRITICAL and HIGH severity issues
   - If count = 0, proceed to Step 3.5 (Testing Phase)
   - If count > 0, proceed to Step 3.2

#### 3.2 User Approval Gate

**REQUIRED**: Before applying ANY fixes, present findings to user:

1. **Display summary**:
   ```
   ## Iteration [N] Review Results

   Found [X] critical/high priority issues:

   ### CRITICAL Issues ([count])
   - [file:line] Description
   ...

   ### HIGH Issues ([count])
   - [file:line] Description
   ...

   Suggested fixes are ready to apply.
   ```

2. **Ask user**: "Type 'approve' to proceed with applying fixes, or 'skip' to move to next iteration, or 'stop' to exit."

3. **Wait for user response**:
   - If "approve" → proceed to Step 3.3
   - If "skip" → proceed to Step 3.5
   - If "stop" → exit loop and go to Step 4

#### 3.3 Apply Fixes Phase

1. **Create TodoWrite list** with one todo per issue to fix

2. **For each issue** (in order: CRITICAL first, then HIGH):
   - Mark corresponding todo as "in_progress"
   - Read the file that needs fixing
   - Apply the suggested fix using Edit tool
   - Mark todo as "completed"
   - Increment fixes_applied counter
   - Update iteration report with fix details

3. **Log all fixes** to iteration report with:
   - File and line modified
   - Issue description
   - Fix applied

#### 3.4 Validation Phase - Linting & Formatting

1. **Run linting**:
   ```bash
   make lint
   ```
   - If fails: Log warnings but continue (will be caught in next iteration)

2. **Run formatting**:
   ```bash
   make format
   ```
   - Auto-formats all files

#### 3.5 Testing Phase

1. **Run full test suite**:
   ```bash
   make test
   ```

2. **Capture test results**:
   - Exit code (0 = pass, non-zero = fail)
   - Number of tests passed/failed
   - Failing test names

3. **If tests FAIL**:

   a. **Invoke test_engineer agent**:
      ```
      Task tool with subagent_type='test_engineer'
      Prompt: "Tests are failing after applying code fixes. Please analyze the test failures and determine if:
      1. The tests need to be updated to reflect new logic
      2. The code fixes introduced new bugs
      3. Tests were already failing (pre-existing issues)

      Test output:
      [paste test output]

      Files modified in this iteration:
      [list files changed]

      Provide specific recommendations for fixing the tests or reverting problematic changes."
      ```

   b. **Parse test_engineer recommendations**

   c. **Ask user**: "Tests failed. test_engineer recommends: [summary]. Type 'fix-tests' to apply test fixes, 'revert' to undo last fixes, or 'continue' to proceed to next iteration."

   d. **Based on user choice**:
      - "fix-tests": Apply test_engineer recommendations, re-run tests
      - "revert": Use git to revert changes from this iteration
      - "continue": Proceed to iteration check

4. **If tests PASS**:
   - Log success to iteration report
   - Proceed to iteration check

#### 3.6 Iteration Check

1. **Update iteration report** with:
   - Issues found this iteration
   - Fixes applied
   - Test results
   - Validation results

2. **Increment iteration counter**: current_iteration += 1

3. **Check continuation conditions**:
   - If current_iteration > max_iterations:
     - Log: "Maximum iterations reached"
     - Exit loop → go to Step 4
   - If no CRITICAL/HIGH issues found in this iteration AND tests pass:
     - Log: "No critical issues remaining, tests passing"
     - Exit loop → go to Step 4
   - Otherwise:
     - Log: "Starting iteration [N+1]"
     - Loop back to Step 3.1

### Step 4: Final Report

1. **Generate final summary**:
   ```markdown
   # Iterative Review Summary

   **Scope**: [files/directory reviewed]
   **Total Iterations**: [N]
   **Total Issues Found**: [X]
   **Total Fixes Applied**: [Y]
   **Final Test Status**: [PASS/FAIL]

   ## Iteration Summary
   [Summary of each iteration]

   ## Final Status
   - ✅ All critical/high priority issues resolved
   - ✅ Tests passing
   - ✅ Code formatted and linted

   OR

   - ⚠️ Maximum iterations reached
   - ⚠️ [N] issues remaining
   - See detailed report: docs/code_reviews/iterative_review_[timestamp].md
   ```

2. **Save final report** to `docs/code_reviews/iterative_review_<DDMMYY>-<HHMM>.md`

3. **Display summary** to user with:
   - Path to detailed report
   - Overall success/failure status
   - Recommendations for next steps if issues remain

---

## Important Notes

1. **NEVER apply fixes without user approval** - always wait for "approve" response
2. **Track all changes** in the iteration report for auditability
3. **Focus on bugs and logic errors** - ignore style/documentation issues
4. **Run tests after every fix** - ensure changes don't break functionality
5. **Use TodoWrite extensively** - keep user informed of progress
6. **Respect max iterations** - don't run indefinitely
7. **Clear communication** - use file:line references, show before/after diffs when helpful

## Error Handling

- If changes-reviewer agent fails: Log error, skip to testing phase
- If test_engineer agent fails: Ask user for manual intervention
- If git commands fail: Inform user and request manual scope specification
- If file operations fail: Log error and continue with remaining files
