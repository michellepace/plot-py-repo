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
            "code_lines": [100, 150],
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

    assert result == ["Test Code", "Source Code"]


def test_prepare_data_filters_to_latest_commit_per_date() -> None:
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
            "code_lines": [100, 200, 150, 250],
        }
    )

    result = _prepare_data(df)

    # Should only include rows from latest commit (def456), resulting in 3 categories
    assert len(result) == 3
    categories = result["category"].tolist()
    assert "Source Code" in categories
    assert "Test Code" in categories
    assert "Documentation" in categories


def test_prepare_data_categorizes_files_by_directory() -> None:
    """Files categorized by directory: src→Source Code, tests→Test Code, other→Other."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 4,
            "commit_id": ["abc123"] * 4,
            "filedir": ["src", "tests", "docs", "lib"],
            "filename": ["main.py", "test_main.py", "guide.py", "util.py"],
            "docstring_lines": [10, 20, 5, 8],
            "comment_lines": [5, 10, 3, 4],
            "code_lines": [100, 200, 50, 75],
        }
    )

    result = _prepare_data(df)

    categories = result["category"].tolist()
    assert "Source Code" in categories
    assert "Test Code" in categories
    assert "Other" in categories
    assert "Documentation" in categories
    assert len(result) == 4


def test_prepare_data_aggregates_lines_by_category() -> None:
    """Line counts correctly aggregated across files within each category."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 2,
            "commit_id": ["abc123"] * 2,
            "filedir": ["src", "src"],
            "filename": ["main.py", "utils.py"],
            "docstring_lines": [10, 5],
            "comment_lines": [3, 2],
            "code_lines": [100, 50],
        }
    )

    result = _prepare_data(df)

    # Source Code: 100 + 50 = 150
    assert result[result["category"] == "Source Code"]["line_count"].item() == 150
    # Documentation is aggregated (10+5) + (3+2) = 20
    assert result[result["category"] == "Documentation"]["line_count"].item() == 20
