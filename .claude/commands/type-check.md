# Type Check Command

Run comprehensive mypy type checking on the entire codebase and provide actionable feedback.

## Instructions

You are a Python type checking assistant. Your task is to:

1. **Run mypy type checking**:
   - Execute `uv run mypy .` to check all Python files
   - Capture all output including errors, warnings, and summary

2. **Analyze the results**:
   - Count total errors found
   - Group errors by:
     - File (show which files have the most issues)
     - Error type (e.g., missing type hints, incompatible types, etc.)
   - Identify patterns in the errors

3. **Present findings clearly**:
   - Show summary statistics (total errors, files affected)
   - List the top 10 most critical errors with file:line references
   - Group similar errors together
   - Highlight any blocking issues vs. minor type hints

4. **Provide recommendations**:
   - Suggest whether errors should be fixed:
     - Automatically (patterns that can be batch-fixed)
     - Manually (complex type issues requiring human judgment)
     - Deferred (low-priority improvements)
   - Offer to fix common patterns if appropriate

## Output Format

Structure your response as:

```
## Type Check Results

**Summary:**
- Total errors: X
- Files affected: Y
- Error categories: Z

**Top Issues:**
[List top 10 errors with file:line:column references]

**Error Breakdown:**
[Group errors by type/pattern]

**Recommendations:**
[Actionable next steps]
```

## Important Notes

- Use `uv run mypy .` (NOT just `mypy`)
- Parse output to provide file:line references in the format `file_path:line_number`
- Focus on actionable feedback
- If there are 0 errors, celebrate and confirm type safety!
- If there are >100 errors, suggest focusing on high-priority files first
