"""Evolution chart generation for Python repository evolution."""

from pathlib import Path

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

    Extracts dates from timestamps, maps raw categories to display categories,
    then groups and sums line counts:
    - src + code → "Source Code"
    - tests + code → "Test Code"
    - docstrings_comments → "Docstrings/Comments"

    Returns:
        DataFrame with columns: date, category, line_count (one row per date/category)
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    # Map raw categories to display categories
    conditions = [
        (df["filedir"] == "src") & (df["category"] == "code"),
        (df["filedir"] == "tests") & (df["category"] == "code"),
        df["category"] == "docstrings_comments",
    ]
    choices = ["Source Code", "Test Code", "Docstrings/Comments"]
    df["display_category"] = pd.Series(dtype=str)

    for condition, choice in zip(conditions, choices, strict=True):
        df.loc[condition, "display_category"] = choice

    return (
        df.groupby(["date", "display_category"], as_index=False)["line_count"]
        .sum()
        .rename(columns={"display_category": "category"})  # type: ignore[call-overload]
    )


def _calculate_category_order(df_prepared: pd.DataFrame) -> list[str]:
    """Calculate category display order by total line count (descending).

    Returns:
        List of category names sorted by total lines, largest first
    """
    category_totals = df_prepared.groupby("category")["line_count"].sum()
    return category_totals.sort_values(ascending=False).index.tolist()


def _plot_and_save(df_prepared: pd.DataFrame, output_path: Path) -> None:
    """Generate stacked area chart and write WebP image to output_path."""
    category_order = _calculate_category_order(df_prepared)

    fig = px.area(
        df_prepared,
        x="date",
        y="line_count",
        color="category",
        title="Repository Growth Over Time",
        labels={"date": "Date", "line_count": "Lines of Code", "category": "Category"},
        category_orders={"category": category_order},
    )

    apply_common_layout(fig)

    fig.write_image(str(output_path), scale=2)
