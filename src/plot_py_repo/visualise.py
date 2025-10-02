"""Visualization generation for Python repository evolution."""

from pathlib import Path

import pandas as pd

from . import chart_evolution, chart_modules


def create_images(csv_path: str, output_dir: str) -> None:
    """Create both evolution and module visualisation images from CSV.

    Args:
        csv_path: Path to CSV file with Git commit history
        output_dir: Directory where WebP images should be saved
    """
    # Read CSV once
    df = pd.read_csv(csv_path)

    # Filter out __init__.py files
    filtered_df = df[df["filename"] != "__init__.py"].copy()
    if not isinstance(filtered_df, pd.DataFrame):
        msg = "Expected DataFrame after filtering"
        raise TypeError(msg)

    # Generate both charts
    output_path = Path(output_dir)
    chart_evolution.create(filtered_df, output_path / "repo_evolution.webp")
    chart_modules.create(filtered_df, output_path / "repo_modules.webp")

    print(f"✅  Created {output_path / 'repo_evolution.webp'}")
    print(f"✅  Created {output_path / 'repo_modules.webp'}")
