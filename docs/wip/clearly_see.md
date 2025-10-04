# Test Organization Analysis: `test_count_lines.py`

## Current State

**Total tests:** 17
**Structure:** Flat list of functions
**Problem:** "Cannot see the wood through the trees" - difficult to navigate and understand coverage

## Test-by-Test Analysis

### 1. `test_empty_content`

**Covers:** Edge case - completely empty input (zero lines)
**Classification:** Edge Cases & Error Handling

### 2. `test_single_blank_line`

**Covers:** Blank line behavior (not counted)
**Classification:** Blank Line Handling

### 3. `test_module_docstring_single_line`

**Covers:** Module-level docstring (single line)
**Classification:** Docstring Classification

### 4. `test_module_docstring_multiline`

**Covers:** Module-level docstring (multi-line, includes blank lines within)
**Classification:** Docstring Classification

### 5. `test_function_docstring`

**Covers:** Function-level docstring
**Classification:** Docstring Classification

### 6. `test_async_function_docstring`

**Covers:** Async function-level docstring
**Classification:** Docstring Classification

### 7. `test_decorator_counts_as_code`

**Covers:** Decorator syntax classified as code
**Classification:** Code Classification

### 8. `test_class_docstring`

**Covers:** Class-level docstring
**Classification:** Docstring Classification

### 9. `test_nested_function_docstring`

**Covers:** Nested function docstrings (multiple docstrings in one file)
**Classification:** Docstring Classification

### 10. `test_standalone_comment`

**Covers:** Comment on its own line
**Classification:** Comment Classification

### 11. `test_inline_comment_counts_as_code`

**Covers:** **Critical distinction** - inline comments classified as code (priority rule)
**Classification:** Classification Priority Rules (difficult to classify - see below)

### 12. `test_simple_code_statement`

**Covers:** Basic code statement
**Classification:** Code Classification

### 13. `test_string_literal_not_docstring`

**Covers:** String literal assigned to variable (not a docstring)
**Classification:** Docstring Exclusions (difficult to classify - see below)

### 14. `test_multiline_string_literal_not_docstring`

**Covers:** Multi-line string literal assigned to variable (not a docstring)
**Classification:** Docstring Exclusions (difficult to classify - see below)

### 15. `test_syntax_error_handles_gracefully`

**Covers:** Error handling - malformed Python doesn't crash
**Classification:** Edge Cases & Error Handling

### 16. `test_content_without_trailing_newline`

**Covers:** Edge case - content normalization (missing final newline)
**Classification:** Edge Cases & Error Handling

### 17. `test_classify_lines_comprehensive`

**Covers:** Integration test - realistic Python file with all classification types
**Classification:** Integration Tests

---

## Logical Groupings

### Group 1: Docstring Classification (6 tests)

Tests the AST-based docstring detection for all supported node types:

- `test_module_docstring_single_line`
- `test_module_docstring_multiline`
- `test_function_docstring`
- `test_async_function_docstring`
- `test_class_docstring`
- `test_nested_function_docstring`

**Coverage:** Module, FunctionDef, AsyncFunctionDef, ClassDef docstrings (maps to `_extract_docstring_lines`)

### Group 2: Docstring Exclusions (2 tests)

Tests what doesn't qualify as a docstring:

- `test_string_literal_not_docstring`
- `test_multiline_string_literal_not_docstring`

**Coverage:** String literals that aren't first statement in module/function/class

### Group 3: Comment Classification (2 tests)

Tests comment detection and priority:

- `test_standalone_comment`
- `test_inline_comment_counts_as_code`

**Coverage:** Standalone vs inline comments (maps to `_mark_comment_lines` and priority rules)

### Group 4: Code Classification (2 tests)

Tests basic code detection:

- `test_decorator_counts_as_code`
- `test_simple_code_statement`

**Coverage:** Decorator syntax and basic code lines (maps to `_mark_code_lines`)

### Group 5: Blank Line Handling (1 test)

Tests blank line behavior:

- `test_single_blank_line`

**Coverage:** Lines that remain "pending" become "blank"

### Group 6: Edge Cases & Error Handling (3 tests)

Tests robustness:

- `test_empty_content`
- `test_syntax_error_handles_gracefully`
- `test_content_without_trailing_newline`

**Coverage:** Empty input, malformed Python, missing newline

### Group 7: Integration (1 test)

Tests complete flow:

