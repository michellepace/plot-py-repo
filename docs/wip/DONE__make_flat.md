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
# Returns: (docstring_lines, comment_lines, executable_lines)
```

**Internal processing:**

```python
classif = ["pending", "docstring", "executable", "comment", "blank", ...]
# Lines classified as "blank" are NOT included in return tuple
```

**Verified with `horse.py` (39 total lines):**

```python
classify_lines(horse_content) → (10, 3, 15)
# 10 docstrings + 3 comments + 15 executable = 28 lines counted
# 39 - 28 = 11 blank lines EXCLUDED
```

### Current CSV Structure (`git_history.py`)

**Format:** Long/pivoted (2 rows per file)

**Header:**

```csv
commit_date,commit_id,filedir,filename,category,line_count
```

**Example rows:**

```csv
2025-09-30 23:47:26 +0200,83036f2,src,cli.py,executable,15
2025-09-30 23:47:26 +0200,83036f2,src,cli.py,documentation,13
```

**Aggregation logic (git_history.py:145-146):**

```python
docstring_lines, comment_lines, executable_lines = classify_lines(content)
documentation_lines = docstring_lines + comment_lines  # ← Pre-aggregation
```

### Current Chart Requirements

**`chart_evolution.py`** - Stacked area chart over time

- Uses `df["category"] == "executable"` (split by src/tests)
- Uses `df["category"] == "documentation"`
- Maps to 3 display categories: "Source Code", "Test Code", "Documentation"

**`chart_breakdown.py`** - Horizontal bar by file

- Sums ALL categories: `groupby(["filedir", "filename"])["line_count"].sum()`
- Doesn't care about category split

---

## Decision 1: CSV Structure

### Option 1A: Keep Current (Long Format, Pre-aggregated)

**Structure:**

```csv
commit_date,commit_id,filedir,filename,category,line_count
2025-09-30...,83036f2,src,cli.py,executable,15
2025-09-30...,83036f2,src,cli.py,documentation,13
```

**Characteristics:**

- 2 rows per file
- Categories: `executable`, `documentation`
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
commit_date,commit_id,filedir,filename,docstring_lines,comment_lines,executable_lines,documentation_lines,total_lines
2025-09-30...,83036f2,src,cli.py,10,3,15,13,28
```

**Characteristics:**

- 1 row per file (50% fewer rows)
- Raw counts preserved: `docstring_lines, comment_lines, executable_lines`
- Derived columns for convenience: `documentation_lines, total_lines`

**Implementation changes:**

**`git_history.py` (lines 145-156):**

```python
# Current
docstring_lines, comment_lines, executable_lines = classify_lines(content)
documentation_lines = docstring_lines + comment_lines
f.write(f"...executable,{executable_lines}\n")
f.write(f"...documentation,{documentation_lines}\n")

# Proposed
docstring_lines, comment_lines, executable_lines = classify_lines(content)
total_lines = len(content.splitlines())
documentation_lines = docstring_lines + comment_lines
f.write(f"...{docstring_lines},{comment_lines},{executable_lines},{documentation_lines},{total_lines}\n")
```

**`chart_evolution.py` (_prepare_data, add one line):**

```python
def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # NEW: Create aggregated column from raw columns
    df["category"] = "executable"  # Default
    df.loc[df["documentation_lines"] > 0, "category"] = "documentation"
    df["line_count"] = df["executable_lines"]
    df.loc[df["category"] == "documentation", "line_count"] = df["documentation_lines"]

    # Rest of existing logic unchanged...
```

**Alternative simpler approach for chart_evolution:**

```python
# Create long-format subset from wide format
df_exec = df[["commit_date", "commit_id", "filedir", "filename", "executable_lines"]].copy()
df_exec["category"] = "executable"
df_exec["line_count"] = df_exec["executable_lines"]

df_docs = df[["commit_date", "commit_id", "filedir", "filename", "documentation_lines"]].copy()
df_docs["category"] = "documentation"
df_docs["line_count"] = df_docs["documentation_lines"]

df_long = pd.concat([df_exec, df_docs], ignore_index=True)
# Continue with existing logic on df_long
```

**`chart_breakdown.py` (minimal change):**

```python
# Current
df_modules = df_latest.groupby(["filedir", "filename"])["line_count"].sum()

# Proposed
df_latest["total_lines"] = (
    df_latest["docstring_lines"] +
    df_latest["comment_lines"] +
    df_latest["executable_lines"]
)
df_modules = df_latest.groupby(["filedir", "filename"])["total_lines"].sum()
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
classify_lines(content) → (docstring_lines, comment_lines, executable_lines_excluding_blanks)
# Blanks tracked internally but not returned
```

**Verified example (horse.py):**

```text
Total: 39 lines
Docstrings: 10
Comments: 3
Executable: 15 (actual executable code only)
Blanks: 11 (EXCLUDED)
Sum: 28 ≠ 39
```

**Pros:**

- ✅ More precise definition of "executable"
- ✅ Separates blank formatting from actual executable code

**Cons:**

- ❌ Counts don't add up to total (`sum ≠ total_lines`)
- ❌ More complex mental model
- ❌ Less aligned with common interpretation ("lines of executable code")
- ❌ Requires separate blank line tracking if needed

---

### Option 2B: Count Blanks as Executable (Proposed)

**Behavior:**

```python
classify_lines(content) → (docstring_lines, comment_lines, executable_lines_including_blanks)
# Everything that isn't docstrings/comments = executable
```

**Verified example (horse.py):**

```text
Total: 39 lines
Docstrings: 10
Comments: 3
Executable: 26 (15 actual + 11 blanks)
Sum: 39 = 39 ✓
```

