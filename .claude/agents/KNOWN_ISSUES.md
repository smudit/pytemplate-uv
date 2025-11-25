# Known Issues and Workarounds

Common issues and their solutions when working with Claude Code agents.

## Textual UI Testing

### pilot.click() Not Working with ModalScreen Buttons

**Issue:** `pilot.click()` does not properly trigger `Button.Pressed` events in `ModalScreen` contexts, even though it's the recommended approach per Textual documentation.

**Root Cause:**
- `pilot.click()` simulates mouse clicks at screen coordinates
- `ModalScreen` intercepts click events before they reach child widgets
- This prevents the button's event handler from being invoked

**Workaround:** Use direct `button.press()` instead of `pilot.click()`:

```python
# ❌ This doesn't work reliably in ModalScreen
await pilot.click("#my-button")

# ✅ Use this pattern instead
button = app.screen.query_one("#my-button", Button)
button.press()
await pilot.pause()
```

**When to use this workaround:**
- Any button in a `ModalScreen` or `BaseModal` subclass
- When tests show button clicks not triggering expected behavior
- When you see "OutOfBounds" errors even with proper screen sizing

**Additional Considerations:**
- Increase test terminal size to `(80, 40)` or larger for modals with tall content
- This workaround tests the same functionality (button press handling)
- It's more direct and avoids coordinate-based clicking limitations
- Key presses still work fine with `await pilot.press("key")`

**Example Fix:**

```python
async def test_modal_button_dismiss(self) -> None:
    """Test modal button dismisses correctly."""
    app = TestApp()
    async with app.run_test(size=(80, 40)) as pilot:
        await pilot.pause()

        await app.push_screen(MyModal())
        await pilot.pause()

        # Direct button press instead of pilot.click()
        button = app.screen.query_one("#close-button", Button)
        button.press()
        await pilot.pause()

        assert len(app.screen_stack) == 1  # Modal dismissed
```

**Related Issues:**
- GitHub: Textualize/textual - Known issues with pilot.click and ModalScreen
- This is a framework limitation, not a testing mistake

**Status:** Workaround required until Textual fixes event propagation in ModalScreen

---

## Agent Tool Limitations

### Read Tool Line Limits

**Issue:** Read tool has default line limits that may truncate large files.

**Workaround:**
- Use `offset` and `limit` parameters to read files in chunks
- For very large files, use Grep to search specific patterns first
- Consider using Bash with `head`/`tail` for initial file inspection

```python
# Read first 100 lines
Read(file_path="/path/to/file.py", offset=0, limit=100)

# Read next 100 lines
Read(file_path="/path/to/file.py", offset=100, limit=100)
```

---

### Bash Command Timeouts

**Issue:** Long-running Bash commands may timeout (default: 2 minutes).

**Workaround:**
- Use `timeout` parameter to extend: `Bash(command="...", timeout=600000)` (10 min)
- For very long operations, use `run_in_background: true`
- Monitor with `BashOutput` tool

```python
# Long-running test suite
Bash(
    command="uv run pytest tests/",
    timeout=600000,  # 10 minutes
    description="Run full test suite"
)
```

---

## Codex Skill Issues

### Context Detection Fragility

**Issue:** Codex skill tries to detect context (code review vs general) which can be unreliable.

**Workaround:**
- Commands should pass explicit context via prompt
- Avoid relying on keyword detection
- Use dedicated commands for specific workflows

**Better Approach:**
```markdown
# In command that invokes codex skill
Skill: codex
Prompt: "[CONTEXT: code_review] Review the following changes..."
```

---

## Git Operations

### Untracked Files Not Showing in git diff

**Issue:** `git diff HEAD` doesn't show newly created files.

**Workaround:**
- Use `git status --porcelain` to find untracked files
- Combine: `git diff HEAD` + `git ls-files --others --exclude-standard`
- For reviews, consider: `git diff HEAD && git status --short`

---

## Performance Issues

### Slow Agent Initialization

**Issue:** Some agents (especially Opus-based) take time to initialize.

**Workaround:**
- Use Haiku for quick, simple tasks
- Use Sonnet for balanced performance/quality
- Reserve Opus for critical reviews only (e.g., lead_architect)

**Model Selection Guide:**
- **Haiku**: Quick code reviews, simple tasks (<30s)
- **Sonnet**: Most agents, balanced quality (30s-2min)
- **Opus**: Architecture reviews, critical analysis (2-5min)

---

## Directory Navigation

### Relative Path Issues

**Issue:** Agents may have different working directories than expected.

**Workaround:**
- Always use absolute paths when possible
- Check current directory with `pwd` if uncertain
- Use `Path(__file__).parent` pattern in Python

---

## Testing Coverage Reports

### Coverage.py Missing Branches

**Issue:** Branch coverage not tracked without explicit flag.

**Workaround:**
```bash
# Include branch coverage
pytest --cov=src --cov-branch --cov-report=term-missing

# Set in pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-branch --cov-report=term-missing"
```

---

## Reporting New Issues

If you encounter issues not listed here:

1. **Document clearly:**
   - Agent name
   - Command/action taken
   - Expected vs actual behavior
   - Error messages

2. **Create workaround** if possible

3. **Update this file** via PR or issue

4. **Check upstream:**
   - Claude Code GitHub: [anthropics/claude-code](https://github.com/anthropics/claude-code)
   - Textual GitHub: [Textualize/textual](https://github.com/Textualize/textual)

---

## See Also

- `README.md` - Agent overview and quick reference
- `AGENT_GUIDE.md` - Detailed usage patterns
- `.claude/references/` - Reference documentation
