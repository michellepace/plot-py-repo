"""Breakdown chart generation for Python repository evolution."""

from pathlib import Path

import pandas as pd
import plotly.express as px

from .theme import apply_common_layout


def create(df: pd.DataFrame, output_path: Path) -> None:
    """Create horizontal bar chart showing repository breakdown by file.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    df_prepared = _prepare_data(df)
    _plot_and_save(df_prepared, output_path)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform commit data into file-level line counts for latest commit.

    Returns DataFrame with columns: filedir, filename, line_count (sorted descending).
    """
    # Filter to latest commit only
    latest_commit_date = df["commit_date"].max()
    df_latest = df[df["commit_date"] == latest_commit_date].copy()

    # Calculate total lines for each file
    df_latest["line_count"] = (
        df_latest["docstring_lines"]
        + df_latest["comment_lines"]
        + df_latest["code_lines"]
    )

    # Select relevant columns
    df_files = df_latest.loc[:, ["filedir", "filename", "line_count"]].copy()

    # Sort by line count: largest at top for horizontal bar chart
    return df_files.sort_values("line_count", ascending=False)


def _plot_and_save(df_prepared: pd.DataFrame, output_path: Path) -> None:
    """Generate horizontal bar chart and write WebP image to output_path."""
    # Create horizontal bar chart
    fig = px.bar(
        df_prepared,
        y="filename",
        x="line_count",
        color="filedir",
        title="Repository Breakdown by File (current state)",
        labels={"filename": "", "line_count": "Total Lines"},
        text="line_count",
        orientation="h",
        category_orders={"filename": df_prepared["filename"].tolist()},
    )

    apply_common_layout(fig)
    fig.write_image(str(output_path), scale=2)
