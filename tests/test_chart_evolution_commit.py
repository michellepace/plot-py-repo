"""Tests for commit-indexed stacked bar chart: data transformation and image export."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_evolution_commit import (
    CATEGORY_CODE_COMMENTS,
    CATEGORY_SOURCE_CODE,
    CATEGORY_TEST_CODE,
    _calculate_category_order,
    _prepare_data,
    create,
)


# Chapter 1: Data Contract
def test_prepare_data_requires_essential_columns() -> None:
    """_prepare_data() requires essential columns from CSV."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"],
            "commit_date": pd.to_datetime(["2024-01-01T10:00:00"]),
            "commit_id": ["abc123"],
            "filedir": ["src"],
            "code_lines": [100],
            "documentation_lines": [15],
        }
    )

    result = _prepare_data(df)

    assert "commit_index" in result.columns
    assert "category" in result.columns
    assert "line_count" in result.columns


def test_prepare_data_fails_with_missing_required_columns() -> None:
    """_prepare_data() raises KeyError when essential columns are missing."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"],
            "commit_date": pd.to_datetime(["2024-01-01T10:00:00"]),
            # Missing filedir and code_lines
        }
    )

    with pytest.raises(KeyError):
        _prepare_data(df)


# Chapter 2: Data Transformation Pipeline
def test_prepare_data_creates_commit_index_chronologically() -> None:
    """Oldest commit gets index 1, newest gets highest index."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"] * 3,
            "commit_date": pd.to_datetime(
                [
                    "2024-01-03T10:00:00",  # Newest (should be index 3)
                    "2024-01-01T10:00:00",  # Oldest (should be index 1)
                    "2024-01-02T10:00:00",  # Middle (should be index 2)
                ]
            ),
            "commit_id": ["ccc333", "aaa111", "bbb222"],
            "filedir": ["src", "src", "src"],
            "code_lines": [300, 100, 200],
            "documentation_lines": [30, 10, 20],
        }
    )

    result = _prepare_data(df)

    # Check that commit_index values are 1, 2, 3
    commit_indices = sorted(result["commit_index"].unique())
    assert commit_indices == [1, 2, 3]

    # Verify oldest commit (2024-01-01) got index 1
    commit_1_data = result[result["commit_index"] == 1]
    commit_1_source = commit_1_data[commit_1_data["category"] == CATEGORY_SOURCE_CODE]
    assert commit_1_source["line_count"].item() == 100


def test_prepare_data_includes_all_commits() -> None:
    """All commits included in result (no filtering like date-based chart)."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"] * 6,
            "commit_date": pd.to_datetime(
                [
                    "2024-01-01T10:00:00",
                    "2024-01-01T10:00:00",
                    "2024-01-02T10:00:00",
                    "2024-01-02T10:00:00",
                    "2024-01-03T10:00:00",
                    "2024-01-03T10:00:00",
                ]
            ),
            "commit_id": ["aaa111", "aaa111", "bbb222", "bbb222", "ccc333", "ccc333"],
            "filedir": ["src", "tests"] * 3,
            "code_lines": [100, 200, 150, 250, 180, 300],
            "documentation_lines": [15, 30, 23, 37, 27, 45],
        }
    )

    result = _prepare_data(df)

    # Should have 3 unique commit indices
    unique_commits = result["commit_index"].nunique()
    assert unique_commits == 3


def test_prepare_data_categorises_files_by_directory() -> None:
    """Files categorised by directory: src→Source Code, tests→Test Code."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo", "test-repo"],
            "commit_date": pd.to_datetime(["2024-01-01T10:00:00"] * 2),
            "commit_id": ["abc123", "abc123"],
            "filedir": ["src", "tests"],
            "code_lines": [100, 200],
            "documentation_lines": [15, 30],
        }
    )

    result = _prepare_data(df)

    categories = result["category"].tolist()
    assert CATEGORY_SOURCE_CODE in categories
    assert CATEGORY_TEST_CODE in categories
    assert CATEGORY_CODE_COMMENTS in categories


def test_prepare_data_uses_fail_loud_for_uncategorised_directories() -> None:
    """Non-src/non-tests directories produce UNCATEGORISED_DIR (fail-loud).

    Note: Currently impossible in production as git_history only scans src/ and tests/.
    This test documents defensive behaviour if filters change.
    """
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo", "test-repo"],
            "commit_date": pd.to_datetime(["2024-01-01T10:00:00"] * 2),
            "commit_id": ["abc123", "abc123"],
            "filedir": ["docs", "scripts"],
            "code_lines": [50, 75],
            "documentation_lines": [8, 12],
        }
    )

    result = _prepare_data(df)

    # All code_lines entries should be categorised as UNCATEGORISED_DIR
    uncategorised_rows = result[result["category"] == "UNCATEGORISED_DIR"]
    assert len(uncategorised_rows) == 1
    assert uncategorised_rows["line_count"].item() == 125  # 50 + 75

    # Documentation lines still get categorised as Code Comments
    comment_rows = result[result["category"] == CATEGORY_CODE_COMMENTS]
    assert len(comment_rows) == 1
    assert comment_rows["line_count"].item() == 20  # 8 + 12


