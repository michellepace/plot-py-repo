"""Tests for git_history module."""

import subprocess
from pathlib import Path

from plot_py_repo.git_history import generate_csv


def _run_git(command: list[str], repo_path: Path) -> str:
    """Run git command in repo and return output."""
    return subprocess.check_output(command, cwd=repo_path).decode().strip()  # noqa: S603


def test_csv_timestamps_match_git_log_default_timezone(tmp_path: Path) -> None:
    """CSV commit_date column should match git log's default timezone output."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    _run_git(["git", "init"], repo_path)
    _run_git(["git", "config", "user.name", "Test User"], repo_path)
    _run_git(["git", "config", "user.email", "test@example.com"], repo_path)

    (repo_path / "src").mkdir()
    (repo_path / "src" / "example.py").write_text("def hello():\n    pass\n")

    _run_git(["git", "add", "."], repo_path)
    _run_git(["git", "commit", "-m", "Initial commit"], repo_path)

    git_timestamp = _run_git(["git", "log", "-1", "--format=%ai"], repo_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    csv_timestamp = Path(csv_path).read_text().split("\n")[1].split(",")[0]

    assert csv_timestamp == git_timestamp


def test_csv_uses_wide_format_with_nine_columns(tmp_path: Path) -> None:
    """CSV uses wide format with 9 columns including derived columns."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    _run_git(["git", "init"], repo_path)
    _run_git(["git", "config", "user.name", "Test User"], repo_path)
    _run_git(["git", "config", "user.email", "test@example.com"], repo_path)

    # Create file with known line counts: 1 docstring, 1 comment, 2 executable
    (repo_path / "src").mkdir()
    file_content = '"""Docstring."""\n# Comment\nx = 1\ny = 2\n'
    (repo_path / "src" / "example.py").write_text(file_content)

    _run_git(["git", "add", "."], repo_path)
    _run_git(["git", "commit", "-m", "Initial commit"], repo_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    csv_content = Path(csv_path).read_text()
    lines = csv_content.strip().split("\n")

    # Verify header
    header = lines[0]
    expected_header = (
        "commit_date,commit_id,filedir,filename,executable_lines,"
        "docstring_lines,comment_lines,total_lines,documentation_lines"
    )
    assert header == expected_header, (
        f"Expected header:\n{expected_header}\nGot:\n{header}"
    )

    # Verify data row (should be only one row for one file)
    assert len(lines) == 2, f"Expected 2 lines (header + 1 data row), got {len(lines)}"
    data_row = lines[1]
    columns = data_row.split(",")

    # Verify 9 columns
    assert len(columns) == 9, f"Expected 9 columns, got {len(columns)}: {columns}"

    # Extract numeric columns
    executable_lines = int(columns[4])
    docstring_lines = int(columns[5])
    comment_lines = int(columns[6])
    total_lines = int(columns[7])
    documentation_lines = int(columns[8])

    # Verify derived columns
    assert documentation_lines == docstring_lines + comment_lines, (
        f"documentation_lines ({documentation_lines}) should equal "
        f"docstring_lines ({docstring_lines}) + comment_lines ({comment_lines})"
    )

    assert total_lines == docstring_lines + comment_lines + executable_lines, (
        f"total_lines ({total_lines}) should equal sum of "
        f"docstring ({docstring_lines}) + comment ({comment_lines}) + "
        f"executable ({executable_lines})"
    )
