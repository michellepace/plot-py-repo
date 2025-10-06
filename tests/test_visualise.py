"""Tests for visualise module."""

from pathlib import Path

import pandas as pd

from plot_py_repo.visualise import _exclude_filenames, _load_csv


def test_load_csv_loads_dataframe(tmp_path: Path) -> None:
    """Loads CSV file and returns DataFrame."""
    csv_path = tmp_path / "test_history.csv"
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df.to_csv(csv_path, index=False)

    result = _load_csv(str(csv_path))

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2


def test_exclude_filenames_single() -> None:
    """Removes rows matching single filename."""
    df = pd.DataFrame({"filename": ["module.py", "__init__.py", "test_example.py"]})

    result = _exclude_filenames(df, ["__init__.py"])

    filenames = list(result["filename"])
    assert "__init__.py" not in filenames
    assert "module.py" in filenames
    assert "test_example.py" in filenames
    assert len(result) == 2


def test_exclude_filenames_multiple() -> None:
    """Removes rows matching multiple filenames."""
    df = pd.DataFrame({"filename": ["module.py", "__init__.py", "horse.py", "main.py"]})

    result = _exclude_filenames(df, ["__init__.py", "horse.py"])

    filenames = list(result["filename"])
    assert "__init__.py" not in filenames
    assert "horse.py" not in filenames
    assert "module.py" in filenames
    assert "main.py" in filenames
    assert len(result) == 2


def test_exclude_filenames_empty_list_returns_all_rows() -> None:
    """Empty exclusion list returns all rows unchanged."""
    df = pd.DataFrame({"filename": ["module.py", "__init__.py"]})

    result = _exclude_filenames(df, [])

    assert len(result) == len(df)
    assert list(result["filename"]) == ["module.py", "__init__.py"]


def test_exclude_filenames_nonexistent_filename_returns_all_rows() -> None:
    """Non-existent filename in exclusion list returns all rows."""
    df = pd.DataFrame({"filename": ["module.py", "main.py"]})

    result = _exclude_filenames(df, ["nonexistent.py"])

    assert len(result) == len(df)
    assert list(result["filename"]) == ["module.py", "main.py"]
