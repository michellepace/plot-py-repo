# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Capabilities
**Purpose**: Visualize Python repository evolution through Git history

**Architecture**: UV Package Application with TDD, pure functions, layer separation

**Entry Point**: `viz-python-repo` CLI with subcommands for counting lines, generating CSV, and creating visualizations

## Core Architecture

**Key Modules**:
- `src/viz_python_repo/cli.py` - CLI entry point with subcommand routing
- `src/viz_python_repo/count_lines.py` - Line classification logic (code/docstrings/comments)
- `src/viz_python_repo/git_history.py` - Git history traversal and CSV generation
- `src/viz_python_repo/plot_evolution.py` - Stacked area chart generation (Plotly)
- `src/viz_python_repo/plot_modules.py` - Module breakdown bar chart (Plotly)

## Tech Stack

- **Python**: 3.13+
- **Key Patterns**: Use `pathlib` (not `os`), `pytest` with `tmp_path`
- **Visualization**: Plotly Express for charts, Kaleido for WebP export
- **Dependencies**: See [pyproject.toml](pyproject.toml) for complete list

## Commands

**UV Workflow Rules:**
- Use `uv run` - never activate venv
- Use `uv add` - never pip
- Use `pyproject.toml` - never requirements.txt

### Package Management
```bash
uv sync                              # Match packages to lockfile
uv add <pkg>                         # Add runtime dependency
uv add --dev <pkg>                   # Add dev dependency
uv tree                              # Show dependency tree
uv lock --upgrade-package <pkg>      # Update specific package
uv lock --upgrade && uv sync         # Update all packages and apply
```

### Application CLI
```bash
uv run viz-python-repo count-lines <file>                  # Count lines in Python file
uv run viz-python-repo generate-csv [repo_path] --output <csv>  # Generate CSV from Git history
uv run viz-python-repo plot-evolution <csv>                # Create stacked area chart
uv run viz-python-repo plot-modules <csv>                  # Create module bar chart
```

### Development Tools
```bash
uv run pytest                        # Run all tests
uv run pytest -v <test_file>::<test_function>  # Run specific test
uv run ruff check --fix              # Lint and auto-fix
uv run ruff format                   # Format code
uv run pre-commit run --all-files    # Run all pre-commit hooks
```

## Code Design Principles: Elegant Simplicity over Over-Engineered

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:
- **Pure functions preferred** - no side effects in business logic, easier to test
- **Clear module boundaries** - easier to test and understand
- **Single responsibility** - complex functions are hard to test

**Key Architecture Guidelines**:
- **Layer separation** - CLI → business logic → I/O
- **One module, one purpose** - Each `.py` file has a clear, focused role
- **Handle errors at boundaries** - Catch exceptions in CLI layer, not business logic
- **Type hints required** - All function signatures need type annotations
- **Descriptive naming** - Functions/variables should clearly indicate purpose and be consistent throughout

## TDD Implementation

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity
- Test incrementally: One test should drive one behaviour
- Use focused test names that describe what's being tested

## Code Quality Standards

- **Ruff**: Strictest settings (ALL rules enabled)
- **Pyright**: Configured to avoid Ruff duplicates (see [pyproject.toml](pyproject.toml))
- **Pre-commit**: Auto-runs on every commit
