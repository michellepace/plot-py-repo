# CSV Structure & Blank Line Treatment: Decision Document

**Status:** ✅ Completed - Fully implemented as of 2025-10-05
**Created:** 2025-10-04
**Completed:** 2025-10-05
**Context:** Test refactoring of `test_count_lines.py` revealed data structure inconsistencies

## Implementation Summary

**Decision taken:** Both 1B + 2B (Wide CSV format + Blanks counted as code)

**Changes implemented:**

- CSV structure changed to wide format with derived columns
- Terminology: `executable_lines` → `code_lines` (includes blanks)
- All tests and documentation updated
- Equation verified: `code_lines + documentation_lines = total_lines`

**Commit:** `refactor: rename executable_lines to code_lines with blank line inclusion`

---

## Current State (Verified)

### `count_lines.py` Behavior

**Function signature:**

```python
classify_lines(content: str) -> tuple[int, int, int]
# Returns: (docstring_lines, comment_lines, code_lines)
```

**Internal processing:**

```python
classif = ["pending", "docstring", "executable", "comment", "blank", ...]
# Lines classified as "blank" ARE included in code_lines count
```

**Verified with `horse.py` (39 total lines):**

```python
classify_lines(horse_content) → (10, 3, 26)
# 10 docstrings + 3 comments + 26 code_lines (15 executable + 11 blanks) = 39 lines counted
# 26 + 13 = 39 ✓
```

### Current CSV Structure (`git_history.py`)

**Format:** Wide/flat (1 row per file)

**Header:**

```csv
commit_date,commit_id,filedir,filename,code_lines,docstring_lines,comment_lines,total_lines,documentation_lines
```

**Example rows:**

```csv
2025-09-30 23:47:26 +0200,83036f2,src,cli.py,26,10,3,39,13
```

**Column calculation logic:**

```python
docstring_lines, comment_lines, code_lines = classify_lines(content)
total_lines = len(content.splitlines())
documentation_lines = docstring_lines + comment_lines
```

### Current Chart Requirements

**`chart_evolution.py`** - Stacked area chart over time

- Uses `code_lines` column (split by src/tests)
- Uses `documentation_lines` column
- Maps to 3 display categories: "Source Code", "Test Code", "Documentation"

**`chart_breakdown.py`** - Horizontal bar by file

- Uses `total_lines` column: `groupby(["filedir", "filename"])["total_lines"].sum()`
- Total equals: `code_lines + documentation_lines`

---

## Decision 1: CSV Structure

### Option 1A: Keep Current (Long Format, Pre-aggregated)

**Structure:**

```csv
commit_date,commit_id,filedir,filename,category,line_count
2025-09-30...,83036f2,src,cli.py,code,26
2025-09-30...,83036f2,src,cli.py,documentation,13
```

**Characteristics:**

- 2 rows per file
- Categories: `code`, `documentation`
- Pre-aggregated in `git_history.py`

**Pros:**

- ✅ Already implemented and working
- ✅ Optimized for `chart_evolution.py` (primary chart)
- ✅ Follows "tidy data" principle (one observation per row)

**Cons:**

