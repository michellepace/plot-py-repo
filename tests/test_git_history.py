"""Tests for git_history module."""

import subprocess
from pathlib import Path

from plot_py_repo.git_history import generate_csv


def _run_git(command: list[str], repo_path: Path) -> str:
    """Run git command in repo and return output."""
    return subprocess.check_output(command, cwd=repo_path).decode().strip()  # noqa: S603


def _create_test_repo_with_commit(
    tmp_path: Path, file_content: str = "def hello():\n    pass\n"
) -> Path:
    """Create initialized Git repo with a committed Python file."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    _run_git(["git", "init"], repo_path)
    _run_git(["git", "config", "user.name", "Test User"], repo_path)
    _run_git(["git", "config", "user.email", "test@example.com"], repo_path)

    (repo_path / "src").mkdir()
    (repo_path / "src" / "example.py").write_text(file_content)

    _run_git(["git", "add", "."], repo_path)
    _run_git(["git", "commit", "-m", "Initial commit"], repo_path)

    return repo_path


def test_csv_timestamps_match_git_log_default_timezone(tmp_path: Path) -> None:
    """CSV commit_date column should match git log's default timezone output."""
    repo_path = _create_test_repo_with_commit(tmp_path)

    git_timestamp = _run_git(["git", "log", "-1", "--format=%ai"], repo_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    csv_timestamp = Path(csv_path).read_text().split("\n")[1].split(",")[0]

    assert csv_timestamp == git_timestamp


def test_csv_has_nine_columns_in_wide_format(tmp_path: Path) -> None:
    """CSV uses wide format with 9 columns in header and data rows."""
    repo_path = _create_test_repo_with_commit(tmp_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    csv_content = Path(csv_path).read_text()
    lines = csv_content.strip().split("\n")

    # Verify header has 9 columns
    header = lines[0]
    expected_header = (
        "commit_date,commit_id,filedir,filename,code_lines,"
        "docstring_lines,comment_lines,total_lines,documentation_lines"
    )
    assert header == expected_header, (
        f"Expected header:\n{expected_header}\nGot:\n{header}"
    )

    # Verify data row has 9 columns
    data_row = lines[1]
    columns = data_row.split(",")
    assert len(columns) == 9, f"Expected 9 columns, got {len(columns)}: {columns}"


def test_csv_derived_columns_calculated_correctly(tmp_path: Path) -> None:
    """CSV derived columns use correct formulas: documentation_lines and total_lines."""
    # Create file with known line counts: 1 docstring, 1 comment, 2 code
    file_content = '"""Docstring."""\n# Comment\nx = 1\ny = 2\n'
    repo_path = _create_test_repo_with_commit(tmp_path, file_content)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    csv_content = Path(csv_path).read_text()
    lines = csv_content.strip().split("\n")

    # Extract numeric columns from data row
    columns = lines[1].split(",")
    code_lines = int(columns[4])
    docstring_lines = int(columns[5])
    comment_lines = int(columns[6])
    total_lines = int(columns[7])
    documentation_lines = int(columns[8])

    # Verify documentation_lines = docstring_lines + comment_lines
    assert documentation_lines == docstring_lines + comment_lines, (
        f"documentation_lines ({documentation_lines}) should equal "
        f"docstring_lines ({docstring_lines}) + comment_lines ({comment_lines})"
    )

    # Verify total_lines = code_lines + docstring_lines + comment_lines
    assert total_lines == code_lines + docstring_lines + comment_lines, (
        f"total_lines ({total_lines}) should equal "
        f"code_lines ({code_lines}) + docstring_lines ({docstring_lines}) + "
        f"comment_lines ({comment_lines})"
    )
