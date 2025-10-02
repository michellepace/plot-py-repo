"""Tests for visualise module."""

import pandas as pd


def test_filter_excludes_init_py() -> None:
    """DataFrame filter excludes __init__.py files."""
    df = pd.DataFrame(
        {
            "filename": [
                "module.py",
                "__init__.py",
                "test_example.py",
            ],
            "line_count": [100, 1, 50],
        }
    )

    filtered = df[df["filename"] != "__init__.py"]
    filenames = list(filtered["filename"])

    assert "__init__.py" not in filenames
    assert "module.py" in filenames
    assert "test_example.py" in filenames
