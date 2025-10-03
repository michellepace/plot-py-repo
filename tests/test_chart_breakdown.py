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
            "category": ["code", "code"],
            "line_count": [100, 50],
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
            "category": ["code", "code", "code", "code"],
            "line_count": [100, 200, 150, 250],
        }
    )

    result = _prepare_data(df)

    # Should only have latest commit data: main.py=150, test_main.py=250
    assert len(result) == 2
    assert result.iloc[0]["filename"] == "test_main.py"
    assert result.iloc[0]["line_count"] == 250
    assert result.iloc[1]["filename"] == "main.py"
    assert result.iloc[1]["line_count"] == 150


def test_prepare_data_sums_across_categories_per_file() -> None:
    """Line counts summed across categories (code + docstrings_comments) for each file."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 4,
            "commit_id": ["abc123"] * 4,
            "filedir": ["src", "src", "tests", "tests"],
            "filename": ["main.py", "main.py", "test_main.py", "test_main.py"],
            "category": ["code", "docstrings_comments", "code", "docstrings_comments"],
            "line_count": [100, 20, 50, 10],  # main.py total=120, test_main.py total=60
        }
    )

    result = _prepare_data(df)

    assert len(result) == 2
    assert result.iloc[0]["filename"] == "main.py"
    assert result.iloc[0]["line_count"] == 120  # 100 + 20
    assert result.iloc[1]["filename"] == "test_main.py"
    assert result.iloc[1]["line_count"] == 60  # 50 + 10


def test_prepare_data_sorts_by_line_count_descending() -> None:
    """Files sorted by line count descending (largest first for horizontal bar chart)."""
    df = pd.DataFrame(
        {
            "commit_date": ["2024-01-01T10:00:00"] * 3,
            "commit_id": ["abc123"] * 3,
            "filedir": ["src", "src", "tests"],
            "filename": ["small.py", "large.py", "medium.py"],
            "category": ["code", "code", "code"],
            "line_count": [50, 300, 150],
        }
    )

    result = _prepare_data(df)

    # Should be sorted: large.py (300), medium.py (150), small.py (50)
    assert len(result) == 3
    assert result.iloc[0]["filename"] == "large.py"
    assert result.iloc[0]["line_count"] == 300
    assert result.iloc[1]["filename"] == "medium.py"
    assert result.iloc[1]["line_count"] == 150
    assert result.iloc[2]["filename"] == "small.py"
    assert result.iloc[2]["line_count"] == 50
