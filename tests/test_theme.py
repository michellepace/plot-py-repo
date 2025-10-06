"""Tests for theme module."""

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from plot_py_repo.theme import _format_date, add_footnote_annotation, apply_common_layout


def test_apply_common_layout_applies_theme_to_figure() -> None:
    """apply_common_layout() applies theme settings to figure."""
    fig = go.Figure()
    result = apply_common_layout(fig)

    assert result.layout["width"] == 1600
    assert result.layout["height"] == 900
    assert result.layout["template"] == pio.templates["plotly_white"]
    assert result.layout["legend"]["orientation"] == "h"
    assert result is fig  # Confirms in-place modification


def test_format_date_converts_timestamp_to_human_readable() -> None:
    """_format_date() converts pandas Timestamp to human-readable format."""
    timestamp: pd.Timestamp = pd.Timestamp("2025-10-06 04:38:16 +0200")  # type: ignore[assignment]
    result = _format_date(timestamp)
    assert result == "6 Oct 2025"


def test_add_footer_adds_annotation_with_text() -> None:
    """add_footer() adds annotation with footer text."""
    fig = go.Figure()
    timestamp: pd.Timestamp = pd.Timestamp("2025-10-06 04:38:16 +0200")  # type: ignore[assignment]
    result = add_footnote_annotation(
        fig,
        repository_name="TestRepo",
        latest_commit_date=timestamp,
    )

    # Verify annotation contains expected text
    annotations = fig.layout.annotations  # type: ignore[attr-defined]
    footer_text = annotations[0].text
    assert "TestRepo" in footer_text
    assert "6 Oct 2025" in footer_text
    assert "All lines counted (as in IDE)" in footer_text

    assert result is fig
