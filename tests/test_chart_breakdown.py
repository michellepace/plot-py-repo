"""Tests for chart_breakdown module."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_breakdown import _prepare_data, create


@pytest.mark.filterwarnings("ignore::DeprecationWarning:plotly.io._kaleido")
@pytest.mark.slow
def test_create_generates_webp_file(tmp_path: Path) -> None:
    """create() writes WebP file to specified path."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00", "2024-01-02T10:00:00"],
            "commit_id": ["abc123", "def456"],
            "filedir": ["src", "tests"],
            "filename": ["module.py", "test_module.py"],
            "docstring_lines": [10, 5],
            "comment_lines": [5, 3],
            "executable_lines": [100, 50],
        }
    )
    output_path = tmp_path / "modules.webp"

    create(df, output_path)

    assert output_path.exists()


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
            "commit_id": ["abc123", "abc123", "def456", "def456"],
            "filedir": ["src", "tests", "src", "tests"],
            "filename": ["main.py", "test_main.py", "main.py", "test_main.py"],
            "docstring_lines": [10, 20, 15, 25],
            "comment_lines": [5, 10, 8, 12],
            "executable_lines": [100, 200, 150, 250],
        }
    )

    result = _prepare_data(df)

    # Should only have latest commit data: main.py total=173, test_main.py total=287
    assert len(result) == 2
    assert result.iloc[0]["filename"] == "test_main.py"
    assert result.iloc[0]["line_count"] == 287  # 25 + 12 + 250
    assert result.iloc[1]["filename"] == "main.py"
    assert result.iloc[1]["line_count"] == 173  # 15 + 8 + 150


def test_prepare_data_sums_across_categories_per_file() -> None:
    """Line counts summed across all line types for each file."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 2,
            "commit_id": ["abc123"] * 2,
            "filedir": ["src", "tests"],
            "filename": ["main.py", "test_main.py"],
            "docstring_lines": [15, 8],
            "comment_lines": [5, 2],
            "executable_lines": [100, 50],  # main.py total=120, test_main.py total=60
        }
    )

    result = _prepare_data(df)

    assert len(result) == 2
    assert result.iloc[0]["filename"] == "main.py"
    assert result.iloc[0]["line_count"] == 120  # 15 + 5 + 100
    assert result.iloc[1]["filename"] == "test_main.py"
    assert result.iloc[1]["line_count"] == 60  # 8 + 2 + 50


def test_prepare_data_sorts_by_line_count_descending() -> None:
    """Files sorted by line count descending (largest first for horizontal bar chart)."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 3,
            "commit_id": ["abc123"] * 3,
            "filedir": ["src", "src", "tests"],
            "filename": ["small.py", "large.py", "medium.py"],
            "docstring_lines": [5, 30, 15],
            "comment_lines": [3, 20, 10],
            "executable_lines": [50, 300, 150],
        }
    )

    result = _prepare_data(df)

    # Should be sorted: large.py (350), medium.py (175), small.py (58)
    assert len(result) == 3
    assert result.iloc[0]["filename"] == "large.py"
    assert result.iloc[0]["line_count"] == 350  # 30 + 20 + 300
    assert result.iloc[1]["filename"] == "medium.py"
    assert result.iloc[1]["line_count"] == 175  # 15 + 10 + 150
    assert result.iloc[2]["filename"] == "small.py"
    assert result.iloc[2]["line_count"] == 58  # 5 + 3 + 50
