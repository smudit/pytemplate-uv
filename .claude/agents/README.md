# Custom Claude Code Agents

This directory contains custom subagent definitions for the MS AI Assistant project.

## Quick Reference

| Agent | Purpose | Model | Use When |
|-------|---------|-------|----------|
| **wireframe-generator** | Analyze UI code → Generate wireframes | Sonnet | Documenting existing UI |
| **textual-ui-developer** | Wireframe specs → Textual Python code | Sonnet | Implementing TUI components |
| **textual-ui-tester** | Write async tests for Textual components | Sonnet | Testing TUI with pytest |
| **textual-tui-designer** | Design Textual UI from requirements | Sonnet | UI/UX design for TUI |
| **lead_architect** | Review implementation plans | Opus | **MANDATORY** plan reviews |
| **backend-architect** | Design APIs, databases, architecture | Sonnet | Backend system design |
| **changes-reviewer** | Bug detection and code quality review | Sonnet | **PROACTIVE** code reviews |
| **test_engineer** | Maintain and sync test suites | Sonnet | Test updates and coverage |

## Usage Patterns

### Automatic Delegation
Claude will automatically use agents when appropriate:
```
You: "Generate wireframes from the chat UI code"
→ Invokes wireframe-generator automatically
```

### Explicit Request
```
You: "Use the lead_architect agent to review the plan in docs/plans/plan_xyz.md"
→ Explicitly invokes specific agent
```

### Proactive Use
Some agents should be used proactively:
- **lead_architect**: Reviews ALL plans from `/plan` command
- **changes-reviewer**: Reviews code after modifications
- **test_engineer**: Updates tests after code changes

## Core Agents

### wireframe-generator
**Analyzes Python UI code → Generates markdown wireframes**

- Supported frameworks: Textual, Tkinter, PyQt, Kivy, Rich
- Outputs: Component hierarchies, ASCII wireframes, navigation flows
- Tools: Read, Grep, Glob, Write

**Example:** "Generate wireframes from ms_ai_assistant/chat_app/"

### textual-ui-developer
**Wireframe specs → Working Textual Python code**

- Implements layouts, screens, widgets from design docs
- Handles TCSS styling and keyboard bindings
- Does NOT implement business logic

**Example:** "Implement the chat message component from wireframes_main.md"

### lead_architect ⭐
**Senior architect for plan reviews (MANDATORY for /plan)**

- Reviews implementation plans before development
- Validates architecture, security, scalability
- Provides approval status: ✅ APPROVED | ⚠️ CONDITIONS | ❌ REVISIONS
- Uses Opus model for highest quality reviews

**Workflow:** `/plan` command → lead_architect review → User approval → Implementation

### backend-architect
**API and backend system architecture specialist**

- Designs RESTful/GraphQL APIs with OpenAPI specs
- Plans database schemas, caching, scaling strategies
- Creates architecture diagrams (Mermaid)

**Example:** "Design API architecture for multi-tenant SaaS platform"

### changes-reviewer ⭐
**Proactive code review for bugs and quality (Use after code changes)**

- Focuses on: bugs, logic errors, security issues
- Priority-based findings: CRITICAL, HIGH, MEDIUM, LOW
- Runs automatically or manually invoked

**Example:** Use `/review-unified --deep` after making changes

### test_engineer
**Python test suite maintenance and synchronization**

- Updates tests when code changes
- Ensures coverage of new functionality
- Uses: pytest, pytest-cov, unittest, mocks

**Example:** "Update tests for the new authentication module"

## Textual TUI Specialists

### textual-ui-tester
**Async testing for Textual applications**

- Uses pytest with `app.run_test()` and Pilot API
- Snapshot testing with pytest-textual-snapshot
- See: `KNOWN_ISSUES.md` for pilot.click() workaround

### textual-tui-designer
**UI/UX design for Textual applications**

- Analyzes requirements → Creates UI designs
- Generates wireframes with component mapping
- Asks clarifying questions before designing

## Wireframe Documentation

Project wireframes located at:
- `ms_ai_assistant/chat_app/docs/wireframes_index.md` - Overview
- `ms_ai_assistant/chat_app/docs/wireframes_main.md` - Core layouts
- `ms_ai_assistant/chat_app/docs/wireframes_states.md` - State variations
- `ms_ai_assistant/chat_app/docs/wireframes_special_views.md` - Modals
- `ms_ai_assistant/chat_app/docs/wireframes_components.md` - Technical specs

## Creating New Agents

1. Create `.md` file in `.claude/agents/`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: my-agent
   description: Clear description of when to use
   tools: Read, Write, Edit
   model: sonnet
   ---
   ```
3. Write detailed system prompt below frontmatter
4. Verify with `/agents` command in Claude Code

## Best Practices

1. **Single Responsibility**: One clear purpose per agent
2. **Descriptive Names**: Use when-to-use descriptions
3. **Minimal Tools**: Only grant necessary tool access
4. **Clear Prompts**: Provide specific, actionable instructions
5. **Document Integration**: Update README when adding agents

## See Also

- `AGENT_GUIDE.md` - Detailed usage guide and patterns
- `KNOWN_ISSUES.md` - Workarounds for agent limitations
- `.claude/commands/` - Slash commands that use agents
- [Claude Code Docs](https://docs.claude.com/claude-code) - Official documentation

## Version History

| Date | Agent | Changes |
|------|-------|---------|
| 2025-11-22 | - | Documentation restructure: Split into README, GUIDE, KNOWN_ISSUES |
| 2025-11-18 | lead_architect | Initial creation for plan reviews |
| 2025-11-16 | wireframe-generator | Initial creation |
| 2025-11-06 | backend-architect | Initial creation |
| 2025-11-05 | textual-ui-tester | Initial creation |
| 2025-11-05 | textual-ui-developer | Initial creation |
