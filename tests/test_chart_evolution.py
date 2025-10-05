"""Tests for chart_evolution module."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_evolution import _calculate_category_order, _prepare_data, create


# Chapter 1: Data Contract
def test_prepare_data_requires_essential_columns() -> None:
    """_prepare_data() requires essential columns from CSV."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"],
            "filedir": ["src"],
            "code_lines": [100],
            "documentation_lines": [15],
        }
    )

    result = _prepare_data(df)

    assert "date" in result.columns
    assert "category" in result.columns
    assert "line_count" in result.columns


def test_prepare_data_fails_with_missing_required_columns() -> None:
    """_prepare_data() raises KeyError when essential columns are missing."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"],
            # Missing filedir and code_lines
        }
    )

    with pytest.raises(KeyError):
        _prepare_data(df)


# Chapter 2: Data Transformation Pipeline
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
            "filedir": ["src", "tests", "src", "tests"],
            "code_lines": [100, 200, 150, 250],
            "documentation_lines": [15, 30, 23, 37],
        }
    )

    result = _prepare_data(df)

    assert len(result) == 3
    categories = result["category"].tolist()
    assert "Source Code" in categories
    assert "Test Code" in categories
    assert "Documentation" in categories


def test_prepare_data_categorises_files_by_directory() -> None:
    """Files categorized by directory: src→Source Code, tests→Test Code, other→Other."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 4,
            "filedir": ["src", "tests", "docs", "lib"],
            "code_lines": [100, 200, 50, 75],
            "documentation_lines": [15, 30, 8, 12],
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
            "filedir": ["src", "src"],
            "code_lines": [100, 50],
            "documentation_lines": [13, 7],
        }
    )

    result = _prepare_data(df)

    assert result[result["category"] == "Source Code"]["line_count"].item() == 150
    assert result[result["category"] == "Documentation"]["line_count"].item() == 20


# Chapter 3: Helper Functions
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


# Chapter 4: Integration (End-to-End)
@pytest.mark.filterwarnings("ignore::DeprecationWarning:plotly.io._kaleido")
@pytest.mark.slow
def test_create_generates_webp_file(tmp_path: Path) -> None:
    """create() writes WebP file to specified path."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00", "2024-01-02T10:00:00"],
            "filedir": ["src", "src"],
            "code_lines": [100, 150],
            "documentation_lines": [15, 23],
        }
    )
    output_path = tmp_path / "evolution.webp"

    create(df, output_path)

    assert output_path.exists()
