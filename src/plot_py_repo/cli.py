"""Command-line interface for plot-py-repo."""

import argparse

from .git_history import generate_csv
from .visualise import create_charts


def main() -> None:
    """Main entry point for plot-py-repo CLI."""
    parser = argparse.ArgumentParser(
        prog="plot-py-repo",
        description="""🦧 Visualise Python repository evolution through Git history.

Analyses Git commits to track code growth over time:
 • Classifies lines as code vs docstrings/comments
 • Generates CSV with line counts per file per commit
 • Creates two charts: evolution timeline and breakdown by file
 """,
        epilog="""examples:
  plot-py-repo                           # Visualise current repo
  plot-py-repo /path/to/repo             # Visualise different repo
  plot-py-repo --csv history.csv         # Regenerate charts from CSV
  plot-py-repo --output-dir ./reports    # Save outputs to ./reports""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to Git repository (default: current directory)",
    )
    parser.add_argument(
        "--csv",
        metavar="FILE",
        help="Skip Git analysis, create visualisations from existing CSV",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=".",
        help="Output directory for CSV and images (default: current directory)",
    )

    args = parser.parse_args()

    # Validate: repo_path and --csv are mutually exclusive
    if args.csv and args.repo_path != ".":
        parser.error("Cannot specify both repo_path and --csv")

    # Execute workflow
    if args.csv:
        # Development mode: just visualise existing CSV
        create_charts(args.csv, args.output_dir)
    else:
        # Normal mode: generate CSV + visualise
        csv_path = generate_csv(args.repo_path, args.output_dir)
        create_charts(csv_path, args.output_dir)
