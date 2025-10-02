"""Visualization generation for Python repository evolution."""

from pathlib import Path

import pandas as pd

from . import chart_evolution, chart_modules


def _load_and_exclude_files(csv_path: str, filenames: list[str]) -> pd.DataFrame:
    """Load CSV and exclude rows where filename is in filenames list."""
    df = pd.read_csv(csv_path)
    mask = ~df["filename"].isin(filenames)
    return df.loc[mask].copy()


def create_charts(csv_path: str, output_dir: str) -> None:
    """Create evolution and module visualisation WebP images from CSV history."""
    filtered_df = _load_and_exclude_files(csv_path, ["__init__.py"])

    # Generate both charts
    output_path = Path(output_dir)
    chart_evolution.create(filtered_df, output_path / "repo_evolution.webp")
    chart_modules.create(filtered_df, output_path / "repo_modules.webp")

    print(f"✅  Created {output_path / 'repo_evolution.webp'}")
    print(f"✅  Created {output_path / 'repo_modules.webp'}")
