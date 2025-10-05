"""Tests for chart_evolution module."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_evolution import _calculate_category_order, _prepare_data, create


@pytest.mark.filterwarnings("ignore::DeprecationWarning:plotly.io._kaleido")
@pytest.mark.slow
def test_create_generates_webp_file(tmp_path: Path) -> None:
    """create() writes WebP file to specified path."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00", "2024-01-02T10:00:00"],
            "commit_id": ["abc123", "def456"],
            "filedir": ["src", "src"],
            "filename": ["module.py", "module.py"],
            "docstring_lines": [10, 15],
            "comment_lines": [5, 8],
            "executable_lines": [100, 150],
        }
    )
    output_path = tmp_path / "evolution.webp"

    create(df, output_path)

    assert output_path.exists()


def test_calculate_category_order_returns_categories_sorted_by_total_lines() -> None:
    """Categories ordered by total line count descending (largest first)."""
    df_prepared = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
            "category": ["Source Code", "Test Code", "Source Code", "Test Code"],
            "line_count": [100, 300, 150, 400],  # Test Code total=700, Source=250
        }
    )

    result = _calculate_category_order(df_prepared)

    assert result == ["Test Code", "Source Code"]  # Largest first


def test_prepare_data_uses_latest_commit_when_multiple_commits_same_date() -> None:
    """With multiple commits on same date, use only the latest commit state."""
    df = pd.DataFrame(
        {
            "commit_date": [
                "2024-01-01T10:00:00",  # Earlier commit
                "2024-01-01T10:00:00",
                "2024-01-01T15:00:00",  # Later commit (should be used)
                "2024-01-01T15:00:00",
            ],
            "commit_id": ["abc123", "abc123", "def456", "def456"],
            "filedir": ["src", "tests", "src", "tests"],
            "filename": ["main.py", "test_main.py", "main.py", "test_main.py"],
            "docstring_lines": [10, 20, 15, 25],
            "comment_lines": [5, 10, 8, 12],
            "executable_lines": [100, 200, 150, 250],
        }
    )

    result = _prepare_data(df)

    # Should have latest commit only: Source Code=150, Test Code=250, Documentation=60
    assert len(result) == 3
    assert result[result["category"] == "Source Code"]["line_count"].item() == 150
    assert result[result["category"] == "Test Code"]["line_count"].item() == 250
    # Documentation from latest commit: (15+25) docstrings + (8+12) comments = 60
    assert result[result["category"] == "Documentation"]["line_count"].item() == 60


def test_prepare_data_retains_unmatched_rows_in_other_category() -> None:
    """Rows that don't match known categories should be aggregated under 'Other'."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 4,
            "commit_id": ["abc123"] * 4,
            "filedir": ["src", "tests", "docs", "lib"],
            "filename": ["main.py", "test_main.py", "guide.py", "util.py"],
            "docstring_lines": [10, 20, 5, 8],
            "comment_lines": [5, 10, 3, 4],
            "executable_lines": [100, 200, 50, 75],
        }
    )

    result = _prepare_data(df)

    # Should have 4 categories: Source Code, Test Code, Other, and Documentation
    categories = result["category"].tolist()
    assert "Source Code" in categories
    assert "Test Code" in categories
    assert "Other" in categories
    assert "Documentation" in categories
    assert len(result) == 4

    # Check line counts
    assert result[result["category"] == "Source Code"]["line_count"].item() == 100
    assert result[result["category"] == "Test Code"]["line_count"].item() == 200
    assert result[result["category"] == "Other"]["line_count"].item() == 125  # 50 + 75
    # Documentation: (10+20+5+8) docstrings + (5+10+3+4) comments = 65
    assert result[result["category"] == "Documentation"]["line_count"].item() == 65
