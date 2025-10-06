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


def _parse_csv_first_row(csv_path: str) -> tuple[list[str], list[str]]:
    """Parse CSV header and first data row.

    Returns:
        Tuple of (header_columns, first_data_row)
    """
    lines = Path(csv_path).read_text().split("\n")
    return lines[0].split(","), lines[1].split(",")


def test_csv_timestamps_match_git_log_default_timezone(tmp_path: Path) -> None:
    """CSV commit_date column should match git log's default timezone output."""
    repo_path = _create_test_repo_with_commit(tmp_path)
    git_timestamp = _run_git(["git", "log", "-1", "--format=%ai"], repo_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    header, data = _parse_csv_first_row(csv_path)
    csv_timestamp = data[header.index("commit_date")]

    assert csv_timestamp == git_timestamp


def test_csv_has_ten_columns_in_wide_format(tmp_path: Path) -> None:
    """CSV uses wide format with 10 columns in header and data rows."""
    repo_path = _create_test_repo_with_commit(tmp_path)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    header, data = _parse_csv_first_row(csv_path)

    # Verify header has 10 columns with expected names
    expected_columns = {
        "repo_name",
        "commit_date",
        "commit_id",
        "filedir",
        "filename",
        "code_lines",
        "docstring_lines",
        "comment_lines",
        "total_lines",
        "documentation_lines",
    }
    assert len(header) == 10, f"Expected 10 columns, got {len(header)}: {header}"
    assert set(header) == expected_columns, (
        f"Column mismatch: {set(header) ^ expected_columns}"
    )

    # Verify data row has 10 columns
    assert len(data) == 10, f"Expected 10 columns, got {len(data)}: {data}"


def test_csv_derived_columns_calculated_correctly(tmp_path: Path) -> None:
    """CSV derived columns use correct formulas: documentation_lines and total_lines."""
    # Create file with known line counts: 1 docstring, 1 comment, 2 code
    file_content = '"""Docstring."""\n# Comment\nx = 1\ny = 2\n'
    repo_path = _create_test_repo_with_commit(tmp_path, file_content)

    csv_path = generate_csv(str(repo_path), str(tmp_path))
    header, data = _parse_csv_first_row(csv_path)

    # Extract numeric columns by name
    code_lines = int(data[header.index("code_lines")])
    docstring_lines = int(data[header.index("docstring_lines")])
    comment_lines = int(data[header.index("comment_lines")])
    total_lines = int(data[header.index("total_lines")])
    documentation_lines = int(data[header.index("documentation_lines")])

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
