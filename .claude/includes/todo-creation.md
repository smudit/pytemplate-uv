# Todo Creation Pattern

Standard pattern for creating and managing todos in commands.

## When to Use TodoWrite

Use the TodoWrite tool when:
- Task requires 3+ distinct steps
- Task is non-trivial and complex
- User explicitly requests todo tracking
- You need to track progress across multiple files/operations

## Todo Structure

Each todo must have:
- `content`: Imperative form ("Fix bug in auth.py")
- `activeForm`: Present continuous ("Fixing bug in auth.py")
- `status`: One of `pending`, `in_progress`, `completed`

## Pattern

### 1. Initial Todo List Creation

```markdown
Create TodoWrite list at start of complex task:

[
  {"content": "Analyze current implementation", "status": "pending", "activeForm": "Analyzing current implementation"},
  {"content": "Design solution approach", "status": "pending", "activeForm": "Designing solution approach"},
  {"content": "Implement core functionality", "status": "pending", "activeForm": "Implementing core functionality"},
  {"content": "Write tests", "status": "pending", "activeForm": "Writing tests"},
  {"content": "Run validation checks", "status": "pending", "activeForm": "Running validation checks"}
]
```

### 2. Working Through Todos

**CRITICAL RULE**: Exactly ONE todo must be `in_progress` at any time.

```markdown
# Before starting work
Mark current todo as in_progress

# Do the work
[Execute the task]

# Immediately after completing
Mark todo as completed

# Move to next
Mark next todo as in_progress
```

### 3. Dynamic Todo Updates

Add new todos if discoveries made during implementation:

```markdown
# If you discover additional work needed
Add new todo to the list with pending status
Update existing todos if needed
Keep user informed of changes
```

### 4. Completion

```markdown
# When all todos completed
Present summary of what was accomplished
Highlight any deviations from original plan
Suggest next steps if applicable
```

## Best Practices

1. **Be specific**: "Fix null check in auth.py:45" not "Fix bugs"
2. **Break down**: Large tasks into 3-7 smaller todos
3. **Update frequently**: Mark completed immediately, not in batches
4. **One at a time**: Never have 2+ todos in_progress
5. **Reflect reality**: If todo isn't needed, remove it entirely

## Examples

### Good Todo List
```json
[
  {"content": "Read user.py to understand current auth logic", "status": "completed", "activeForm": "Reading user.py"},
  {"content": "Add type hints to login() function", "status": "in_progress", "activeForm": "Adding type hints to login()"},
  {"content": "Add type hints to logout() function", "status": "pending", "activeForm": "Adding type hints to logout()"},
  {"content": "Run mypy validation", "status": "pending", "activeForm": "Running mypy validation"}
]
```

### Bad Todo List (Anti-patterns)
```json
[
  {"content": "Fix stuff", "status": "pending", "activeForm": "Fixing stuff"},  // ❌ Too vague
  {"content": "Update code", "status": "in_progress", "activeForm": "Updating code"},  // ❌ Multiple in_progress
  {"content": "Test", "status": "in_progress", "activeForm": "Testing"},  // ❌ Multiple in_progress
  {"content": "Write documentation maybe", "status": "pending", "activeForm": "Writing documentation"}  // ❌ Uncertain
]
```

## Integration with Commands

Commands should:
1. Create initial todo list at start (if task is complex)
2. Reference todos in output ("Working on todo 3/5...")
3. Update todos in real-time as work progresses
4. Remove todos that become irrelevant
5. Add todos if new work discovered

## See Also

- Claude Code documentation on TodoWrite tool
- `.claude/includes/user-approval-gate.md` - Approval pattern (often used before todos)
