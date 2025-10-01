# Instructions for Creating Plotly Express Visualization Scripts

## Context
I have a UV-managed Python project with Git commit history logged to `my_repo_history.csv`. I need to create two Plotly Express graphs to visualize the evolution of my codebase.

## CSV Data Structure
```csv
datetime,commit_id,dir_group,filename,category,line_count
2025-09-28T15:18:49+02:00,7537888b6cc73e55cf04b41e8c53bfec9ba522a4,src,youtube_to_xml/cli.py,code,119
2025-09-28T15:18:49+02:00,7537888b6cc73e55cf04b41e8c53bfec9ba522a4,src,youtube_to_xml/cli.py,docstrings_comments,55
```

## Project Setup
- **Package Manager:** UV (never use pip/venv directly)
- **Python Version:** 3.13+
- **Dependencies Needed:**
  - `pandas` for data processing
  - `plotly` for visualization
  - `kaleido` for static image export (WebP/PNG/JPEG)
  - Install with: `uv add --dev pandas plotly kaleido`
  - **Note:** Kaleido requires Chrome/Chromium browser installed on system

## Task: Create Graph Scripts One-by-One

### Graph 1: Stacked Area Chart (Evolution Over Time)
**File:** `scripts/plot_evolution.py`

**Requirements:**
- Stacked area chart showing codebase growth over time
- **X-axis:** Date (one data point per day)
  - Aggregate all commits per day - take the LAST commit of each day as the snapshot
  - Extract date only from `datetime` column (ignore time)
- **Y-axis:** Total non-blank line counts
- **Stacks (bottom to top):**
  1. Muted blue (#41668c): Source code (`dir_group=src` + `category=code`)
  2. Muted purple (#4a366f): Test code (`dir_group=tests` + `category=code`)
  3. Medium gray (#8b8b8b): All docstrings/comments (`category=docstrings_comments` across both directories)
- **Aspect Ratio:** 16:9 (recommend 1600x900 pixels, scale=2 for retina)
- **Output:** Save as WebP image file for web embedding
- **Styling:**
  - Use clean template (e.g., `plotly_white` or `simple_white`)
  - Enable interactive tooltips showing exact line counts
  - Clear title and axis labels
  - Professional font and spacing

**Data Processing Notes:**
- **Filter out `__init__.py` files** - Exclude rows where `filename` is `__init__.py` (minimal lines, creates noise)
- Extract date only from `datetime` column (e.g., "2025-09-28")
- For days with multiple commits, take the LAST commit (most recent timestamp) as the daily snapshot
- Group by date and category, sum `line_count` for each category
- Result: One data point per day showing repository state at end of that day
- Your repo spans ~8 weeks (Aug 6 - Sept 30), so expect ~42 daily data points

### Graph 2: Horizontal Bar Chart (Final Module Breakdown)
**File:** `scripts/plot_modules.py`

**Requirements:**
- Static view of latest commit only (most recent `datetime`)
- Horizontal bar chart of line counts per module
- **Y-axis:** Module filenames (e.g., `tests/test_cli.py`, `src/youtube_to_xml/cli.py`)
  - Sort descending by total lines (largest modules at top)
- **X-axis:** Non-blank line counts per module
- **Colors:**
  - Muted blue (#41668c): `dir_group=src`
  - Muted purple (#4a366f): `dir_group=tests`
- **Bars:** Show total lines per module (sum `code` + `docstrings_comments`)
- **Labels:** Display count values on/near bars
- **Aspect Ratio:** 16:9 (1600x900 pixels, scale=2)
- **Output:** Save as WebP image file
- **Styling:**
  - Clean template matching Graph 1
  - Readable module names on y-axis
  - Clear title

**Data Processing Notes:**
- **Filter out `__init__.py` files** - Exclude rows where `filename` is `__init__.py` (minimal lines, creates noise)
- Filter to latest `datetime` only
- Group by `filename` and sum `line_count` across both categories
- Concatenate `dir_group` + `/` + `filename` for full path display

## Implementation Approach
**Please implement Graph 1 first.** Once working, I'll ask you to implement Graph 2.

For each graph script:
1. Use pandas to load `my_repo_history.csv`
2. Process data according to requirements above
3. Create Plotly Express figure with specified styling
4. Apply clean template (e.g., `template="plotly_white"`)
5. Set dimensions to 16:9 ratio (1600x900 pixels)
6. Export to WebP using: `fig.write_image("output.webp", width=1600, height=900, scale=2)`
7. Include proper titles, axis labels, and legend
8. Print confirmation with file path when saved

**WebP Export Example:**
```python
import plotly.express as px

fig = px.area(df, x='datetime', y='line_count', color='category')
fig.update_layout(template='plotly_white', title='My Chart')
fig.write_image("evolution.webp", width=1600, height=900, scale=2)
```

## Code Quality Requirements
- Follow project's TDD principles (write tests if complex logic)
- Use pure functions where possible
- Type hints required
- Use `pathlib` not `os`
- Follow ruff/pyright standards (see `pyproject.toml`)

## Output Format
Each script should:
- Be runnable via: `uv run scripts/plot_evolution.py`
- Accept optional CLI args (e.g., output path, aggregation level)
- Print confirmation when HTML saved
- Include docstring explaining what it does

## Styling Best Practices (Applied)

Based on Plotly research:
- ✅ **Plotly Express preferred** - Cleaner code than graph_objects
- ✅ **3 categories** - Optimal (research says 3-5 max)
- ✅ **Clean templates** - `plotly_white` or `simple_white` for professional look
- ✅ **16:9 aspect ratio** - Standard for web embedding
- ✅ **Informative titles** - Essential for blog posts
- ✅ **High resolution** - `scale=2` for retina displays

**Note on Stacked Area Charts:**
- Best for showing "part-to-whole" trends over time ✅
- Bottom layer (test code) easiest to read precisely
- Middle/top layers harder to compare (no shared baseline)
- Consider adding tooltips for exact values

---

## Start Command
Please create `scripts/plot_evolution.py` first using the requirements above. Use pandas and plotly express. Generate a stacked area chart showing the evolution of my codebase over Git commits, and export it as a WebP image (1600x900, scale=2) with clean styling.