def test_prepare_data_aggregates_lines_by_commit_and_category() -> None:
    """Line counts correctly aggregated across files within each commit/category."""
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"] * 4,
            "commit_date": pd.to_datetime(
                [
                    "2024-01-01T10:00:00",
                    "2024-01-01T10:00:00",
                    "2024-01-02T10:00:00",
                    "2024-01-02T10:00:00",
                ]
            ),
            "commit_id": ["abc123", "abc123", "def456", "def456"],
            "filedir": ["src", "src", "src", "src"],
            "code_lines": [100, 50, 80, 70],
            "documentation_lines": [13, 7, 11, 9],
        }
    )

    result = _prepare_data(df)

    # Commit 1 (2024-01-01): 100 + 50 = 150 source, 13 + 7 = 20 comments
    commit_1 = result[result["commit_index"] == 1]
    commit_1_source = commit_1[commit_1["category"] == CATEGORY_SOURCE_CODE]
    commit_1_comments = commit_1[commit_1["category"] == CATEGORY_CODE_COMMENTS]
    assert commit_1_source["line_count"].item() == 150
    assert commit_1_comments["line_count"].item() == 20

    # Commit 2 (2024-01-02): 80 + 70 = 150 source, 11 + 9 = 20 comments
    commit_2 = result[result["commit_index"] == 2]
    commit_2_source = commit_2[commit_2["category"] == CATEGORY_SOURCE_CODE]
    commit_2_comments = commit_2[commit_2["category"] == CATEGORY_CODE_COMMENTS]
    assert commit_2_source["line_count"].item() == 150
    assert commit_2_comments["line_count"].item() == 20


def test_prepare_data_handles_duplicate_timestamps_correctly() -> None:
    """Commits with identical timestamps get separate indices (no aggregation spike).

    Regression test for: Two commits with same timestamp were assigned same index,
    causing line counts to be summed incorrectly (e.g., 887 + 887 = 1774).
    """
    df = pd.DataFrame(
        {
            "repo_name": ["test-repo"] * 4,
            "commit_date": pd.to_datetime(
                [
                    # Two different commits with IDENTICAL timestamp
                    "2024-01-01T15:24:57+00:00",
                    "2024-01-01T15:24:57+00:00",
                    "2024-01-01T15:24:57+00:00",
                    "2024-01-01T15:24:57+00:00",
                ]
            ),
            "commit_id": [
                "77522e7",
                "77522e7",
                "9b6f283",
                "9b6f283",
            ],  # Two unique commits
            "filedir": ["tests", "tests", "tests", "tests"],
            "code_lines": [450, 437, 450, 437],  # Each commit has 887 total test lines
            "documentation_lines": [10, 5, 10, 5],
        }
    )

    result = _prepare_data(df)

    # Should have 2 unique commit indices (not 1!)
    unique_commits = result["commit_index"].nunique()
    assert unique_commits == 2

    # Each commit should have 887 test lines (NOT 1774 from summing)
    for idx in [1, 2]:
        commit_data = result[result["commit_index"] == idx]
        test_code = commit_data[commit_data["category"] == CATEGORY_TEST_CODE]
        assert test_code["line_count"].item() == 887  # Not 1774!


# Chapter 3: Helper Functions
def test_calculate_category_order_returns_categories_sorted_by_total_lines() -> None:
    """Categories ordered by total line count descending (largest first)."""
    df_prepared = pd.DataFrame(
        {
            "commit_index": [1, 1, 2, 2],
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
            "repo_name": ["test-repo"] * 4,
            "commit_date": pd.to_datetime(
                [
                    "2024-01-01T10:00:00",
                    "2024-01-01T10:00:00",
                    "2024-01-02T10:00:00",
                    "2024-01-02T10:00:00",
                ]
            ),
            "commit_id": ["abc123", "abc123", "def456", "def456"],
            "filedir": ["src", "tests", "src", "tests"],
            "code_lines": [100, 50, 150, 75],
            "documentation_lines": [15, 8, 23, 12],
        }
    )
    output_path = tmp_path / "evolution_commit.webp"

    create(df, output_path)

    assert output_path.exists()
