"""Tests for visualise module."""

from pathlib import Path

import pandas as pd

from plot_py_repo.visualise import _load_and_exclude_files


def test_load_and_exclude_files_single_filename(tmp_path: Path) -> None:
    """_load_and_exclude_files() loads CSV and excludes specified filename."""
    # Create CSV file with test data including __init__.py
    csv_path = tmp_path / "test_history.csv"
    df = pd.DataFrame(
        {
            "timestamp": [
                "2024-01-01T10:00:00",
                "2024-01-01T10:00:00",
                "2024-01-01T10:00:00",
            ],
            "commit_id": ["abc123", "abc123", "abc123"],
            "filedir": ["src", "src", "tests"],
            "filename": ["module.py", "__init__.py", "test_example.py"],
            "category": ["code", "code", "code"],
            "line_count": [100, 1, 50],
        }
    )
    df.to_csv(csv_path, index=False)

    # Load and exclude __init__.py
    result = _load_and_exclude_files(str(csv_path), ["__init__.py"])

    # Verify __init__.py is filtered out
    filenames = list(result["filename"])
    assert "__init__.py" not in filenames
    assert "module.py" in filenames
    assert "test_example.py" in filenames


def test_load_and_exclude_files_multiple_filenames(tmp_path: Path) -> None:
    """_load_and_exclude_files() can exclude multiple filenames."""
    # Create CSV file with multiple files to exclude
    csv_path = tmp_path / "test_history.csv"
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01T10:00:00"] * 4,
            "commit_id": ["abc123"] * 4,
            "filedir": ["src"] * 4,
            "filename": ["module.py", "__init__.py", "horse.py", "main.py"],
            "category": ["code"] * 4,
            "line_count": [100, 1, 50, 75],
        }
    )
    df.to_csv(csv_path, index=False)

    # Load and exclude multiple files
    result = _load_and_exclude_files(str(csv_path), ["__init__.py", "horse.py"])

    # Verify both files are filtered out
    filenames = list(result["filename"])
    assert "__init__.py" not in filenames
    assert "horse.py" not in filenames
    assert "module.py" in filenames
    assert "main.py" in filenames
