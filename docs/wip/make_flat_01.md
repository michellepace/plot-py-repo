# CSV Structure Decision: Flatten to Match `count_lines.py` Tuple?

**Status:** Deferred decision - documented for future consideration

**Context:** During test refactoring of `test_count_lines.py`, we identified a data structure mismatch between `count_lines.py` output and the CSV file structure.

---

## Current State

### `count_lines.py` Output (source of truth)

```python
classify_lines(content) -> tuple[int, int, int]
# Returns: (docstring_lines, comment_lines, code_lines)
```

**Example:** `(10, 3, 15)` means 10 docstrings, 3 comments, 15 code lines

### Current CSV Structure (long/pivoted format)

```csv
commit_date,commit_id,filedir,filename,category,line_count
2025-09-30...,83036f2,src,cli.py,code,120
2025-09-30...,83036f2,src,cli.py,docstrings_comments,51
```

**Key observation:** Docstrings and comments are **pre-aggregated** in `git_history.py:146`:

```python
doc_lines, comm_lines, code_lines = classify_lines(content)
doc_comm_lines = doc_lines + comm_lines  # ← TRANSFORMATION HAPPENS HERE
```

---

## Proposed Refactoring: Option 1 (Flatten CSV)

### New CSV Structure (wide format, matches tuple)

```csv
commit_date,commit_id,filedir,filename,docstring_lines,comment_lines,code_lines
2025-09-30...,83036f2,src,cli.py,40,11,120
```

**Changes required:**

1. **`git_history.py`** - Write 3 columns instead of 2 rows per file
2. **`chart_evolution.py`** - Add aggregation in `_prepare_data()`:

   ```python
   df["docstrings_comments"] = df["docstring_lines"] + df["comment_lines"]
   ```

3. **`chart_breakdown.py`** - Sum all 3 columns:

   ```python
   df["total_lines"] = df["docstring_lines"] + df["comment_lines"] + df["code_lines"]
   ```

### Advantages

✅ **Data integrity:** CSV matches source data structure exactly
✅ **Flexibility:** Future charts can choose how to aggregate categories
✅ **Transparency:** Raw data preserved; transformations happen at point of use
✅ **Extensibility:** New charts can create different category groupings
✅ **Simpler CSV:** One row per file (instead of 2), fewer total rows

### Disadvantages

❌ **Migration:** Need to regenerate all existing CSV files
❌ **Chart complexity:** Each chart module must aggregate (but follows architecture pattern)
❌ **Breaking change:** External tools reading current CSV would break

---

## Alternative: Option 2 (Keep Current Structure)

### Keep existing long format with pre-aggregated categories

**Rationale for current design:**

- Optimized for `chart_evolution.py` - the primary visualization
- Follows "tidy data" principles (one observation per row)
- Already works and is battle-tested

**Disadvantage:**

- Permanent loss of granularity - can never separate docstrings from comments
- Future charts limited to existing category split

---

## Chart Module Impact Analysis

### Current Chart Needs

**`chart_evolution.py` (lines 42-48):**

```python
# Uses df["category"] expecting "code" and "docstrings_comments"
conditions = [
    (df["filedir"] == "src") & (df["category"] == "code"),
    (df["filedir"] == "tests") & (df["category"] == "code"),
    df["category"] == "docstrings_comments",  # ← Combined category
]
```

**Impact:** Would need to add one aggregation line: `df["docstrings_comments"] = ...`

**`chart_breakdown.py` (line 30):**

```python
# Just sums line_count across ALL categories - doesn't care about split
df_modules = df_latest.groupby(["filedir", "filename"])["line_count"].sum()
```

**Impact:** Would change to: `df["total_lines"] = df[["docstring_lines", "comment_lines", "code_lines"]].sum(axis=1)`

### Future Chart Extensibility

Following the architecture pattern (`arch-03.md`), new charts would:

**Option 1 (flattened CSV):**

```python
def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    # Chart decides how to aggregate
    df["docs_and_comments"] = df["docstring_lines"] + df["comment_lines"]
    # OR create different groupings
    df["non_code"] = df["docstring_lines"] + df["comment_lines"]
    df["executable"] = df["code_lines"]
```

**Option 2 (current):**

```python
def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    # Stuck with pre-defined categories
    # Cannot separate docstrings from comments if needed
```

---

## Recommendation

**Lean toward Option 1** (flatten CSV) if:

- We anticipate needing separate docstring/comment metrics in future charts
- We value data preservation over pre-optimization
- We're willing to accept one-time migration cost

**Keep Option 2** (current) if:

- Current charts meet all foreseeable needs
- We prioritize stability and avoiding breaking changes
- The combined "docstrings_comments" category is semantically meaningful

---

## Decision Criteria

Before implementing Option 1, answer:

1. **Do we foresee charts that need to distinguish docstrings from comments?**
   - Example: "Documentation coverage" chart (docstrings only)
   - Example: "Comment density" analysis

2. **Is the CSV format part of a public API?**
   - Do external tools depend on current structure?
   - Can we version the CSV format?

3. **What's the migration path?**
   - How many existing CSV files need regeneration?
   - Do we support both formats during transition?

---

## Next Steps (When Resuming This Decision)

1. Review all existing charts and identify category usage patterns
2. Survey potential future visualizations and their data needs
3. Check if any external tools/scripts parse the current CSV
4. Create migration plan if choosing Option 1
5. Write tests for CSV structure (currently untested)

---

**Document created:** 2025-10-04
**Related work:** `test_count_lines.py` refactoring
**Architecture reference:** `docs/architecture/arch-03.md`
