# Code Review Command

Perform a **user-approved** code review using the codex skill, with documented output and systematic fix application.

## Parameters

Extract from user request or use defaults (DO NOT prompt for missing parameters):

- **target**: File path, directory, or "full codebase" (default: current directory)
- **uncommitted**: Set to `true` for `--uncommitted` flag (reviews only git diff HEAD)
- **focus**: Specific review areas (e.g., "type safety, error handling") - optional
- **model**, **reasoning**: Passed to codex skill (skill provides defaults)

## Workflow

### 1. Pre-Processing: Determine Review Scope

- If `uncommitted` is `true`:
  - Run `git diff HEAD` to capture uncommitted changes
  - Save diff output to variable for use in prompt
  - Set target to current directory
- Otherwise: Use specified target (file/directory/codebase)
- Note the scope for documentation

### 2. Execute Review: Invoke Codex Skill

Use the Skill tool to invoke "codex" (NOT direct Bash):

- Context: "code review" (tells skill to use defaults without prompting)
- Build prompt based on scope:
  - **For uncommitted**: Include diff output in prompt with instruction to review only those changes
  - **For target**: Standard review prompt for specified files/directories
- Add focus areas to prompt if specified
- Pass parameters: model, reasoning (skill provides defaults)
- Skill handles codex execution in read-only mode
- Capture full output synchronously

### 3. Post-Processing: Document & Parse

1. **Save output**:
   - Create `docs/code_reviews/` if needed
   - Write to `code_review_DDMMYY.md` (e.g., `code_review_161125.md`)
   - Include: timestamp, parameters, scope (uncommitted/full), findings
2. **Parse recommendations**:
   - Extract all actionable items from codex output
   - Create structured TodoWrite list with specific, actionable items
   - Each todo: "Fix [issue] in [file:line]" format
   - All todos start as `pending`

### 4. User Approval Gate

**STOP and ask user**:
> "Please review the todo list above. Reply 'approve' to proceed with fixes, or suggest changes."

- Wait for explicit approval
- Update todos if user suggests changes
- Only proceed after confirmation

### 5. Apply Fixes (After Approval Only)

- Mark ONE todo as `in_progress` before starting
- Apply fix using Edit/Write tools (**Claude Code** applies, not codex)
- Mark `completed` immediately after finishing
- Repeat for each todo systematically

### 6. Validation

Run project quality checks:

- `make lint` and/or `make format`
- `make test` (if applicable)
- Report any failures

## Usage Examples

```bash
/gpt-review --uncommitted                    # Review uncommitted changes
/gpt-review src/module.py                    # Review specific file
/gpt-review --focus "type safety"            # Review with focus
/gpt-review --uncommitted --focus "security" # Uncommitted + focus
```

## Critical Rules

- ✅ Use Skill tool to invoke "codex"
- ✅ Wait for user approval before applying fixes
- ✅ Save all reviews with timestamp
- ✅ Process codex output only once
- ❌ Never re-read or re-process codex output
- ❌ Never apply fixes without approval

## Testing & Validation Checklist

### Uncommitted Scope Validation

To verify `--uncommitted` reviews are properly scoped:

**Setup:**
1. Make some uncommitted changes to 2-3 files
2. Note the specific files changed (e.g., `fileA.py`, `fileB.md`)
3. Ensure other files in the repo are NOT changed

**Test Execution:**
1. Run `/gpt-review --uncommitted`
2. Check the review output in `docs/code_reviews/code_review_DDMMYY.md`

**Expected Results:**
- ✅ Review mentions ONLY the files you changed
- ✅ Review references specific line numbers from your changes
- ✅ Review does NOT mention unchanged files
- ✅ Saved output includes scope: "uncommitted changes (git diff HEAD)"

**Failure Indicators:**
- ❌ Review mentions files you didn't change
- ❌ Review appears to analyze the entire codebase
- ❌ No mention of specific uncommitted changes

### General Review Validation

For targeted file/directory reviews:

**Test Execution:**
1. Run `/gpt-review src/specific_file.py`
2. Check review output

**Expected Results:**
- ✅ Review focuses on the specified target
- ✅ Saved output includes correct target path
- ✅ Review doesn't analyze unrelated files
