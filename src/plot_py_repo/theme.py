"""Centralised theming for Plotly visualisations."""

from pathlib import Path

import pandas as pd
from plotly.graph_objects import Figure

# Standard layout settings applied to all charts
DEFAULT_LAYOUT = {
    "template": "plotly_dark",  # plotly_white, simple_white
    "width": 700,
    "height": 500,
    # Explicit margins for precise positioning
    "margin": {
        "l": 80,  # Left margin
        "r": 40,  # Right margin
        "t": 100,  # Top margin
        "b": 80,  # Bottom margin (space for footer)
    },
    # Legend positioned horizontally at top right, above chart area
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1.0,
        "title_text": "",
    },
}


def _format_date(commit_datetime: pd.Timestamp) -> str:
    """Format pandas Timestamp to human-readable date (e.g., '6 Oct 2025')."""
    return commit_datetime.strftime("%d %b %Y").lstrip("0")


def apply_common_layout(fig: Figure) -> Figure:
    """Apply standard layout settings to a Plotly figure.

    Modifies the figure in-place and returns it (following Plotly's API pattern).

    Args:
        fig: Plotly figure to apply theme settings to

    Returns:
        The same figure with layout settings applied (for method chaining)
    """
    return fig.update_layout(**DEFAULT_LAYOUT)


def add_footnote_annotation(
    fig: Figure, repository_name: str, latest_commit_date: pd.Timestamp
) -> Figure:
    """Add footer annotation with repository context below chart area.

    Positioning uses paper coordinates relative to plot area:
    - (0, 0) = bottom-left corner of plot area
    - (1, 1) = top-right corner of plot area
    - x=-0.05: 5% left of plot area's left edge (aligns with y-axis)
    - y=-0.17: 17% below plot area's bottom edge (in bottom margin)

    Args:
        fig: Plotly figure to add footer to
        repository_name: Name of repository being visualised
        latest_commit_date: Date of most recent commit in the chart

    Returns:
        The same figure with footer annotation added (for method chaining)
    """
    formatted_date = _format_date(latest_commit_date)
    footer_text = f"{repository_name}, {formatted_date} • All lines counted (as in IDE)"

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=-0.05,
        y=-0.17,
        text=footer_text,
        showarrow=False,
        font={"size": 11, "color": "#778899"},
        xanchor="left",
        yanchor="top",
    )

    return fig


def save_chart_image(fig: Figure, output_path: Path) -> None:
    """Save chart to WebP with standard scale factor for optimal text sizing.

    Uses scale=2 to render at base dimensions (700x500) then scale up to 1400x1000.
    This produces larger text and markers relative to canvas size for better readability.

    Args:
        fig: Plotly figure to save
        output_path: Path where WebP image should be saved
    """
    fig.write_image(output_path, scale=2)
