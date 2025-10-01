"""Visualization generation for Python repository evolution."""

from pathlib import Path

import pandas as pd
import plotly.express as px


def create_images(csv_path: str, output_dir: str) -> None:
    """Create both evolution and module visualisation images from CSV.

    Args:
        csv_path: Path to CSV file with Git commit history
        output_dir: Directory where WebP images should be saved
    """
    # Read CSV once
    df = pd.read_csv(csv_path)

    # Filter out __init__.py files
    filtered_df = df[df["filename"] != "__init__.py"].copy()
    if not isinstance(filtered_df, pd.DataFrame):
        msg = "Expected DataFrame after filtering"
        raise TypeError(msg)

    # Generate both charts
    output_path = Path(output_dir)
    _plot_evolution(filtered_df, output_path / "repo_evolution.webp")
    _plot_modules(filtered_df, output_path / "repo_modules.webp")

    print(f"✅  Created {output_path / 'repo_evolution.webp'}")
    print(f"✅  Created {output_path / 'repo_modules.webp'}")


def _plot_evolution(df: pd.DataFrame, output_path: Path) -> None:
    """Create stacked area chart showing codebase evolution over time.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    # Extract date from timestamp
    df_evolution = df.copy()
    df_evolution["date"] = pd.to_datetime(df_evolution["timestamp"]).dt.date

    # For multiple commits per day, keep only the last one
    df_evolution = (
        df_evolution.sort_values("timestamp")
        .groupby(["date", "commit_id", "filedir", "filename", "category"])
        .last()
        .reset_index()
    )

    # Create category groups for stacking
    # We need: src_code, tests_code, docstrings_comments
    aggregated = []

    for date in df_evolution["date"].unique():
        date_data = df_evolution[df_evolution["date"] == date]

        # Source code lines
        src_code = date_data[
            (date_data["filedir"] == "src") & (date_data["category"] == "code")
        ]["line_count"].sum()

        # Test code lines
        tests_code = date_data[
            (date_data["filedir"] == "tests") & (date_data["category"] == "code")
        ]["line_count"].sum()

        # All docstrings/comments
        doc_comments = date_data[date_data["category"] == "docstrings_comments"][
            "line_count"
        ].sum()

        aggregated.extend(
            [
                {"date": date, "category": "Source Code", "line_count": src_code},
                {"date": date, "category": "Test Code", "line_count": tests_code},
                {
                    "date": date,
                    "category": "Docstrings/Comments",
                    "line_count": doc_comments,
                },
            ]
        )

    df_plot = pd.DataFrame(aggregated)

    # Create stacked area chart
    fig = px.area(
        df_plot,
        x="date",
        y="line_count",
        color="category",
        title="Python Repository Evolution Over Time",
        labels={"date": "Date", "line_count": "Lines of Code", "category": "Category"},
        color_discrete_map={
            "Source Code": "#41668c",
            "Test Code": "#4a366f",
            "Docstrings/Comments": "#8b8b8b",
        },
        category_orders={"category": ["Source Code", "Test Code", "Docstrings/Comments"]},
    )

    fig.update_layout(
        template="plotly_white",
        width=1600,
        height=900,
        font={"size": 14},
        hovermode="x unified",
    )

    fig.write_image(str(output_path), scale=2)


def _plot_modules(df: pd.DataFrame, output_path: Path) -> None:
    """Create horizontal bar chart showing line counts per module.

    Args:
        df: DataFrame with commit history data
        output_path: Path where WebP image should be saved
    """
    # Filter to latest commit only
    latest_timestamp = df["timestamp"].max()
    df_latest = df[df["timestamp"] == latest_timestamp].copy()

    # Group by filedir and filename, sum across categories
    df_modules = (
        df_latest.groupby(["filedir", "filename"])["line_count"].sum().reset_index()
    )

    # Create full path display
    df_modules["module"] = df_modules["filedir"] + "/" + df_modules["filename"]

    # Sort by line count descending
    df_modules = df_modules.sort_values("line_count", ascending=True)

    # Create horizontal bar chart
    fig = px.bar(
        df_modules,
        y="module",
        x="line_count",
        color="filedir",
        title="Module Breakdown (Latest Commit)",
        labels={"module": "Module", "line_count": "Lines of Code", "filedir": "Type"},
        color_discrete_map={"src": "#41668c", "tests": "#4a366f"},
        text="line_count",
        orientation="h",
    )

    fig.update_layout(
        template="plotly_white",
        width=1600,
        height=900,
        font={"size": 14},
        showlegend=True,
    )

    fig.update_traces(textposition="outside")

    fig.write_image(str(output_path), scale=2)
