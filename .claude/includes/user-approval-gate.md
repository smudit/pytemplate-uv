# User Approval Gate Pattern

Common pattern for getting user approval before proceeding with changes.

## Usage

Include this section in commands that modify code or apply fixes.

## Pattern

### Before Applying Changes

**STOP and ask user:**

> "I've analyzed the changes and created a plan. Please review:
>
> [Summary of findings]
>
> **Proposed Actions:**
> [List of specific actions to take]
>
> Type 'approve' to proceed, 'modify' to adjust the plan, or 'cancel' to stop."

### Wait for Response

- **"approve"** or **"yes"** → Proceed with implementation
- **"modify"** → Ask what changes user wants, update plan, re-confirm
- **"cancel"** or **"no"** → Stop execution, save current state

### After Approval

- Begin implementation
- Mark first todo as `in_progress`
- Execute changes systematically
- Mark each todo as `completed` after finishing

## Example Implementation

```markdown
### Step 4: User Approval Gate

**REQUIRED**: Before applying ANY fixes, present findings to user:

1. **Display summary:**
   - Total items found: X
   - Critical/High priority: Y
   - Estimated time: Z minutes

2. **Ask user**: "Type 'approve' to proceed with fixes, 'skip' to continue without changes, or 'stop' to exit."

3. **Wait for user response:**
   - If "approve" → proceed to next step
   - If "skip" → skip to validation phase
   - If "stop" → exit workflow

**NEVER apply changes without explicit approval.**
```

## Best Practices

1. **Be specific**: Show exactly what will change
2. **Provide context**: Explain why changes are needed
3. **Give options**: Don't force a single path
4. **Respect choice**: If user says no, don't proceed
5. **Save state**: If cancelled, save progress so user can resume later

## Anti-Patterns (Avoid)

- ❌ Applying changes before asking
- ❌ Assuming "silence means yes"
- ❌ Asking but not waiting for response
- ❌ Re-asking after user says no
- ❌ Making approval optional with defaults
