"""Stacked bar chart visualising repository growth by commit index."""

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import plotly.express as px

from .theme import add_footnote_annotation, apply_common_layout, save_chart_image

CHART_TITLE = "Repository Growth by Commit"

CATEGORY_CODE_COMMENTS = "Code Comments"
CATEGORY_SOURCE_CODE = "Source Code"
CATEGORY_TEST_CODE = "Test Code"


def create(df: pd.DataFrame, output_path: Path) -> None:
    """Create stacked bar chart showing codebase evolution by commit index.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    df_prepared = _prepare_data(df)
    latest_commit_date = cast("pd.Timestamp", df["commit_date"].max())
    repo_name = df["repo_name"].iloc[0]
    _plot_and_save(df_prepared, latest_commit_date, output_path, repo_name)


def _prepare_data(df_per_file: pd.DataFrame) -> pd.DataFrame:
    """Transform per-file commit data into aggregated chart categories by commit index.

    Input: One row per file per commit (includes filedir column).

    Process:
    1. Create commit_index by ranking unique commits chronologically (oldest = 1)
       Uses commit_id to ensure each unique commit gets its own index,
       preventing duplicate timestamps from being aggregated together
    2. Melt wide format (code_lines, documentation_lines) to long format
    3. Categorise by line_type and filedir:
       - documentation_lines → "Code Comments"
       - code_lines + src → "Source Code"
       - code_lines + tests → "Test Code"
       - code_lines + other → "UNCATEGORISED_DIR"
    4. Sum lines across all files within each commit_index/category combination

    Returns:
        DataFrame with columns: commit_index, category, line_count
        (one row per commit_index/category)
    """
    df = df_per_file.copy()

    # Create commit index: rank commits chronologically (oldest = 1)
    # Use commit_id to ensure each unique commit gets its own index
    commit_info = df[["commit_date", "commit_id"]].drop_duplicates()
    commit_info = commit_info.sort_values(["commit_date", "commit_id"])  # type: ignore[call-overload]
    commit_info["commit_index"] = range(1, len(commit_info) + 1)
    df = df.merge(commit_info, on=["commit_date", "commit_id"], how="left")

    # Transform wide format to long format
    df_long = df.melt(
        id_vars=["commit_index", "filedir"],
        value_vars=["code_lines", "documentation_lines"],
        var_name="line_type",
        value_name="line_count",
    )

    # Map line_type and filedir to display categories
    conditions = [
        df_long["line_type"] == "documentation_lines",
        (df_long["line_type"] == "code_lines") & (df_long["filedir"] == "src"),
        (df_long["line_type"] == "code_lines") & (df_long["filedir"] == "tests"),
    ]
    choices = [CATEGORY_CODE_COMMENTS, CATEGORY_SOURCE_CODE, CATEGORY_TEST_CODE]
    df_long["category"] = np.select(conditions, choices, default="UNCATEGORISED_DIR")

    # Aggregate by commit_index and category
    result = df_long.groupby(["commit_index", "category"], as_index=False)[
        "line_count"
    ].sum()

    return cast("pd.DataFrame", result)


def _calculate_category_order(df_prepared: pd.DataFrame) -> list[str]:
    """Calculate category display order by total line count (descending).

    Returns:
        List of category names sorted by total lines, largest first
    """
    category_totals = df_prepared.groupby("category")["line_count"].sum()
    sorted_series = category_totals.sort_values(ascending=False)  # type: ignore[call-overload]
    return [str(cat) for cat in sorted_series.index.tolist()]


def _plot_and_save(
    df_prepared: pd.DataFrame,
    latest_commit_date: pd.Timestamp,
    output_path: Path,
    repo_name: str,
) -> None:
    """Generate stacked bar chart and write WebP image to output_path."""
    category_order = _calculate_category_order(df_prepared)

    fig = px.bar(
        df_prepared,
        x="commit_index",
        y="line_count",
        color="category",
        title=CHART_TITLE,
        labels={"commit_index": "Commit", "line_count": "Total Lines"},
        category_orders={"category": category_order},
        barmode="stack",
    )

    apply_common_layout(fig)
    add_footnote_annotation(
        fig, repository_name=repo_name, latest_commit_date=latest_commit_date
    )
    save_chart_image(fig, output_path)
