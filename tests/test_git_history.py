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
