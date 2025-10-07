"""Visualization generation for Python repository evolution."""

import sys
from pathlib import Path

import pandas as pd

from . import chart_breakdown, chart_evolution, chart_evolution_commit


def _load_csv(csv_path: str) -> pd.DataFrame:
    """Load CSV history file containing Git commit metrics."""
    try:
        df = pd.read_csv(
            csv_path,
            dtype={
                "repo_name": str,
                "commit_id": str,
                "filedir": str,
                "filename": str,
                "code_lines": int,
                "docstring_lines": int,
                "comment_lines": int,
                "total_lines": int,
                "documentation_lines": int,
            },
        )
    except FileNotFoundError:
        print(f"❌  CSV file not found: {csv_path}")
        sys.exit(1)
    else:
        # Parse datetime with timezone preservation
        df["commit_date"] = pd.to_datetime(df["commit_date"])
        return df


def _exclude_filenames(df: pd.DataFrame, filenames: list[str]) -> pd.DataFrame:
    """Remove rows where filename matches any in the exclusion list."""
    mask = ~df["filename"].isin(filenames)
    return df.loc[mask].copy()


def create_charts(csv_path: str, output_dir: str) -> None:
    """Create evolution and breakdown visualisation WebP images from CSV history."""
    df = _load_csv(csv_path)
    filtered_df = _exclude_filenames(df, ["__init__.py"])

    output_path = Path(output_dir)
    chart_evolution.create(filtered_df, output_path / "repo_evolution.webp")
    chart_evolution_commit.create(filtered_df, output_path / "repo_evolution_commit.webp")
    chart_breakdown.create(filtered_df, output_path / "repo_breakdown.webp")

    print(f"✅  Created {output_path / 'repo_evolution.webp'}")
    print(f"✅  Created {output_path / 'repo_evolution_commit.webp'}")
    print(f"✅  Created {output_path / 'repo_breakdown.webp'}")
