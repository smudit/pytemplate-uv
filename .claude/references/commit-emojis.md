# Commit Message Emoji Reference

Complete emoji reference for conventional commit messages used by the `/git-commit` command.

## Core Commit Types

- ✨ **feat**: New feature
- 🐛 **fix**: Bug fix
- 📝 **docs**: Documentation
- 💄 **style**: Formatting/style
- ♻️ **refactor**: Code refactoring
- ⚡️ **perf**: Performance improvements
- ✅ **test**: Tests
- 🔧 **chore**: Tooling, configuration

## Extended Emoji Mapping

### Development Workflow
- 🚀 **ci**: CI/CD improvements
- 🗑️ **revert**: Reverting changes
- 🧪 **test**: Add a failing test
- 🚨 **fix**: Fix linter/type-check warnings
- 🔒️ **fix**: Fix security issues
- 👥 **chore**: Add or update contributors
- 🚚 **refactor**: Move or rename resources
- 🏗️ **refactor**: Make architectural changes
- 🔀 **chore**: Merge branches
- 📦️ **chore**: Add or update compiled files or packages
- ➕ **chore**: Add a dependency
- ➖ **chore**: Remove a dependency
- 🌱 **chore**: Add or update seed files
- 🧑‍💻 **chore**: Improve developer experience

### Feature Development
- 🧵 **feat**: Add or update code related to multithreading or concurrency
- 🔍️ **feat**: Improve SEO
- 🏷️ **feat**: Add or update types
- 💬 **feat**: Add or update text and literals
- 🌐 **feat**: Internationalization and localization
- 👔 **feat**: Add or update business logic
- 📱 **feat**: Work on responsive design
- 🚸 **feat**: Improve user experience / usability

### Bug Fixes & Patches
- 🩹 **fix**: Simple fix for a non-critical issue
- 🥅 **fix**: Catch errors
- 👽️ **fix**: Update code due to external API changes
- 🔥 **fix**: Remove code or files
- 🚑️ **fix**: Critical hotfix
- ✏️ **fix**: Fix typos
- 💚 **fix**: Fix CI build
- 🔇 **fix**: Remove logs

### Code Quality
- 🎨 **style**: Improve structure/format of the code
- 💡 **docs**: Add or update comments in source code
- ⚰️ **refactor**: Remove dead code

### Project Management
- 🎉 **chore**: Begin a project
- 🔖 **chore**: Release/Version tags
- 🚧 **wip**: Work in progress
- 📌 **chore**: Pin dependencies to specific versions
- 👷 **ci**: Add or update CI build system
- 📄 **chore**: Add or update license
- 💥 **feat**: Introduce breaking changes
- 🙈 **chore**: Add or update .gitignore file
- ⏪️ **revert**: Revert changes

### Data & Analytics
- 📈 **feat**: Add or update analytics or tracking code
- 🗃️ **db**: Perform database related changes
- 🔊 **feat**: Add or update logs

### Testing & Quality Assurance
- 📸 **test**: Add or update snapshots
- 🤡 **test**: Mock things
- ⚗️ **experiment**: Perform experiments

### User Experience
- 🍱 **assets**: Add or update assets
- ♿️ **feat**: Improve accessibility
- 💫 **ui**: Add or update animations and transitions
- 🥚 **feat**: Add or update an easter egg

### Feature Flags & Configuration
- 🚩 **feat**: Add, update, or remove feature flags
- 🦺 **feat**: Add or update code related to validation
- ✈️ **feat**: Improve offline support

## Usage Examples

### Simple Commits
```
✨ feat: add user authentication system
🐛 fix: resolve memory leak in rendering process
📝 docs: update API documentation with new endpoints
♻️ refactor: simplify error handling logic in parser
```

### Commits with Scope
```
🔒️ fix(auth): strengthen authentication password requirements
⚡️ perf(database): optimize user query performance
🎨 style(components): reorganize component structure
🧑‍💻 chore(cli): improve developer tooling setup process
```

### Detailed Commit Example
```
🐛 fix(auth): resolve JWT token validation issue

- Fix incorrect signature verification in token validator
- Add proper error handling for expired tokens
- Update token refresh logic to handle edge cases
- Add logging for debugging token failures

This fixes the critical issue where valid tokens were being
rejected after server restart due to incorrect key loading.

Closes #234
```

## Commit Type Detection Patterns

The `/git-commit` command automatically detects commit types based on content:

### Bug Fix Detection (`fix:`)
- Keywords: `fix`, `bug`, `resolve`, `issue`, `error`, `crash`, `patch`
- Patterns: Exception handling, null checks, boundary conditions

### Feature Detection (`feat:`)
- New files or functions
- Keywords: `add`, `implement`, `create`, `introduce`, `new`
- Patterns: New classes, endpoints, components

### Performance Detection (`perf:`)
- Keywords: `optimize`, `speed`, `performance`, `cache`, `lazy`
- Patterns: Algorithm improvements, caching, query optimization

### Refactoring Detection (`refactor:`)
- Keywords: `refactor`, `restructure`, `reorganize`, `extract`, `simplify`
- Patterns: Moving code, renaming, extracting methods

## Best Practices

1. **Be Specific**: Choose the emoji that best matches your change
2. **Use Scope**: Add scope when changes affect specific module: `🐛 fix(auth): ...`
3. **Keep First Line Short**: Under 72 characters including emoji
4. **Add Context in Body**: Explain why, not just what
5. **Reference Issues**: Include `Closes #123` or `Relates to #456`
6. **Breaking Changes**: Use 💥 and add `BREAKING CHANGE:` in footer

## See Also

- `.claude/commands/git-commit.md` - Full git-commit command documentation
- [Conventional Commits](https://www.conventionalcommits.org/) - Specification
- [Gitmoji](https://gitmoji.dev/) - Emoji guide for commit messages
