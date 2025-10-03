"""Tests for chart_breakdown module."""

from pathlib import Path

import pandas as pd
import pytest

from plot_py_repo.chart_breakdown import create


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
