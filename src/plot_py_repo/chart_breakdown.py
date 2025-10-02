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
    """Transform commit data into file-level line counts for latest commit."""
    # Filter to latest commit only
    latest_timestamp = df["timestamp"].max()
    df_latest = df[df["timestamp"] == latest_timestamp].copy()

    # Group by filedir and filename, sum across categories
    df_modules = (
        df_latest.groupby(["filedir", "filename"])["line_count"].sum().reset_index()
    )

    # Sort by line count: largest at top for horizontal bar chart
    return df_modules.sort_values("line_count", ascending=False)


def _plot_and_save(df_prepared: pd.DataFrame, output_path: Path) -> None:
    """Generate horizontal bar chart and write WebP image to output_path."""
    # Create horizontal bar chart
    fig = px.bar(
        df_prepared,
        y="filename",
        x="line_count",
        color="filedir",
        title="Repository Breakdown by File (current state)",
        labels={"filename": "", "line_count": "Lines of Code", "filedir": "Type"},
        text="line_count",
        orientation="h",
        category_orders={"filename": df_prepared["filename"].tolist()},
    )

    apply_common_layout(fig)

    fig.write_image(str(output_path), scale=2)
