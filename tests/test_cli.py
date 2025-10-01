"""Simple CLI user flow tests for viz-python-repo."""

import subprocess
from pathlib import Path


def run_cli(*args: str) -> str:
    """Run viz-python-repo CLI and return combined output.

    Args:
        *args: Command-line arguments to pass to viz-python-repo

    Returns:
        Combined stdout + stderr output
    """
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "viz-python-repo", *args],  # noqa: S607
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    return result.stdout + result.stderr


def test_cli_help() -> None:
    """Test that CLI help command works."""
    output = run_cli("--help")
    assert "Visualize Python repository evolution" in output
    assert "count-lines" in output
    assert "generate-csv" in output
    assert "plot-evolution" in output
    assert "plot-modules" in output


def test_count_lines_missing_file() -> None:
    """Test count-lines with non-existent file shows error."""
    output = run_cli("count-lines", "nonexistent_file.py")
    assert "Error: File not found" in output


def test_count_lines_success(tmp_path: Path) -> None:
    """Test count-lines successfully counts a simple Python file."""
    # Create a simple Python file
    test_file = tmp_path / "test.py"
    test_file.write_text('"""Docstring."""\n\n# Comment\nprint("hello")\n')

    output = run_cli("count-lines", str(test_file))
    assert "Actual code lines:" in output
    assert "Docstring lines:" in output
    assert "Comment lines:" in output
    assert "line_count_code:" in output
    assert "line_count_docstrings_comments:" in output


def test_plot_evolution_stub() -> None:
    """Test plot-evolution shows not implemented message."""
    output = run_cli("plot-evolution", "dummy.csv")
    assert "Not yet implemented" in output
    assert "Stacked area chart" in output


def test_plot_modules_stub() -> None:
    """Test plot-modules shows not implemented message."""
    output = run_cli("plot-modules", "dummy.csv")
    assert "Not yet implemented" in output
    assert "Bar chart" in output
