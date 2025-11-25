---
name: codex
description: Use when the user asks to run Codex CLI (codex exec, codex resume) or references OpenAI Codex for code analysis, refactoring, or automated editing
---

# Codex Skill: Technical Execution Guide

This skill provides instructions for **how to execute codex CLI** properly. Workflow orchestration is handled by commands (e.g., `/codex-review`).

## Execution Context Detection

Determine the context before executing:

**1. Code Review Context** (invoked by `/codex-review` or context contains "code review"):

- Use defaults WITHOUT prompting: `gpt-5.1-codex`, `medium` reasoning
- Override only if user explicitly specifies model/reasoning

**2. General/Interactive Context** (direct user request like "use codex to..."):

- Ask user (via `AskUserQuestion`) in a **single prompt with two questions**:
  - Which model: `gpt-5.1-codex` or `gpt-5.1`
  - Which reasoning: `high`, `medium`, or `low`

## Building the Codex Command

### Required Flags (Always Use)

- `--skip-git-repo-check` - Required for all commands
- `2>/dev/null` - Suppress thinking tokens (unless user explicitly requests them)

### Model & Reasoning

```bash
-m <MODEL>                                    # gpt-5-codex or gpt-5
--config model_reasoning_effort="<LEVEL>"    # high, medium, or low
```

### Sandbox Modes

Select based on task requirements:

| Mode | Use Case | Flag |
|------|----------|------|
| Read-only | Analysis, review, read-only tasks | `--sandbox read-only` |
| Workspace Write | Apply local edits, refactoring | `--sandbox workspace-write --full-auto` |
| Full Access | Network access, broad permissions | `--sandbox danger-full-access --full-auto` |

**Default**: `--sandbox read-only` (safest option)

### Optional Flags

- `-C <DIR>` - Run from specific directory
- Prompt via stdin or as final argument

### Resume Sessions

```bash
# Resume with new prompt (inherit all settings from original session)
echo "your prompt here" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

**Important**:

- Flags go between `exec` and `resume` ONLY if explicitly requested
- Resume inherits model, reasoning, and sandbox from original session

## Example Commands

### Code Review (Read-Only)

```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only \
  --skip-git-repo-check \
  -C /path/to/project \
  "Perform comprehensive code review focusing on type safety and error handling" 2>/dev/null
```

### Interactive Refactoring (Workspace Write)

```bash
codex exec -m gpt-5 \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  "Refactor authentication module to use async/await" 2>/dev/null
```

### Resume Previous Session

```bash
echo "Now add comprehensive error handling" | \
  codex exec --skip-git-repo-check resume --last 2>/dev/null
```

## Post-Execution Guidelines

### For General/Interactive Usage

- After completion, inform user: *"You can resume this session anytime by saying 'codex resume'"*
- Use `AskUserQuestion` to confirm next steps or gather clarifications
- Restate chosen model, reasoning, and sandbox mode when proposing follow-ups

### For Code Review Context

- Return output to calling command for post-processing
- Command handles: saving output, creating todos, user approval, applying fixes
- Do NOT create todos or apply fixes in skill - command orchestrates this

## Error Handling

**Stop and report** if:

- `codex --version` fails (codex not installed/configured)
- `codex exec` exits non-zero (execution error)
- Request user direction before retrying

**Permission requirements**:

- `--sandbox read-only` + `--skip-git-repo-check`: Always safe, no permission needed
- `--full-auto`, `--sandbox workspace-write/danger-full-access`: Ask permission via `AskUserQuestion` (unless code review context)

**Warnings/partial results**:

- General usage: Summarize and ask how to adjust
- Code review: Return output with warnings; command handles reporting
