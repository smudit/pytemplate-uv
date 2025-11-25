# GPT Plan Command

Create a **comprehensive implementation plan** for updating existing features or adding new features using the codex skill. This command **DOES NOT make code changes** - it only produces a plan with **mandatory architecture review** by the lead_architect agent before creating todos.

## Parameters

Extract from user request or use defaults (DO NOT prompt for missing parameters):

- **feature**: Description of the feature to add or update (required, extracted from request)
- **target**: Specific file/directory scope (default: infer from feature description)
- **focus**: Specific aspects to consider (e.g., "architecture, testing, security") - optional
- **model**, **reasoning**: Passed to codex skill (skill provides defaults)

## Workflow

**High-Level Flow**:

1. Understand feature scope and requirements
2. Generate plan using codex skill
3. Save plan document
4. **Submit plan to lead_architect agent for review** (MANDATORY)
5. If approved: Create todo list → User approval gate → Implementation
6. If revisions required: Present to user → Wait for guidance → Update plan

### 1. Pre-Processing: Understand Feature Scope

- Parse user's feature request to understand:
  - Is this a new feature or update to existing feature?
  - What components/files are likely affected?
  - What is the desired outcome?
- Use codebase exploration if needed to identify relevant files/patterns
- Note the scope for documentation

### 2. Execute Planning: Invoke Codex Skill

Use the Skill tool to invoke "codex" (NOT direct Bash):

- Context: "planning" (tells skill to focus on implementation strategy)
- Task: "Create a detailed implementation plan for: [feature description]"
- Pass parameters: model, reasoning, target (if specified), focus
- Skill handles codex execution in read-only mode
- Request codex to provide:
  - Architectural considerations
  - **Mermaid architecture diagrams** (REQUIRED for architectural changes):
    - Current architecture (before changes)
    - Proposed architecture (after changes)
    - Component relationships and data flow
    - Use appropriate diagram types: flowchart, sequence, class, or component diagrams
  - Files to create/modify
  - Implementation steps with rationale
  - Testing requirements
  - Potential risks/challenges
  - Dependencies and prerequisites
- Capture full output synchronously

### 3. Post-Processing: Document & Structure

1. **Save output**:
   - Create `docs/plans/` directory if needed
   - Write to `plan_gpt_DDMMYY-HH:MM.md` (e.g., `plan_gpt_161125-14:30.md`)
   - Include:
     - Timestamp
     - Feature description
     - Full codex planning output
     - Scope and affected components

### 4. Architecture Review

**CRITICAL**: Before creating todos, the plan MUST be reviewed by the lead_architect agent.

1. **Invoke Lead Architect**:
   - Use the Task tool with `subagent_type="lead_architect"`
   - Pass the plan file path for review
   - Request comprehensive architecture review covering:
     - Design patterns and SOLID principles
     - Security considerations
     - Testing strategy
     - Scalability and performance
     - Best practices adherence
   - Wait for review completion

2. **Process Review Results**:
   - Save review to `docs/plans/review_gpt_DDMMYY-HH:MM.md` alongside the plan
   - Examine the review status:
     - **✅ APPROVED**: Proceed to create todo list (step 5)
     - **⚠️ APPROVED WITH CONDITIONS**: Proceed to create todo list, note conditions in first todo
     - **❌ REVISIONS REQUIRED**: Go to step 4.3

3. **Handle Required Revisions**:
   - Present the architect's recommendations to the user:
     > "The lead architect has reviewed the implementation plan and identified critical issues that need to be addressed:
     >
     > [List critical issues from review]
     >
     > **Recommendations**:
     > [List recommendations from review]
     >
     > Please review the full architecture review in `docs/plans/review_gpt_DDMMYY-HH:MM.md` and provide your feedback. Would you like to:
     > 1. Revise the plan based on these recommendations
     > 2. Proceed anyway (explain why)
     > 3. Discuss specific concerns"
   - **STOP and wait** for user response
   - Do NOT create todo list until user provides guidance
   - Update plan based on user feedback if requested
   - Re-submit to lead_architect if significant changes made

