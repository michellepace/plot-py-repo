Your task is to assess the feasibility of my idea:

<idea>
## Objective
Visualise this project repo so I can "tell a visual story" via two images (graphs created by Plotly Express) on my website blog.

## Graphs

### Graph 1: Stacked Area Chart (Evolution Over Time)
This chart visualises the growth and shrinkage of the Python application across Git commits. It employs a stacked area format with the x-axis representing commit timestamps (aggregated to daily or weekly intervals for clarity, if desired) and the y-axis indicating total non-blank line counts. The stacks consist of three layers: the bottom layer (e.g., dark green) for aggregated code lines from files in the `tests/` directory, the middle layer (e.g., dark blue) for aggregated code lines from files in the `src/` directory, and the top layer (e.g., light gray) for aggregated docstrings and comments across both directories. This design highlights trends, such as refactoring impacts, while excluding blank lines to focus on meaningful content. For instance, on a given date, it might display 2,000 test code lines, 1,000 source code lines, and 500 docstring/comment lines, totaling 3,500 non-blank lines.

### Graph 2: Vertical Bar Chart (Final Module Breakdown)
This chart presents a static view of the final (latest commit) line counts per Python module, sorted descending by total lines for emphasis on the largest contributors. It uses a vertical bar format with the y-axis listing module filenames (e.g., `tests/test_utils.py`, `src/main.py`) and the x-axis showing non-blank line counts per module, excluding blank lines. Bars are colored to distinguish categories: dark green for modules in the `tests/` directory and dark blue for those in the `src/` directory. Labels appear alongside each bar for readability, enabling quick identification of heavyweight modules without interactivity.

## DATA

### Required Data Source
All Git commits, scanning Python files in `src/` and `tests/` directories only.

### Required CSV Structure
To facilitate processing with Pandas and Plotly Express:

```text
datetime,commit_id,dir_group,filename,category,line_count
2025-10-01T12:00:00Z,abc123def456,src,cli.py,code,500
2025-10-01T12:00:00Z,abc123def456,src,cli.py,docstrings_comments,100
2025-10-01T12:00:00Z,abc123def456,tests,test_cli.py,code,30
```

This structure is complete and supports both graphs efficiently. It includes `datetime` and `commit_id` for temporal flexibility (e.g., daily or weekly aggregation for the stacked chart), `dir_group` for quick categorisation, `filename` for module-level granularity in the bar chart, `category` to separate code from docstrings/comments, and `line_count` for the actual metric.

### Existing Script To Count Lines

Proven script exists, needs modification for CSV output and Git. 

Currently:

```bash
~/projects/python/youtube-to-xml git:(main) ✗ 
$ uv run scripts/count_python_lines.py src/youtube_to_xml/file_parser.py
Actual code lines: 139
Docstring lines:    52
Comment lines:      22

line_count_code:                 139
line_count_docstrings_comments:   74
```

</idea>

Can you explain how we can use Git and modify the script to output as CSV?

Notes:
- all `.py` fiels are <700 lines
- this repo relatively speaking is small