- `test_classify_lines_comprehensive`

**Coverage:** All classification types in realistic scenario

---

## Difficult-to-Classify Tests (and decisions made)

### 1. `test_inline_comment_counts_as_code`

**Conflict:** Is this testing comments or code?
**Decision:** Placed in "Comment Classification" because it tests comment behavior, specifically the classification priority rule (code tokens take precedence over comment tokens on the same line).
**Rationale:** Understanding comment behavior requires knowing this distinction.

### 2. `test_string_literal_not_docstring` + `test_multiline_string_literal_not_docstring`

**Conflict:** Are these testing docstrings or code?
**Decision:** Created separate "Docstring Exclusions" group rather than merging into "Docstring Classification" or "Code Classification".
**Rationale:** These tests verify the boundaries of what qualifies as a docstring (negative cases), which is conceptually different from testing that docstrings are detected (positive cases).

### 3. `test_empty_content`

**Conflict:** Is this an edge case or a blank line test?
**Decision:** Placed in "Edge Cases & Error Handling" because empty content is zero lines (not blank lines).
**Rationale:** Blank lines exist within content; empty content is a boundary condition.

---

## Recommendation: Organize with Test Classes

### Verdict: **Yes, organize - clarity gains outweigh complexity**

**Rationale:**

1. **Current pain:** User cannot navigate 17 tests effectively
2. **Growth expected:** Test suite will expand as edge cases emerge
3. **Clear structure:** Groups map directly to implementation flow
4. **Low overhead:** Test classes add minimal syntax (no `self` needed)
5. **Better coverage visibility:** Easy to spot gaps and ensure complete coverage

### Alternative Considered: Comment-Based Grouping

```python
# === Docstring Classification ===

def test_module_docstring_single_line():
    ...
```

**Pros:** Simpler, less code
**Cons:** Weaker separation, harder to navigate, no pytest benefits (shared fixtures, class-level setup)

**Verdict:** Too weak for 17+ tests spanning 7 logical groups

---

## Proposed Structure

```python
"""Tests for count_lines module."""

from plot_py_repo.count_lines import classify_lines


class TestDocstringClassification:
    """Tests for AST-based docstring detection."""

    def test_module_docstring_single_line(self) -> None: ...
    def test_module_docstring_multiline(self) -> None: ...
    def test_function_docstring(self) -> None: ...
    def test_async_function_docstring(self) -> None: ...
    def test_class_docstring(self) -> None: ...
    def test_nested_function_docstring(self) -> None: ...


class TestDocstringExclusions:
    """Tests for what doesn't qualify as a docstring."""

    def test_string_literal_not_docstring(self) -> None: ...
    def test_multiline_string_literal_not_docstring(self) -> None: ...


class TestCommentClassification:
    """Tests for comment detection and priority rules."""

    def test_standalone_comment(self) -> None: ...
    def test_inline_comment_counts_as_code(self) -> None: ...


class TestCodeClassification:
    """Tests for basic code detection."""

    def test_decorator_counts_as_code(self) -> None: ...
    def test_simple_code_statement(self) -> None: ...


class TestBlankLineHandling:
    """Tests for blank line behavior."""

    def test_single_blank_line(self) -> None: ...


class TestEdgeCasesAndErrorHandling:
    """Tests for robustness and boundary conditions."""

    def test_empty_content(self) -> None: ...
    def test_syntax_error_handles_gracefully(self) -> None: ...
    def test_content_without_trailing_newline(self) -> None: ...


class TestIntegration:
    """Integration tests for complete classification flow."""

    def test_classify_lines_comprehensive(self) -> None: ...
```

---

## Benefits of This Structure

1. **Instant coverage visibility:** Scan class names to understand what's tested
2. **Easy navigation:** Jump to relevant section by group
3. **Exposes gaps:** Easy to identify missing test coverage within each category
4. **Future-proof:** New tests have clear home (e.g., more edge cases go in TestEdgeCasesAndErrorHandling)
5. **Self-documenting:** Class docstrings explain what each group tests
6. **pytest benefits:** Can share fixtures within classes if needed later

---

## Coverage Gaps Identified

While analyzing tests, identified potential missing coverage:

- **Multiple blank lines:** Single blank tested, but not consecutive blanks
- **Mixed scenarios:** Only one integration test for comprehensive scenarios

**Recommendation:** Add remaining tests to appropriate classes after reorganization.
