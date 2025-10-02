"""Tests for theme module."""

import plotly.graph_objects as go

from plot_py_repo.theme import apply_common_layout


def test_apply_common_layout_applies_theme_to_figure() -> None:
    """apply_common_layout() applies theme settings to figure."""
    fig = go.Figure()
    result = apply_common_layout(fig)

    assert result.layout["width"] == 1600
    assert result.layout["height"] == 900
    assert result.layout["template"] is not None
    assert result is fig  # Confirms in-place modification
