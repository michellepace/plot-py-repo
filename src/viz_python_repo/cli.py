"""Command-line interface for viz-python-repo."""

import argparse
import sys
from pathlib import Path

from .count_lines import classify_lines
from .git_history import generate_csv


def cmd_count_lines(args: argparse.Namespace) -> None:
    """Count lines in a Python file.

    Args:
        args: Parsed command-line arguments with 'file' attribute
    """
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"Error reading file: {e}")
        sys.exit(1)

    docstring_lines, comment_lines, code_lines = classify_lines(content)

    print(f"Actual code lines: {code_lines:>3}")
    print(f"Docstring lines:   {docstring_lines:>3}")
    print(f"Comment lines:     {comment_lines:>3}")
    print()
    print(f"line_count_code:                 {code_lines:>3}")
    print(f"line_count_docstrings_comments:  {docstring_lines + comment_lines:>3}")


def cmd_generate_csv(args: argparse.Namespace) -> None:
    """Generate CSV from Git commit history.

    Args:
        args: Parsed command-line arguments with 'repo_path' and 'output' attributes
    """
    generate_csv(args.repo_path, args.output)


def cmd_plot_evolution(args: argparse.Namespace) -> None:
    """Create stacked area chart of repository evolution.

    Args:
        args: Parsed command-line arguments with 'csv' attribute
    """
    print(f"plot-evolution: Not yet implemented (would process {args.csv})")
    print("Coming soon: Stacked area chart showing codebase growth over time")


def cmd_plot_modules(args: argparse.Namespace) -> None:
    """Create bar chart of module breakdown.

    Args:
        args: Parsed command-line arguments with 'csv' attribute
    """
    print(f"plot-modules: Not yet implemented (would process {args.csv})")
    print("Coming soon: Bar chart showing lines per module")


def main() -> None:
    """Main entry point for viz-python-repo CLI."""
    parser = argparse.ArgumentParser(
        prog="viz-python-repo",
        description="Visualize Python repository evolution through Git history",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # count-lines subcommand
    parser_count = subparsers.add_parser(
        "count-lines", help="Count lines in a Python file"
    )
    parser_count.add_argument("file", help="Path to Python file")
    parser_count.set_defaults(func=cmd_count_lines)

    # generate-csv subcommand
    parser_csv = subparsers.add_parser(
        "generate-csv", help="Generate CSV from Git commit history"
    )
    parser_csv.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to Git repository (defaults to current directory)",
    )
    parser_csv.add_argument(
        "--output", default="repo_line_counts.csv", help="Output CSV file path"
    )
    parser_csv.set_defaults(func=cmd_generate_csv)

    # plot-evolution subcommand
    parser_evolution = subparsers.add_parser(
        "plot-evolution", help="Create stacked area chart of evolution"
    )
    parser_evolution.add_argument("csv", help="Path to CSV file with Git history")
    parser_evolution.set_defaults(func=cmd_plot_evolution)

    # plot-modules subcommand
    parser_modules = subparsers.add_parser(
        "plot-modules", help="Create bar chart of module breakdown"
    )
    parser_modules.add_argument("csv", help="Path to CSV file with Git history")
    parser_modules.set_defaults(func=cmd_plot_modules)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)
