# Repository Guidelines

## Project Structure & Module Organization
- `pytemplate/`: CLI entrypoints (`main.py`), template manager, logger, constants.
- `pytemplate/templates/`: cookiecutter scaffolds, config specs, and shared resources (coding rules, env examples); update `template_paths.yaml` when relocating templates.
- `tests/`: pytest suite covering CLI flows, template management, config validation, security, and integration cases.
- `docs/`: reference material and examples; update when template behavior changes.
- `Taskfile.yml`, `pyproject.toml`, `uv.lock`: tooling, tasks, and dependency definitions.

## Build, Test, and Development Commands
- Environment: `uv venv && source .venv/bin/activate && uv sync --all-extras` (or `task install:dev`).
- Run CLI locally: `uv run pytemplate --help`, `task run:create-config TYPE=lib`, `task run:create-project CONFIG=path/to/config.yaml`.
- Quality gates: `task format`, `task lint`, `task lint:fix`, `task typecheck`, `task check` (runs format check, lint, mypy).
- Tests: `task test` or `task test:verbose`; coverage targets via `task coverage`, `task coverage:html`, `task test-cov` (fails under 80% coverage).
- Build/publish: `task build`, `task publish:dry`.

## Coding Style & Naming Conventions
- Ruff + Black enforce 100-char lines, PEP8 naming, import sorting; run `task format` before pushing.
- Prefer snake_case for functions/modules, PascalCase for classes, SCREAMING_SNAKE_CASE for constants (see `pytemplate/constants.py`).
- Use type hints; keep Typer command functions small and composable.
- Template files use Jinja variables (e.g., `{{cookiecutter.project_name}}`); keep names aligned with `cookiecutter.json` to avoid broken renders.

## Testing Guidelines
- Add tests in `tests/` mirroring target modules; files start with `test_`, functions with `test_*`.
- For CLI flows, reuse fixtures in `tests/conftest.py` (`temp_project_dir`, `temp_templates_dir`, etc.) to isolate filesystem effects.
- Prefer assertions on generated file contents/structure over only exit codes; add regression tests for new flags and edge cases.
- Enforce coverage locally with `task test-cov`; HTML report at `htmlcov/index.html` when needed.

## Commit & Pull Request Guidelines
- Use conventional commits with optional emoji prefix seen in history (e.g., `✨ feat(template): ...`, `chore: ...`, `fix:`); imperative mood, include scope when helpful.
- Run `task check` and `task test-cov` before opening PRs; paste notable outputs for reviewers when fixing failures.
- PRs should describe intent, list tests run, link issues, and call out template or docs updates (attach example generated files or screenshots when UX changes).
- Never commit secrets; keep example values in `*.example` or config templates.
