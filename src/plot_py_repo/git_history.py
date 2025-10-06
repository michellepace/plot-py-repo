"""Git history traversal and CSV generation."""

import subprocess
import sys
from pathlib import Path

from .count_lines import classify_lines


class GitError(Exception):
    """Raised when Git operations fail."""


def get_commits(repo_path: str) -> list[tuple[str, str]]:
    """Get list of (commit_hash, timestamp) from Git history (newest first).

    Args:
        repo_path: Path to Git repository

    Returns:
        List of tuples containing (commit_hash, git_timestamp_string).
        Timestamp format matches Git's default: "YYYY-MM-DD HH:MM:SS +ZZZZ"

    Raises:
        GitError: If directory is not a Git repository
    """
    try:
        output = (
            subprocess.check_output(
                ["/usr/bin/git", "log", "--format=%h %ai"],
                cwd=repo_path,
                stderr=subprocess.STDOUT,
            )
            .decode()
            .strip()
        )
        if not output:
            # Empty repo (initialized but no commits)
            return []

        commits = []
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            commit_hash = parts[0]
            git_timestamp = parts[1]
            commits.append((commit_hash, git_timestamp))
    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode() if e.output else ""
        if "not a git repository" in error_msg.lower():
            msg = "Not a Git repository"
            raise GitError(msg) from e
        # Empty repository (no commits yet)
        return []
    else:
        return commits


def generate_csv(repo_path: str, output_dir: str) -> str:
    """Generate CSV file from Git commit history.

    Args:
        repo_path: Path to Git repository
        output_dir: Directory where CSV file should be written

    Returns:
        Path to the generated CSV file

    Raises:
        SystemExit: If Git log cannot be read or no Python files found
    """
    # Display repo path being analyzed
    display_path = repo_path if repo_path != "." else "current directory"
    print(f"➡️  Analyzing Git history at {display_path}...")

    # Extract repository name
    repo_name = Path(repo_path).resolve().name

    # Construct output file path
    output_file = Path(output_dir) / "repo_history.csv"
    file_exists = output_file.exists()

    # Get commits
    try:
        commits = get_commits(repo_path)
    except GitError as e:
        print(f"❌  {e}")
        sys.exit(1)

    if not commits:
        print("❌  No commits yet in this repository")
        sys.exit(1)

    # Track statistics
    total_python_files = 0
    lines_written = 0

    with output_file.open("w", encoding="utf-8") as f:
        f.write(
            "repo_name,commit_date,commit_id,filedir,filename,code_lines,docstring_lines,"
            "comment_lines,total_lines,documentation_lines\n"
        )
        lines_written += 1

        for commit_hash, git_timestamp in commits:
            try:
                tree_output = (
                    subprocess.check_output(  # noqa: S603
                        [
                            "/usr/bin/git",
                            "ls-tree",
                            "-r",
                            "--name-only",
                            commit_hash,
                            "src/",
                            "tests/",
                        ],
                        cwd=repo_path,
                    )
                    .decode()
                    .strip()
                )
                files = [f for f in tree_output.splitlines() if f.endswith(".py")]
            except subprocess.CalledProcessError:
                # Silently skip commits with errors (e.g., empty commits)
                continue

            for file_path in files:
                total_python_files += 1
                filedir = (
                    "src"
                    if file_path.startswith("src/")
                    else "tests"
                    if file_path.startswith("tests/")
                    else None
                )
                if not filedir:
                    continue

                filename = Path(file_path).name

                try:
                    content_output = subprocess.check_output(  # noqa: S603
                        ["/usr/bin/git", "show", f"{commit_hash}:{file_path}"],
                        cwd=repo_path,
                    )
                    content = content_output.decode("utf-8", errors="ignore")
                except subprocess.CalledProcessError:
                    # Silently skip files that can't be read
                    continue

                docstring_lines, comment_lines, code_lines = classify_lines(content)
                documentation_lines = docstring_lines + comment_lines
                total_lines = len(content.splitlines())

                # Write single row with all columns
                #  (timestamp format: "YYYY-MM-DD HH:MM:SS +ZZZZ")
                f.write(
                    f"{repo_name},{git_timestamp},{commit_hash},{filedir},{filename},"
                    f"{code_lines},{docstring_lines},{comment_lines},"
                    f"{total_lines},{documentation_lines}\n"
                )
                lines_written += 1

    # Check if any Python files were found
    if total_python_files == 0:
        print("❌  No Python files found in src/ or tests/ directories")
        output_file.unlink()  # Clean up empty CSV
        sys.exit(1)

    # Success message
    overwrite_msg = " (overwrote existing file)" if file_exists else ""
    print(f"✅  Success! Created {output_file}{overwrite_msg}")
    print(f"    • {len(commits)} commits analyzed")
    print(f"    • {lines_written:,} lines written")

    return str(output_file)