### 5. Create Todo List

**Only proceed here if plan is approved by lead_architect (with or without conditions)**

1. **Parse implementation steps**:
   - Extract all actionable tasks from codex output
   - Incorporate any conditions from architecture review as first todos
   - Create structured TodoWrite list with specific, granular tasks
   - Each todo: Clear action item (e.g., "Create User model in models/user.py", "Add authentication middleware")
   - Organize by implementation order (dependencies first)
   - All todos start as `pending`

### 6. User Approval Gate

**STOP and ask user**:
> "I've created a detailed implementation plan and saved it to docs/plans/plan_gpt_DDMMYY-HH:MM.md. Please review the plan and todo list above. Reply 'approve' to proceed with implementation, or provide feedback to adjust the plan."

- Wait for explicit approval or feedback
- If user suggests changes, update the plan and todos accordingly
- **CRITICAL**: DO NOT implement any changes until user explicitly approves
- Only after approval, mark first todo as `in_progress` and begin implementation

### 7. Plan Output Format

The saved plan document should include:

```markdown
# Implementation Plan: [Feature Name]

**Generated**: [Timestamp]
**Requested by**: User
**Scope**: [Target files/directories]

## Feature Description
[User's feature request]

## Architectural Overview
[High-level approach and design decisions]

## Architecture Diagrams

### Current Architecture
```mermaid
[Mermaid diagram showing current system architecture]
```

### Proposed Architecture

```mermaid
[Mermaid diagram showing architecture after changes]
```

### Component Interactions

```mermaid
[Mermaid sequence/flowchart diagram showing data flow and component interactions]
```

**Note**: Mermaid diagrams are REQUIRED when the plan involves:

- New components or modules
- Changes to system architecture
- Modified data flow or component relationships
- New API endpoints or service integrations

## Implementation Steps

[Detailed steps from codex with rationale]

## Files to Create/Modify

[List of affected files with brief descriptions]

## Testing Strategy

[How to test the implementation]

## Risks and Considerations

[Potential challenges and mitigation strategies]

## Dependencies

[External libraries or prerequisites needed]

## Estimated Complexity

[Brief assessment of implementation complexity]

```

## Usage Examples

```bash
/gpt-plan Add user authentication with JWT tokens
/gpt-plan Update chat handler to support streaming responses
/gpt-plan Create metrics dashboard for tracking usage --focus "performance, scalability"
/gpt-plan Refactor database layer to use async SQLAlchemy --target src/db/
```

## Critical Rules

- ✅ Use Skill tool to invoke "codex" for planning
- ✅ Save plan with timestamp including time (HH:MM)
- ✅ **MANDATORY**: Submit plan to lead_architect agent for review
- ✅ Save architecture review alongside plan
- ✅ If revisions required, present to user and wait for guidance
- ✅ Only create todo list AFTER architect approval
- ✅ Create structured, actionable todo list
- ✅ **Generate Mermaid diagrams** for architectural changes (current vs. proposed)
- ✅ Include appropriate diagram types: flowchart, sequence, class, or component diagrams
- ✅ Wait for user approval before ANY implementation
- ✅ Plan should be comprehensive and consider architecture, testing, security
- ❌ NEVER make code changes during planning phase
- ❌ NEVER skip architecture review step
- ❌ NEVER create todos before architect review
- ❌ NEVER skip user approval gate
- ❌ NEVER proceed to implementation without explicit approval
- ❌ NEVER omit architecture diagrams when changes affect system structure

## After Approval

Once user approves the plan:

1. Mark first todo as `in_progress`
2. Begin systematic implementation following the plan
3. Mark each todo as `completed` immediately after finishing
4. Run quality checks (`make lint`, `make format`, `make test`) after implementation
5. Report results to user