**Equation:**

```text
executable_lines + documentation_lines = total_lines
26 + 13 = 39 ✓
```

**Implementation:**

```python
# count_lines.py (line 119-123)
# Current
return (
    classif.count("docstring"),
    classif.count("comment"),
    classif.count("executable"),  # Excludes blanks
)

# Proposed
return (
    classif.count("docstring"),
    classif.count("comment"),
    classif.count("executable") + classif.count("blank"),  # Includes blanks
)
```

**Mental model:**
> "If I remove all docstrings and comments from this file, what's left is executable code"

**Pros:**

- ✅ Simple equation: `executable + documentation = total`
- ✅ Intuitive interpretation: "lines of executable code in the file"
- ✅ Aligned with common usage: "this file has 100 lines of executable code"
- ✅ Counts add up cleanly (easier to verify)
- ✅ No need to track blanks separately

**Cons:**

- ❌ Includes blank lines in "executable" count
- ❌ More sensitive to formatting style (ruff strict adds consistent blanks)
- ❌ Less precise definition of "actual executable code"

**Semantic consideration:**

- User's use case: distinguish "real executable code" from documentation
- Primary metric: src vs tests code volume (both include blanks equally)
- Blanks are part of executable code structure (function/class spacing)

---

## Combined Impact Matrix

| Decision 1 (CSV) | Decision 2 (Blanks) | CSV Total Lines | Equation | Recommendation |
|-----------------|---------------------|-----------------|----------|----------------|
| Long (current) | Exclude (current) | 28 | ❌ sum ≠ total | Status quo |
| Long | Include | 39 | ✓ sum = total | Partial fix |
| Wide | Exclude | 28 | ❌ sum ≠ total | Inconsistent |
| Wide | Include | 39 | ✓ sum = total | ⭐ **Recommended** |

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
> "Distinguish how many lines of *real* executable code was written, classified by tests/*.py and src/*.py"

- Both src and tests will include blanks equally (fair comparison)
- Blank spacing is part of executable code structure (ruff enforces this)
- Primary metric is executable vs documentation, not blanks vs non-blanks

---

## Implementation Checklist

### Files to Modify

**If implementing both 1B + 2B:**

1. **`src/plot_py_repo/count_lines.py`**
   - [ ] Line 119-123: Include blanks in executable count
   - [ ] Update docstring to reflect new behavior
   - [ ] Function still returns 3-tuple (same signature)

2. **`src/plot_py_repo/git_history.py`**
   - [ ] Line 95: Update CSV header to wide format
   - [ ] Lines 145-156: Write 1 row per file with 5 columns
   - [ ] Calculate `total_lines = len(content.splitlines())`
   - [ ] Add sanity check: `assert doc + comm + executable == total`

3. **`src/plot_py_repo/chart_evolution.py`**
   - [ ] `_prepare_data()`: Create `category` and `line_count` from raw columns
   - [ ] OR: Pivot wide → long format at start of function

4. **`src/plot_py_repo/chart_breakdown.py`**
   - [ ] `_prepare_data()`: Use `total_lines` column or sum 3 columns

5. **`tests/test_count_lines.py`**
   - [ ] Update all assertions: executable count increases by blank count
   - [ ] `test_classify_lines_comprehensive`: Update expected executable from 15 to 26
   - [ ] All other tests: Recalculate expected executable counts

6. **`tests/test_git_history.py`**
   - [ ] Update CSV parsing to match new column structure
   - [ ] May need to add tests for new columns

7. **Documentation**
   - [ ] Update `CLAUDE.md` if CSV structure is documented
   - [ ] Update `docs/architecture/arch-03.md` if data flow described

### Data Migration

**No backward compatibility needed (per user confirmation)**

- [ ] Delete existing `repo_history.csv` files
- [ ] Regenerate with `uv run plot-py-repo`
- [ ] Verify charts render correctly

### Validation Steps

1. [ ] Run `uv run pytest tests/test_count_lines.py -v`
2. [ ] Run `uv run pytest tests/test_git_history.py -v`
3. [ ] Generate fresh CSV: `uv run plot-py-repo`
4. [ ] Verify CSV structure: check header and sample rows
5. [ ] Verify equation: `executable_lines + documentation_lines == total_lines`
6. [ ] Generate charts and verify visual output
7. [ ] Run full test suite: `uv run pytest`

---

## Alternative: Incremental Approach

If uncertain, implement in stages:

**Stage 1:** Decision 2B only (blanks as executable)

- Simpler change (1 file: `count_lines.py`)
- Clean equation immediately
- CSV stays long format (easier migration)

**Stage 2:** Decision 1B (flatten CSV)

- Once confident in blank line treatment
- Adds flexibility for future charts
- Can be done independently

---

## Decision Criteria Summary

**Choose 1B + 2B if:**

- You value data integrity and clean equations
- You want flexibility for future charts
- You're willing to update 3-4 files
- Simple mental model matters ("executable = non-doc/comment")

**Keep current (1A + 2A) if:**

- Current behavior meets all needs
- You want to avoid any changes
- Precise "actual executable code" definition matters more than simplicity

**Hybrid (1A + 2B) if:**

- You want clean equations but minimal code changes
- Long format CSV is acceptable
- Good stepping stone to full implementation

---

**Next Steps:** Review this document, make decision, then update `test_count_lines.py` accordingly.

**Related Files:**

- `flatten_csv_perhaps.md` (earlier analysis)
- `tests/test_count_lines.py` (needs updating after decision)
- `docs/architecture/arch-03.md` (architecture reference)
