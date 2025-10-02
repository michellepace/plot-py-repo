"""Visualization generation for Python repository evolution."""

from pathlib import Path

import pandas as pd
import plotly.express as px

from . import chart_evolution
from .theme import apply_common_layout


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
    chart_evolution.create(filtered_df, output_path / "repo_evolution.webp")
    _plot_modules(filtered_df, output_path / "repo_modules.webp")

    print(f"✅  Created {output_path / 'repo_evolution.webp'}")
    print(f"✅  Created {output_path / 'repo_modules.webp'}")


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

    # Sort by line count: largest at top for horizontal bar chart
    df_modules = df_modules.sort_values("line_count", ascending=False)

    # Create horizontal bar chart
    fig = px.bar(
        df_modules,
        y="filename",
        x="line_count",
        color="filedir",
        title="Module Breakdown (Latest Commit)",
        labels={"filename": "", "line_count": "Lines of Code", "filedir": "Type"},
        text="line_count",
        orientation="h",
        category_orders={"filename": df_modules["filename"].tolist()},
    )

    apply_common_layout(fig)

    fig.write_image(str(output_path), scale=2)
