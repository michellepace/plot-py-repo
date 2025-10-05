"""Tests for count_lines module."""

from plot_py_repo.count_lines import classify_lines


def _assert_count(category: str, expected: int, actual: int) -> None:
    """Assert that line count matches expected value."""
    assert actual == expected, f"Expected {expected} {category}, got {actual}"


# Edge cases


def test_empty_content() -> None:
    """Empty content returns zero counts."""
    content = ""

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 0, executable_cnt)


def test_single_blank_line() -> None:
    """Single blank line is not counted."""
    content = "\n"

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 0, executable_cnt)


def test_blank_lines_between_executable_code_not_counted() -> None:
    """Blank lines between executable code statements are not counted."""
    content = "\n\nx = 1\n\n\ny = 2\n\n"

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 2, executable_cnt)


# Docstrings


def test_single_line_module_docstring_counts_as_docstring() -> None:
    """Triple-quoted string at module level counts as docstring."""
    content = '"""Module docstring."""\n'

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 1, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 0, executable_cnt)


def test_multiline_module_docstring_counts_as_docstring() -> None:
    """All lines including blanks and closing delimiter count as docstring."""
    content = '''"""Line 1 of 5.


Line 3 of 5 - blank lines and closing empty delimiter count!.
"""
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 5, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 0, executable_cnt)


def test_function_docstring_counts_as_docstring() -> None:
    """Function body docstring counts separately from function definition line."""
    content = '''def foo():
    """Function docstring."""
    pass
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 1, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 2, executable_cnt)


def test_async_function_docstring_counts_as_docstring() -> None:
    """Async functions follow same docstring rules as regular functions."""
    content = '''async def fetch():
    """Async docstring."""
    pass # inline comment lines not counted
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 1, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 2, executable_cnt)


def test_class_docstring_counts_as_docstring() -> None:
    """Class body docstring counts separately from class definition line."""
    content = '''class Foo:
    """Class docstring."""
    pass
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 1, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 2, executable_cnt)


def test_nested_function_docstrings_count_as_docstrings() -> None:
    """Each nesting level's docstring counts independently."""
    content = '''def outer():
    """Outer docstring."""
    def inner():
        """Inner docstring."""
        pass
    pass
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 2, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 4, executable_cnt)


# Comments


def test_standalone_comments_count_as_comments() -> None:
    """Comment-only lines count as comments, not executable code."""
    content = "# This is a comment\n\n  # This is a second comment"

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 2, comments_cnt)
    _assert_count("executable line(s)", 0, executable_cnt)


def test_inline_comment_counts_as_executable_code() -> None:
    """Line with inline comment is counted as executable code, not as a comment."""
    content = "x = 1  # inline comment\n"

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 1, executable_cnt)


# Executable


def test_executable_code_statements() -> None:
    """Executable code statements are counted correctly."""
    content = """for i in range(3):
    print(i)
"""

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 2, executable_cnt)


def test_decorator_counts_as_executable_code() -> None:
    """Decorators are counted as executable code."""
    content = """@decorator
def foo():
    pass
"""

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 3, executable_cnt)


# String literals


def test_string_literals_count_as_executable_code() -> None:
    """Triple-quoted strings in assignments count as executable code, not docstrings."""
    content = '''x = """This is a string literal"""
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 1, executable_cnt)


def test_multiline_string_literals_count_as_executable_code() -> None:
    """All lines of assigned string literals count as executable code."""
    content = '''x = """Code Line 1
Code Line 2

Code Line 4 # not a comment"""
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 4, executable_cnt)


# Error handling


def test_syntax_error_handles_gracefully_unclosed_paren() -> None:
    """Content with unclosed parenthesis is handled without crashing."""
    content = """def broken(
    x = 1
print("test")
"""

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 3, executable_cnt)


def test_syntax_error_handles_gracefully_missing_colon() -> None:
    """Content with missing colon is handled without crashing."""
    content = """if True
    pass
print("test")
"""

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 3, executable_cnt)


def test_content_without_trailing_newline() -> None:
    """Content without trailing newline is handled correctly."""
    content = "x = 1"

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    _assert_count("docstring line(s)", 0, docstrings_cnt)
    _assert_count("comment line(s)", 0, comments_cnt)
    _assert_count("executable line(s)", 1, executable_cnt)


# Integration


def test_classify_lines_comprehensive() -> None:
    """Classification of all line types in realistic Python file."""
    content = '''"""Module docstring line 1 of 4.

Module docstring line 3 of 4.
"""

# Comment line 1
x = 1  # Inline comment - whole line is EXECUTABLE
MIN_LENGTH = 5


def greet() -> str:
    """Function docstring single line."""

    def _helper() -> str:
        """Nested function docstring."""
        return "hi"

    result = _helper() + " hello"
    result = result.upper()
    if len(result) > MIN_LENGTH:
        result = result + "!"
    return result  # Another inline - EXECUTABLE


class Horse:
    """Class docstring line 1 of 3.

    Class docstring line 3 of 3."""

    # Comment line 2 (inside class)
    legs = 4


text = """String literal (not docstring) line 1 of 5


String literal (not docstring) line 3 of 5
"""

# Comment line 3 (final)
'''

    docstrings_cnt, comments_cnt, executable_cnt = classify_lines(content)

    # Expected breakdown:
    # - Docstrings: 9 (module:4 + function:1 + nested:1 + class:3)
    # - Comments: 3 (comment line 1, comment inside class, final comment)
    # - Executable: 17 (assignments:3 + function defs:2 + function body:6
    #            + class def:1 + text assignment:5)

    _assert_count("docstring line(s)", 9, docstrings_cnt)
    _assert_count("comment line(s)", 3, comments_cnt)
    _assert_count("executable line(s)", 17, executable_cnt)

    # Verify total line count in content
    total_lines = len(content.splitlines())
    assert total_lines == 40, f"Expected 40 total lines in content, got {total_lines}"
