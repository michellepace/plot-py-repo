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
            "category": ["executable", "executable"],
            "line_count": [100, 150],
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
            "category": ["executable", "executable", "executable", "executable"],
            "line_count": [100, 200, 150, 250],  # Latest has 150 + 250 = 400 total
        }
    )

    result = _prepare_data(df)

    # Should have latest commit only: Source Code=150, Test Code=250
    assert len(result) == 2
    assert result[result["category"] == "Source Code"]["line_count"].item() == 150
    assert result[result["category"] == "Test Code"]["line_count"].item() == 250


def test_prepare_data_retains_unmatched_rows_in_other_category() -> None:
    """Rows that don't match known categories should be aggregated under 'Other'."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 4,
            "commit_id": ["abc123"] * 4,
            "filedir": ["src", "tests", "docs", "lib"],
            "filename": ["main.py", "test_main.py", "guide.py", "util.py"],
            "category": ["executable", "executable", "executable", "executable"],
            "line_count": [100, 200, 50, 75],
        }
    )

    result = _prepare_data(df)

    # Should have 3 categories: Source Code, Test Code, and Other
    categories = result["category"].tolist()
    assert "Source Code" in categories
    assert "Test Code" in categories
    assert "Other" in categories
    assert len(result) == 3

    # Check line counts
    assert result[result["category"] == "Source Code"]["line_count"].item() == 100
    assert result[result["category"] == "Test Code"]["line_count"].item() == 200
    assert result[result["category"] == "Other"]["line_count"].item() == 125  # 50 + 75
