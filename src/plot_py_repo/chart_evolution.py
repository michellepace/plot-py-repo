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
    uses melt() to transform wide format to long format with display categories:
    - code_lines + src → "Source Code"
    - code_lines + tests → "Test Code"
    - code_lines + other → "Other"
    - documentation_lines → "Documentation"

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

    # Transform wide format to long format using melt
    df_long = df.melt(
        id_vars=["date", "filedir"],
        value_vars=["code_lines", "documentation_lines"],
        var_name="line_type",
        value_name="line_count",
    )

    # Map line type and directory to display categories
    df_long["category"] = df_long.apply(_categorize_row, axis=1)

    # Aggregate by date and category
    result = df_long.groupby(["date", "category"], as_index=False)["line_count"].sum()

    return cast("pd.DataFrame", result)


def _categorize_row(row: pd.Series) -> str:
    """Map line type and directory to display category.

    Args:
        row: DataFrame row with 'line_type' and 'filedir' columns

    Returns:
        Display category: 'Documentation', 'Source Code', 'Test Code', or 'Other'
    """
    if row["line_type"] == "documentation_lines":
        return "Documentation"
    # Code lines categorized by directory
    if row["filedir"] == "src":
        return "Source Code"
    if row["filedir"] == "tests":
        return "Test Code"
    return "Other"


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