- ❌ Permanent loss of granularity (can't separate docstrings from comments)
- ❌ Future charts limited to existing category split
- ❌ Misalignment with `count_lines.py` output structure

---

### Option 1B: Flatten to Wide Format with Derived Columns

**Structure:**

```csv
commit_date,commit_id,filedir,filename,code_lines,docstring_lines,comment_lines,total_lines,documentation_lines
2025-09-30...,83036f2,src,cli.py,26,10,3,39,13
```

**Characteristics:**

- 1 row per file (50% fewer rows)
- Raw counts preserved: `docstring_lines, comment_lines, code_lines`
- Derived columns for convenience: `documentation_lines, total_lines`

**Implementation changes:**

**`git_history.py` (lines 145-156):**

```python
# Old (long format)
docstring_lines, comment_lines, code_lines = classify_lines(content)
documentation_lines = docstring_lines + comment_lines
f.write(f"...code,{code_lines}\n")
f.write(f"...documentation,{documentation_lines}\n")

# Implemented (wide format)
docstring_lines, comment_lines, code_lines = classify_lines(content)
total_lines = len(content.splitlines())
documentation_lines = docstring_lines + comment_lines
f.write(f"...{code_lines},{docstring_lines},{comment_lines},{total_lines},{documentation_lines}\n")
```

**`chart_evolution.py` (_prepare_data, implemented approach):**

```python
def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Works directly with wide format columns
    # Uses code_lines and documentation_lines columns
    # Applies src/tests split logic
    # Returns aggregated data for plotting

    # Rest of existing logic uses code_lines column...
```

**Alternative approach (pivot wide → long):**

```python
# Create long-format subset from wide format
df_code = df[["commit_date", "commit_id", "filedir", "filename", "code_lines"]].copy()
df_code["category"] = "code"
df_code["line_count"] = df_code["code_lines"]

df_docs = df[["commit_date", "commit_id", "filedir", "filename", "documentation_lines"]].copy()
df_docs["category"] = "documentation"
df_docs["line_count"] = df_docs["documentation_lines"]

df_long = pd.concat([df_code, df_docs], ignore_index=True)
# Continue with existing logic on df_long
```

**`chart_breakdown.py` (implemented):**

```python
# Old (long format)
df_modules = df_latest.groupby(["filedir", "filename"])["line_count"].sum()

# Implemented (wide format calculates total from components)
df_latest["line_count"] = (
    df_latest["docstring_lines"]
    + df_latest["comment_lines"]
    + df_latest["code_lines"]
)
df_files = df_latest.loc[:, ["filedir", "filename", "line_count"]].copy()

# Note: Functionally equivalent to using total_lines column from CSV
```

**Pros:**

- ✅ CSV matches `count_lines.py` structure (data integrity)
- ✅ Raw data preserved for future flexibility
- ✅ Derived columns provide convenience (`documentation_lines` available)
- ✅ Fewer CSV rows (1 per file instead of 2)
- ✅ Future charts can create different aggregations
- ✅ Sanity checking: `total_lines` verifies data integrity

**Cons:**

- ❌ Requires updating 3 files (`git_history.py`, both chart modules)
- ❌ Chart code slightly more complex (minimal)
- ❌ All existing CSV files need regeneration (acceptable per user)

---

## Decision 2: Blank Lines Treatment

### Option 2A: Keep Current (Exclude Blanks)

**Behavior:**

```python
classify_lines(content) → (docstring_lines, comment_lines, code_lines_excluding_blanks)
# Blanks tracked internally but not returned
```

**Verified example (horse.py):**

```text
Total: 39 lines
Docstrings: 10
Comments: 3
Code: 15 (actual executable code only)
Blanks: 11 (EXCLUDED)
Sum: 28 ≠ 39
```

**Pros:**

- ✅ More precise definition of "executable"
- ✅ Separates blank formatting from actual executable code

**Cons:**

- ❌ Counts don't add up to total (`sum ≠ total_lines`)
- ❌ More complex mental model
- ❌ Less aligned with common interpretation ("lines of code")
- ❌ Requires separate blank line tracking if needed

---

### Option 2B: Count Blanks as Executable (Proposed)

**Behavior:**

```python
classify_lines(content) → (docstring_lines, comment_lines, code_lines_including_blanks)
# Everything that isn't docstrings/comments = code
```

**Verified example (horse.py):**

```text
Total: 39 lines
Docstrings: 10
Comments: 3
Code: 26 (15 actual + 11 blanks)
Sum: 39 = 39 ✓
```

**Equation:**

```text
code_lines + documentation_lines = total_lines
26 + 13 = 39 ✓
```

**Implementation:**

```python
# count_lines.py (line 119-123)
# Old
return (
    classif.count("docstring"),
    classif.count("comment"),
    classif.count("executable"),  # Excludes blanks
)

# Implemented
return (
    classif.count("docstring"),
    classif.count("comment"),
    classif.count("executable") + classif.count("blank"),  # Includes blanks
)
```

**Mental model:**
> "If I remove all docstrings and comments from this file, what's left is code"

**Pros:**

- ✅ Simple equation: `code_lines + documentation_lines = total_lines`
- ✅ Intuitive interpretation: "lines of code in the file"
- ✅ Aligned with common usage: "this file has 100 lines of code"
- ✅ Counts add up cleanly (easier to verify)
- ✅ No need to track blanks separately

**Cons:**

- ❌ Includes blank lines in "code" count
- ❌ More sensitive to formatting style (ruff strict adds consistent blanks)
- ❌ Less precise definition of "actual code"

**Semantic consideration:**

- User's use case: distinguish "real code" from documentation
- Primary metric: src vs tests code volume (both include blanks equally)
- Blanks are part of code structure (function/class spacing)

---

## Combined Impact Matrix

| Decision 1 (CSV) | Decision 2 (Blanks) | CSV Total Lines | Equation | Status |
|-----------------|---------------------|-----------------|----------|----------------|
| Long (old) | Exclude (old) | 28 | ❌ sum ≠ total | Deprecated |
| Long | Include | 39 | ✓ sum = total | Not implemented |
| Wide | Exclude | 28 | ❌ sum ≠ total | Not implemented |
| Wide | Include | 39 | ✓ sum = total | ⭐ **Implemented** |

---

## Recommendation: Both Changes (1B + 2B)

**Implement both:**

- **Decision 1B:** Wide CSV with derived columns
- **Decision 2B:** Blanks counted as executable code

**Rationale:**

1. **Data integrity:** CSV matches source, counts add up
2. **Simplicity:** Clean equation, easier to explain
3. **Flexibility:** Raw data preserved, derived columns for convenience
4. **Alignment:** Matches user's mental model and use case
5. **Sanity checking:** `total_lines` column enables verification

**User's stated goal:**
> "Distinguish how many lines of *real* code was written, classified by tests/*.py and src/*.py"

- Both src and tests include blanks equally (fair comparison)
- Blank spacing is part of code structure (ruff enforces this)
- Primary metric is code vs documentation, not blanks vs non-blanks

---

## Implementation Checklist

### Files to Modify

**If implementing both 1B + 2B:**

1. **`src/plot_py_repo/count_lines.py`**
   - [x] Line 119-123: Include blanks in code_lines count
   - [x] Update docstring to reflect new behavior
   - [x] Function still returns 3-tuple (same signature)

2. **`src/plot_py_repo/git_history.py`**
   - [x] Line 95: Update CSV header to wide format
   - [x] Lines 145-156: Write 1 row per file with 5 columns
   - [x] Calculate `total_lines = len(content.splitlines())`
   - [x] Add sanity check: `assert doc + comm + code == total`

3. **`src/plot_py_repo/chart_evolution.py`**
   - [x] `_prepare_data()`: Uses `code_lines` and `documentation_lines` columns
   - [x] Works directly with wide format

4. **`src/plot_py_repo/chart_breakdown.py`**
   - [x] `_prepare_data()`: Uses `total_lines` column

5. **`tests/test_count_lines.py`**
   - [x] Update all assertions: code_lines count includes blanks
   - [x] `test_classify_lines_comprehensive`: Updated expected code_lines to 26
   - [x] All other tests: Recalculated expected code_lines counts

6. **`tests/test_git_history.py`**
   - [x] Update CSV parsing to match new column structure
   - [x] Tests for new wide format columns

7. **Documentation**
   - [x] Updated `CLAUDE.md` with CSV structure
   - [x] Updated architecture documentation

### Data Migration

**No backward compatibility needed (per user confirmation)**

- [ ] Delete existing `repo_history.csv` files
- [ ] Regenerate with `uv run plot-py-repo`
- [ ] Verify charts render correctly

### Validation Steps

1. [x] Run `uv run pytest tests/test_count_lines.py -v`
2. [x] Run `uv run pytest tests/test_git_history.py -v`
3. [x] Generate fresh CSV: `uv run plot-py-repo`
4. [x] Verify CSV structure: check header and sample rows
5. [x] Verify equation: `code_lines + documentation_lines == total_lines`
6. [x] Generate charts and verify visual output
7. [x] Run full test suite: `uv run pytest`

---

## ~~Alternative: Incremental Approach~~ (Not used)

~~If uncertain, implement in stages:~~

**~~Stage 1:~~** ~~Decision 2B only (blanks as code)~~

- ~~Simpler change (1 file: `count_lines.py`)~~
- ~~Clean equation immediately~~
- ~~CSV stays long format (easier migration)~~

**~~Stage 2:~~** ~~Decision 1B (flatten CSV)~~

- ~~Once confident in blank line treatment~~
- ~~Adds flexibility for future charts~~
- ~~Can be done independently~~

**Note:** Both changes implemented together as single refactor.

---

## Decision Criteria Summary

**✅ Implemented: 1B + 2B**

- ✅ Data integrity and clean equations
- ✅ Flexibility for future charts
- ✅ Updated 4 files successfully
- ✅ Simple mental model ("code_lines = non-doc/comment")

**~~Keep current (1A + 2A)~~** (Deprecated)

- ~~Current behavior meets all needs~~
- ~~You want to avoid any changes~~
- ~~Precise "actual code" definition matters more than simplicity~~

**~~Hybrid (1A + 2B)~~** (Not implemented)

- ~~You want clean equations but minimal code changes~~
- ~~Long format CSV is acceptable~~
- ~~Good stepping stone to full implementation~~

---

**✅ Completed:** All changes implemented and validated.

**Related Files:**

- `flatten_csv_perhaps.md` (earlier analysis)
- `tests/test_count_lines.py` (updated)
- `docs/architecture/arch-03.md` (architecture reference)
