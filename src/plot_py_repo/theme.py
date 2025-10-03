"""Centralised theming for Plotly visualisations."""

from plotly.graph_objects import Figure

# Standard layout settings applied to all charts
DEFAULT_LAYOUT = {
    "template": "plotly_white",
    "width": 1600,
    "height": 900,
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


def apply_common_layout(fig: Figure) -> Figure:
    """Apply standard layout settings to a Plotly figure.

    Modifies the figure in-place and returns it (following Plotly's API pattern).

    Args:
        fig: Plotly figure to apply theme settings to

    Returns:
        The same figure with layout settings applied (for method chaining)
    """
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig
