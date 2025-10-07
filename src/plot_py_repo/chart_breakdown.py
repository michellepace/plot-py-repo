"""Breakdown chart generation for Python repository evolution."""

from pathlib import Path
from typing import cast

import pandas as pd
import plotly.express as px

from .theme import add_footnote_annotation, apply_common_layout, save_chart_image

CHART_TITLE = "Repository Breakdown by File"


def create(df: pd.DataFrame, output_path: Path) -> None:
    """Create horizontal bar chart showing repository breakdown by file.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    df_prepared = _prepare_data(df)
    latest_commit_date = cast("pd.Timestamp", df["commit_date"].max())
    repo_name = df["repo_name"].iloc[0]
    _plot_and_save(df_prepared, latest_commit_date, output_path, repo_name)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Extract latest commit data and return file-level line counts sorted descending."""
    latest_commit_date = df["commit_date"].max()
    return (
        df[df["commit_date"] == latest_commit_date]
        .loc[:, ["filedir", "filename", "total_lines"]]
        .sort_values("total_lines", ascending=False)
    )


def _plot_and_save(
    df_prepared: pd.DataFrame,
    latest_commit_date: pd.Timestamp,
    output_path: Path,
    repo_name: str,
) -> None:
    """Generate horizontal bar chart and write WebP image to output_path."""
    fig = px.bar(
        df_prepared,
        y="filename",
        x="total_lines",
        color="filedir",
        title=CHART_TITLE,
        labels={"filename": "", "total_lines": "Total Lines"},
        text="total_lines",
        orientation="h",
        category_orders={"filename": df_prepared["filename"].tolist()},
    )

    apply_common_layout(fig)
    add_footnote_annotation(
        fig, repository_name=repo_name, latest_commit_date=latest_commit_date
    )
    save_chart_image(fig, output_path)
