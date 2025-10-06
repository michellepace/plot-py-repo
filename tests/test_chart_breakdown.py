"""Tests for horizontal bar chart: data filtering, sorting, and image export."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_breakdown import _prepare_data, create


# Chapter 1: Data Contract
def test_prepare_data_requires_essential_columns() -> None:
    """_prepare_data() requires essential columns from CSV."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"],
            "filedir": ["src"],
            "filename": ["module.py"],
            "total_lines": [115],
        }
    )

    result = _prepare_data(df)

    assert "filedir" in result.columns
    assert "filename" in result.columns
    assert "total_lines" in result.columns


def test_prepare_data_fails_with_missing_required_columns() -> None:
    """_prepare_data() raises KeyError when essential columns are missing."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"],
            "filedir": ["src"],
            # Missing filename and total_lines
        }
    )

    with pytest.raises(KeyError):
        _prepare_data(df)


# Chapter 2: Data Transformation Pipeline
def test_prepare_data_filters_to_latest_commit_only() -> None:
    """With multiple commits, only the latest commit's data is used."""
    df = pd.DataFrame(
        {
            "commit_date": [
                "2024-01-01T10:00:00",  # Earlier commit
                "2024-01-01T10:00:00",
                "2024-01-02T15:00:00",  # Latest commit (should be used)
                "2024-01-02T15:00:00",
            ],
            "filedir": ["src", "tests", "src", "tests"],
            "filename": ["main.py", "test_main.py", "main.py", "test_main.py"],
            "total_lines": [115, 230, 173, 287],
        }
    )

    result = _prepare_data(df)

    assert len(result) == 2
    assert result.iloc[0]["filename"] == "test_main.py"
    assert result.iloc[0]["total_lines"] == 287
    assert result.iloc[1]["filename"] == "main.py"
    assert result.iloc[1]["total_lines"] == 173


def test_prepare_data_sorts_by_line_count_descending() -> None:
    """Files sorted by line count descending (largest first for horizontal bar chart)."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 3,
            "filedir": ["src", "src", "tests"],
            "filename": ["small.py", "large.py", "medium.py"],
            "total_lines": [58, 350, 175],
        }
    )

    result = _prepare_data(df)

    assert len(result) == 3
    assert result.iloc[0]["filename"] == "large.py"
    assert result.iloc[0]["total_lines"] == 350
    assert result.iloc[1]["filename"] == "medium.py"
    assert result.iloc[1]["total_lines"] == 175
    assert result.iloc[2]["filename"] == "small.py"
    assert result.iloc[2]["total_lines"] == 58


# Chapter 3: Integration (End-to-End)
@pytest.mark.filterwarnings("ignore::DeprecationWarning:plotly.io._kaleido")
@pytest.mark.slow
def test_create_generates_webp_file(tmp_path: Path) -> None:
    """create() writes WebP file to specified path."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00", "2024-01-02T10:00:00"],
            "filedir": ["src", "tests"],
            "filename": ["module.py", "test_module.py"],
            "total_lines": [115, 58],
        }
    )
    output_path = tmp_path / "modules.webp"

    create(df, output_path)

    assert output_path.exists()
