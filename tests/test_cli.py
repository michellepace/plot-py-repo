"""Simple CLI user flow tests for plot-py-repo."""

import subprocess
from pathlib import Path

import pytest


def run_cli(*args: str) -> tuple[str, int]:
    """Run plot-py-repo CLI and return output and exit code.

    Args:
        *args: Command-line arguments to pass to plot-py-repo

    Returns:
        Tuple of (combined stdout + stderr output, exit code)
    """
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "plot-py-repo", *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return result.stdout + result.stderr, result.returncode


def _run_git(cmd: list[str], cwd: Path) -> None:
    """Run git command silently in specified directory."""
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)  # noqa: S603


def create_test_git_repo(repo_dir: Path) -> None:
    """Create a minimal Git repository for testing.

    Args:
        repo_dir: Directory where Git repo should be created
    """
    repo_dir.mkdir(exist_ok=True)
    (repo_dir / "src").mkdir(exist_ok=True)
    test_file = repo_dir / "src" / "example.py"
    test_file.write_text('"""Module docstring."""\n\nprint("hello")\n')

    # Initialize Git and make a commit
    _run_git(["git", "init"], repo_dir)
    _run_git(["git", "config", "user.email", "test@test.com"], repo_dir)
    _run_git(["git", "config", "user.name", "Test User"], repo_dir)
    _run_git(["git", "add", "."], repo_dir)
    _run_git(["git", "commit", "-m", "Initial commit"], repo_dir)


def test_help_message() -> None:
    """Displays usage, flags, and examples without legacy subcommands."""
    output, _ = run_cli("--help")
    assert "Visualise Python repository evolution" in output
    assert "repo_path" in output
    assert "--csv FILE" in output
    assert "--output-dir DIR" in output
    assert "examples:" in output
    # Should NOT have old subcommands
    assert "count-lines" not in output
    assert "generate-csv" not in output


@pytest.mark.slow
def test_git_analysis_creates_csv_and_images_in_output_dir(tmp_path: Path) -> None:
    """Full pipeline: Git commits → CSV + WebP charts in --output-dir."""
    repo_dir = tmp_path / "test_repo"
    create_test_git_repo(repo_dir)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run full pipeline with specific repo path and output directory
    _output, exit_code = run_cli(str(repo_dir), "--output-dir", str(output_dir))

    # Verify all outputs created in correct location
    assert exit_code == 0
    assert (output_dir / "repo_history.csv").exists()
    assert (output_dir / "repo_evolution.webp").exists()
    assert (output_dir / "repo_modules.webp").exists()

    # Verify files NOT created in repo directory
    assert not (repo_dir / "repo_history.csv").exists()


@pytest.mark.slow
def test_csv_flag_generates_images_from_existing_csv(tmp_path: Path) -> None:
    """Skips Git traversal, reads provided CSV, generates charts only."""
    # Create a sample CSV file
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "timestamp,commit_id,filedir,filename,category,line_count\n"
        "2025-01-01T00:00:00+00:00,abc123,src,example.py,code,10\n"
        "2025-01-01T00:00:00+00:00,abc123,src,example.py,docstrings_comments,5\n"
    )

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run CLI with --csv flag
    _output, exit_code = run_cli("--csv", str(csv_file), "--output-dir", str(output_dir))

    # Should create images but NOT regenerate CSV
    assert exit_code == 0
    assert not (output_dir / "repo_history.csv").exists()
    assert (output_dir / "repo_evolution.webp").exists()
    assert (output_dir / "repo_modules.webp").exists()
