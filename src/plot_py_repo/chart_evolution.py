"""Evolution chart generation for Python repository evolution."""

from pathlib import Path
from typing import cast

import pandas as pd
import plotly.express as px

from .theme import apply_common_layout


def create(df: pd.DataFrame, output_path: Path) -> None:
    """Create stacked area chart showing codebase evolution over time.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    df_prepared = _prepare_data(df)
    _plot_and_save(df_prepared, output_path)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform granular commit data into aggregated chart categories by date.

    Extracts dates from commit_date column, filters to latest commit per date,
    transforms wide format to long format with display categories:
    - src + executable → "Source Code"
    - tests + executable → "Test Code"
    - documentation → "Documentation"

    Returns:
        DataFrame with columns: date, category, line_count (one row per date/category)
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["commit_date"])
    df["date"] = df["timestamp"].dt.date

    # Filter to latest commit per date
    latest_per_date = df.groupby("date")["timestamp"].max().reset_index()
    df = df.merge(latest_per_date, on=["date", "timestamp"], how="inner")

    # Calculate documentation_lines if not present
    if "documentation_lines" not in df.columns:
        df["documentation_lines"] = df["docstring_lines"] + df["comment_lines"]

    # Create long format by splitting into executable and documentation
    # Executable lines by filedir
    df_exec = df.loc[:, ["date", "filedir", "executable_lines"]].copy()
    df_exec["category"] = "Other"
    df_exec.loc[df["filedir"] == "src", "category"] = "Source Code"
    df_exec.loc[df["filedir"] == "tests", "category"] = "Test Code"
    df_exec["line_count"] = df_exec["executable_lines"]
    df_exec = df_exec.loc[:, ["date", "category", "line_count"]]

    # Documentation lines (all combined)
    df_docs = df.loc[:, ["date", "documentation_lines"]].copy()
    df_docs["category"] = "Documentation"
    df_docs["line_count"] = df_docs["documentation_lines"]
    df_docs = df_docs.loc[:, ["date", "category", "line_count"]]

    # Combine and group by date and category
    df_combined = pd.concat([df_exec, df_docs], ignore_index=True)
    result = df_combined.groupby(["date", "category"], as_index=False)["line_count"].sum()

    return cast("pd.DataFrame", result)


def _calculate_category_order(df_prepared: pd.DataFrame) -> list[str]:
    """Calculate category display order by total line count (descending).

    Returns:
        List of category names sorted by total lines, largest first
    """
    category_totals = df_prepared.groupby("category")["line_count"].sum()
    sorted_series = category_totals.sort_values(ascending=False)  # type: ignore[call-overload]
    return [str(cat) for cat in sorted_series.index.tolist()]


def _plot_and_save(df_prepared: pd.DataFrame, output_path: Path) -> None:
    """Generate stacked area chart and write WebP image to output_path."""
    category_order = _calculate_category_order(df_prepared)

    fig = px.area(
        df_prepared,
        x="date",
        y="line_count",
        color="category",
        title="Repository Growth Over Time",
        labels={"date": "", "line_count": "Total Lines"},
        category_orders={"category": category_order},
    )

    apply_common_layout(fig)
    fig.write_image(str(output_path), scale=2)
