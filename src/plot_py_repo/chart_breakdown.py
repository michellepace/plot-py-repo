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

    Returns DataFrame with columns: filedir, filename, total_lines (sorted descending).
    """
    latest_commit_date = df["commit_date"].max()
    return (
        df[df["commit_date"] == latest_commit_date]
        .loc[:, ["filedir", "filename", "total_lines"]]
        .sort_values("total_lines", ascending=False)
    )


def _plot_and_save(df_prepared: pd.DataFrame, output_path: Path) -> None:
    """Generate horizontal bar chart and write WebP image to output_path."""
    fig = px.bar(
        df_prepared,
        y="filename",
        x="total_lines",
        color="filedir",
        title="Repository Breakdown by File (current state)",
        labels={"filename": "", "total_lines": "Total Lines"},
        text="total_lines",
        orientation="h",
        category_orders={"filename": df_prepared["filename"].tolist()},
    )

    apply_common_layout(fig)
    fig.write_image(str(output_path), scale=2)
