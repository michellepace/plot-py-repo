"""Line counting and classification for Python source files."""

import ast
import contextlib
import tokenize
from io import StringIO


def _extract_docstring_lines(content: str) -> set[int]:
    """Extract line numbers containing docstrings from Python content."""
    docstring_lines: set[int] = set()
    try:
        tree = ast.parse(content)

        class DocVisitor(ast.NodeVisitor):
            def visit(self, node: ast.AST) -> None:
                if isinstance(
                    node,
                    (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                ):
                    doc = ast.get_docstring(node)
                    if doc is not None and node.body:
                        first_stmt = node.body[0]
                        if isinstance(first_stmt, ast.Expr) and isinstance(
                            first_stmt.value, ast.Constant
                        ):
                            doc_node = first_stmt.value
                            start = doc_node.lineno
                            end = doc_node.end_lineno
                            if start and end:
                                for line_num in range(start, end + 1):
                                    docstring_lines.add(line_num)
                self.generic_visit(node)

        visitor = DocVisitor()
        visitor.visit(tree)
    except SyntaxError:
        # If parsing fails, treat as no docstrings
        pass
    return docstring_lines


def _tokenize_content(content: str) -> list[tokenize.TokenInfo]:
    """Tokenise Python content, returning empty list on error."""
    tokens: list[tokenize.TokenInfo] = []
    with contextlib.suppress(tokenize.TokenError):
        tokens = list(tokenize.generate_tokens(StringIO(content).readline))
    return tokens


def _mark_code_lines(
    tokens: list[tokenize.TokenInfo], line_classifications: list[str]
) -> None:
    """Mark lines as 'code' based on non-structural, non-comment tokens."""
    structural = {
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.ENCODING,
    }
    for tok in tokens:
        toktype, _, start, end, _ = tok
        if toktype in structural or toktype == tokenize.COMMENT:
            continue
        start_row, _ = start
        end_row, _ = end
        for row in range(start_row, end_row + 1):
            if (
                0 < row <= len(line_classifications)
                and line_classifications[row - 1] == "pending"
            ):
                line_classifications[row - 1] = "code"


def _mark_comment_lines(
    tokens: list[tokenize.TokenInfo], line_classifications: list[str]
) -> None:
    """Mark lines as 'comment' based on comment tokens."""
    for tok in tokens:
        toktype, _, start, _, _ = tok
        if toktype == tokenize.COMMENT:
            start_row, _ = start
            if (
                0 < start_row <= len(line_classifications)
                and line_classifications[start_row - 1] == "pending"
            ):
                line_classifications[start_row - 1] = "comment"


def classify_lines(content: str) -> tuple[int, int, int]:
    """Count lines in Python content, classifying each as docstring, comment, or code.

    Blank lines are counted as code.

    Args:
        content: Python source code as string

    Returns:
        Tuple of (docstring_lines, comment_lines, code_lines) total counts
    """
    # Handle truly empty content (0 bytes)
    if not content:
        return (0, 0, 0)

    if not content.endswith("\n"):
        content += "\n"

    lines = content.splitlines()
    total_lines = len(lines)

    # Collect docstring lines using AST
    docstring_lines = _extract_docstring_lines(content)

    # Tokenise the content
    tokens = _tokenize_content(content)

    # Initialise classification list (0-based index)
    line_classifications = ["pending"] * total_lines

    # Set docstring classifications
    for line_num in docstring_lines:
        line_classifications[line_num - 1] = "docstring"

    # Mark code and comment lines
    if tokens:
        _mark_code_lines(tokens, line_classifications)
        _mark_comment_lines(tokens, line_classifications)
    else:
        # Fallback: when tokenisation fails, mark non-blank lines as code
        for i, line in enumerate(lines):
            if line.strip() and line_classifications[i] == "pending":
                line_classifications[i] = "code"

    # Remaining 'pending' are blanks
    for i in range(total_lines):
        if line_classifications[i] == "pending":
            line_classifications[i] = "blank"

    # Count the categories (blanks are included in code count)
    return (
        line_classifications.count("docstring"),
        line_classifications.count("comment"),
        line_classifications.count("code") + line_classifications.count("blank"),
    )
