# Rough UX Improvement Ideas

These are **rough ideas** to improve user experience.

- Shared footer in `<visual_chart_enhancement_shared_footer>` tags  - ✅ DONE
- A new chart in `<new_chart>` tags - ✅ DONE
- Better error handling for CLI experience in `<improve_cli_user_experience>` tags - ✅ DONE

<ideas>

<visual_chart_enhancement_shared_footer>

✅ **DONE**

<requirements>

## Evolution Chart

- ✅ Title: "Repository Growth Over Time"
- ✅ Legend: ["Test Code", "Source Code", "Code Comments"]
- Footer: [Repo <REPO_NAME> · <LATEST_COMMIT_DATE> · all lines counted (as in your IDE)] # Standardised in `theme.py`

## Breakdown Chart

- ✅ Title: "Repository Breakdown by File"
- ✅ Legend: ["tests", "src"]  # Already clear
- Footer: [Repo <REPO_NAME> · <LATEST_COMMIT_DATE> · all lines counted (as in your IDE)] # Standardised in `theme.py`

## Positioning of Footer

The footer should be positioning should be "dynamic" in that if I were to change the default figure width and height that it would still be positioned at an offset from the left and bottom of the page. I am open to how this is best implemented as I do not know Plotly Express specifics or indeed theming.

I have curated Plotly Express documentation in `docs/reference/plotly_theming.md` which may be of assistance. Else, please research how to elegantly do this.

## Test Driven Development

A lightweight testing model exists to prevent accidental regression `tests/test_theme.py`. You must consider if it will be of benefit to write a non-brittle test for the footer. Please advise.

</requirements>

<implement>
## Add footer annotation to both charts

Complexity: Medium (need to extract repo name + latest date)

Files to modify:

- Possibly `src/plot_py_repo/theme.py` (Add `add_footer()` to `theme.py` )
- `src/plot_py_repo/chart_evolution.py` (Will footer be automatic unless overridden, do we have to call `add_footer()`?)
- `src/plot_py_repo/chart_breakdown.py` (Will footer be automatic unless overridden, do we have to call `add_footer()`?)

Data needed:

- Repository name (we should add this as the first column in the generated CSV, `repo_name`)
- Latest commit date (already available: `df["commit_date"].max()`)

Format:

```python
footer_text = f"{repo_name} · {latest_date} · all lines counted (as in IDE)"
```

Styling:

- Position: x=0.01, y=-0.1 (bottom-left, outside plot area)
- Font: 9pt
- Colour: #888888 [later: if possible refactor for subtle colour defined by plotly theme so we can easily theme switch]

</implement>

</visual_chart_enhancement_shared_footer>

<improve_cli_user_experience>

✅ **DONE**

## CLI User Experience on Insensical inputs**

   1. ✅ `uv run plot-py-repo --csv does_not_exist.csv` - Shows: `❌  CSV file not found: does_not_exist.csv`
   2. ✅ `uv run plot-py-repo repo-does-not-exist` - Shows: `❌  Directory not found so we couldn't look for Git repo`
   3. ✅ `uv run plot-py-repo repo-does-not-have-git` - Shows: `❌  Not a Git repository`
   4. ✅ `uv run plot-py-repo repo-does-not-have-a-python-file` - Shows: `❌  No Python files found in src/ or tests/ directories`
   5. ✅ `uv run plot-py-repo repo-does-not-have-at-least-one-of-src-or-tests-directory` - Shows: `❌  No Python files found in src/ or tests/ directories`

**Implementation:**

- Fixed scenarios 1-2 (were showing stack traces)
- Verified scenarios 3-5 (already had clean error handling)
- Added 2 TDD tests: `test_nonexistent_repo_shows_clean_error()`, `test_nonexistent_csv_shows_clean_error()`
- Error handling at I/O boundaries (`git_history.py`, `visualise.py`)
- All 5 scenarios now show clean `❌` messages with no stack traces

</improve_cli_user_experience>

<new_chart>

✅ **DONE**

Branch: "feature/chart-evolution-commit"

> Create a new chart module `chart_commit_evolution.py` following the established pattern in `chart_evolution.py`. Generate a stacked bar chart with commit index (1, 2, 3...) on the x-axis instead of dates. Follow TDD.

</new_chart>

</ideas>
