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
    """Tokenize Python content, returning empty list on error."""
    tokens: list[tokenize.TokenInfo] = []
    with contextlib.suppress(tokenize.TokenError):
        tokens = list(tokenize.generate_tokens(StringIO(content).readline))
    return tokens


def _mark_code_lines(tokens: list[tokenize.TokenInfo], classif: list[str]) -> None:
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
            if 0 < row <= len(classif) and classif[row - 1] == "pending":
                classif[row - 1] = "code"


def _mark_comment_lines(tokens: list[tokenize.TokenInfo], classif: list[str]) -> None:
    """Mark lines as 'comment' based on comment tokens."""
    for tok in tokens:
        toktype, _, start, _, _ = tok
        if toktype == tokenize.COMMENT:
            start_row, _ = start
            if 0 < start_row <= len(classif) and classif[start_row - 1] == "pending":
                classif[start_row - 1] = "comment"


def classify_lines(content: str) -> tuple[int, int, int]:
    """Classify lines in Python content as docstrings, comments, or code.

    Args:
        content: Python source code as string

    Returns:
        Tuple of (docstring_lines, comment_lines, code_lines) counts
    """
    if not content.endswith("\n"):
        content += "\n"

    lines = content.splitlines()
    total_lines = len(lines)

    # Collect docstring lines using AST
    docstring_lines = _extract_docstring_lines(content)

    # Tokenize the content
    tokens = _tokenize_content(content)

    # Initialize classification list (0-based index)
    classif = ["pending"] * total_lines

    # Set docstring classifications
    for line_num in docstring_lines:
        classif[line_num - 1] = "docstring"

    # Mark code and comment lines
    _mark_code_lines(tokens, classif)
    _mark_comment_lines(tokens, classif)

    # Remaining 'pending' are blanks
    for i in range(total_lines):
        if classif[i] == "pending":
            classif[i] = "blank"

    # Count the categories
    return (
        classif.count("docstring"),
        classif.count("comment"),
        classif.count("code"),
    )
