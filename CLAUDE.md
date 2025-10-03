# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository (British spelling)

## Project Capabilities

- **Purpose**: Visualise Python repository evolution through Git history
- **Architecture**: UV Package Application with TDD, pure functions, layer separation
- **Entry Point**: `plot-py-repo` CLI - analyses Git history and creates visualisations

## Tech Stack

- **Python**: 3.13+
- **Testing**: pytest with `tmp_path` fixtures
- **Visualisation**: Plotly Express for charts, Kaleido for WebP export
- **Dependencies**: See [pyproject.toml](pyproject.toml) for complete list

## Core Architecture

**Data Flow:**
- CLI → `git_history.generate_csv()` (traverse commits → calls count_lines → writes CSV)
- CLI → `visualise.create_charts()` (orchestrates chart generation)
  - `_load_and_exclude_files()` → filters CSV data
  - `chart_evolution.create()` → generates evolution chart
  - `chart_breakdown.create()` → generates breakdown chart

**Key Modules:**
- `cli.py`: CLI entry point (simple single-command interface)
- `git_history.py`: Traverses Git commits, extracts files, calls count_lines, writes CSV
- `count_lines.py`: Pure utility: classifies Python source lines (no I/O)
- `visualise.py`: Orchestrator: loads/filters CSV, delegates to chart modules
- `chart_evolution.py`: Creates stacked area chart showing evolution over time
- `chart_breakdown.py`: Creates horizontal bar chart showing file breakdown
- `theme.py`: Centralised Plotly theming (layout settings)

## Commands

**UV Workflow Rules:**
- Use `uv run` - never activate venv
- Use `uv add` - never pip
- Use `pyproject.toml` - never requirements.txt

### Package Management
```bash
uv sync                             # Match packages to lockfile
uv add <pkg>                        # Add runtime dependency
uv add --dev <pkg>                  # Add dev dependency
uv tree                             # Show dependency tree
uv lock --upgrade-package <pkg>     # Update specific package
uv lock --upgrade && uv sync        # Update all packages and apply
```

### Application CLI
```bash
uv run plot-py-repo                  # Visualise cwd repo (creates CSV + charts)
uv run plot-py-repo /path/to/repo             # Visualise different repo
uv run plot-py-repo --csv history.csv         # Regenerate charts from existing CSV
uv run plot-py-repo --output-dir ./reports    # Save all outputs to ./reports
```

**Note**: `repo_path` and `--csv` are mutually exclusive (cannot use both together)

### Development Tools
```bash
uv run pytest                                   # Run all tests
uv run pytest -v <test_file>::<test_function>   # Run specific test
uv run ruff check --fix                         # Lint and auto-fix
uv run ruff format                              # Format code
uv run pre-commit run --all-files               # Run all pre-commit hooks
```

## Code Design Principles: Elegant Simplicity over Over-Engineered

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:
- **Pure functions preferred**: no side effects in business logic, easier to test
- **Clear module boundaries**: easier to test and understand
- **Single responsibility**: complex functions are hard to test

**Key Architecture Guidelines**:
- **Layer separation**: CLI → business logic → I/O
- **One module, one purpose**: Each `.py` file has a clear, focused role
- **Handle errors at boundaries**: Catch exceptions in CLI layer, not business logic
- **Type hints required**: All function signatures need type annotations
- **Descriptive naming**: Functions/variables indicate purpose clearly and consistently
- **Use pathlib**: Always use `pathlib` (not `os`) for file operations

## TDD Implementation

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity
- For each test target one behavior with clear failure point
- Use focused test names that describe what's being tested

## Code Quality Standards

- **Naming is important!**: Function and variable names chosen to self-document clarity
- **Docstrings & Comments**: Concise, clear, fresh ➜ important for LLM comprehension
- **Ruff**: Strictest linting settings (ALL rules enabled)
- **Pyright**: Type checking configured in pyproject.toml (not yet in pre-commit hook)
- **Pre-commit hooks**: Runs uv-lock, ruff-check, ruff-format, pytest on every commit