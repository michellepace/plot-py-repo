"""Simple CLI user flow tests for plot-py-repo."""

import subprocess
from pathlib import Path


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


def test_help_message() -> None:
    """Test that help message shows new simplified interface."""
    output, _ = run_cli("--help")
    assert "Visualise Python repository evolution" in output
    assert "repo_path" in output
    assert "--csv FILE" in output
    assert "--output-dir DIR" in output
    assert "examples:" in output
    # Should NOT have old subcommands
    assert "count-lines" not in output
    assert "generate-csv" not in output


def test_visualize_default(tmp_path: Path) -> None:
    """Test default behavior analyses current directory."""
    # Create a minimal Git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / "src").mkdir()
    test_file = repo_dir / "src" / "example.py"
    test_file.write_text('"""Module docstring."""\n\nprint("hello")\n')

    # Initialize Git and make a commit
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Run CLI from repo directory
    _output, exit_code = run_cli("--output-dir", str(tmp_path))

    # Should create CSV and images
    assert exit_code == 0
    assert (tmp_path / "repo_history.csv").exists()
    assert (tmp_path / "repo_evolution.webp").exists()
    assert (tmp_path / "repo_modules.webp").exists()


def test_visualize_specific_repo(tmp_path: Path) -> None:
    """Test analysing a specific repository path."""
    # Create a minimal Git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / "src").mkdir()
    test_file = repo_dir / "src" / "example.py"
    test_file.write_text('"""Module docstring."""\n\nprint("hello")\n')

    # Initialize Git and make a commit
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Run CLI with specific repo path
    _output, exit_code = run_cli(str(repo_dir), "--output-dir", str(output_dir))

    # Should create CSV and images in output dir
    assert exit_code == 0
    assert (output_dir / "repo_history.csv").exists()
    assert (output_dir / "repo_evolution.webp").exists()
    assert (output_dir / "repo_modules.webp").exists()


def test_visualize_csv_flag(tmp_path: Path) -> None:
    """Test --csv flag skips Git analysis and just creates visualisations."""
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

    # Should create images but NOT CSV
    assert exit_code == 0
    assert not (output_dir / "repo_history.csv").exists()
    assert (output_dir / "repo_evolution.webp").exists()
    assert (output_dir / "repo_modules.webp").exists()


def test_visualize_output_dir(tmp_path: Path) -> None:
    """Test --output-dir flag controls where files are written."""
    # Create a minimal Git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / "src").mkdir()
    test_file = repo_dir / "src" / "example.py"
    test_file.write_text('"""Module docstring."""\n\nprint("hello")\n')

    # Initialize Git and make a commit
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    output_dir = tmp_path / "custom_output"
    output_dir.mkdir()

    # Run CLI with custom output directory
    _output, exit_code = run_cli(str(repo_dir), "--output-dir", str(output_dir))

    # All files should be in custom output directory
    assert exit_code == 0
    assert (output_dir / "repo_history.csv").exists()
    assert (output_dir / "repo_evolution.webp").exists()
    assert (output_dir / "repo_modules.webp").exists()
    # Should NOT be in repo directory
    assert not (repo_dir / "repo_history.csv").exists()
