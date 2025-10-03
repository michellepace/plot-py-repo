# ARCHITECTURE 2 (CURRENT)

```
cli.py
  │
  │ (arg parsing: repo_path, --csv, --output-dir)
  │
  ├──> git_history.py (if no --csv)
  │      │
  │      ├─ get_commits(repo_path) → list[(commit_hash, timestamp)]
  │      │    • subprocess: git log --format=%H %ct
  │      │    • Returns commits newest first
  │      │
  │      └─ generate_csv(repo_path, output_dir) → csv_path
  │           │
  │           └─ for each commit:
  │                ├─ subprocess: git ls-tree (get Python files)
  │                └─ for each file:
  │                     ├─ subprocess: git show commit:file
  │                     ├─ classify_lines(content) → (doc, comm, code)
  │                     └─ write CSV rows (2 per file: code, docstrings_comments)
  │
  └──> visualise.py
         │
         └─ create_images(csv_path, output_dir)
              │
              ├─ pd.read_csv(csv_path) → df
              ├─ filter out __init__.py → filtered_df
              │
              ├──> _plot_evolution(filtered_df, path)
              │      │ • Extract dates from commit_date column
              │      │ • Group by date (keep last commit per day)
              │      │ • Aggregate into 3 categories:
              │      │     - Source Code (src + code)
              │      │     - Test Code (tests + code)
              │      │     - Docstrings/Comments (all docstrings_comments)
              │      │ • Create stacked area chart
              │      │ • Hardcoded colors: {"Source Code": "#41668c", ...}
              │      │ • Hardcoded layout: width=1600, height=900, template="plotly_white"
              │      └─ fig.write_image(path)
              │
              └──> _plot_modules(filtered_df, path)
                     │ • Filter to latest commit (max commit_date)
                     │ • Group by filedir + filename, sum line_count
                     │ • Create module path display
                     │ • Sort by line count ascending
                     │ • Create horizontal bar chart
                     │ • Hardcoded colors: {"src": "#41668c", "tests": "#4a366f"}
                     │ • Hardcoded layout: width=1600, height=900, template="plotly_white"
                     └─ fig.write_image(path)

count_lines.py (PURE UTILITY - no I/O)
  │
  └─ classify_lines(content: str) → (docstring_count, comment_count, code_count)
       │
       ├─ _extract_docstring_lines(content) → set[line_numbers]
       │    • Uses AST to find docstrings in modules/functions/classes
       │
       ├─ _tokenize_content(content) → list[tokens]
       │    • Tokenizes Python content
       │
       ├─ _mark_code_lines(tokens, classif)
       │    • Marks lines with non-structural tokens as code
       │
       ├─ _mark_comment_lines(tokens, classif)
       │    • Marks lines with comment tokens as comments
       │
       └─ Returns counts of each category
```

## KEY CHARACTERISTICS

**Monolithic Visualisation:**
- Single `visualise.py` file with two internal plotting functions
- Each function independently handles data preparation AND plotting
- Colors and layouts hardcoded in each function (DUPLICATED)
- No shared theming or configuration

**CSV Generation:**
- Git history traversal in `git_history.py`
- Calls pure utility `classify_lines()` from `count_lines.py`
- Writes CSV with 2 rows per file per commit (code, docstrings_comments)

**Current Limitations:**
- Adding new chart types requires editing `visualise.py` directly
- Color scheme and layout settings duplicated across functions
- No clear separation between data prep and plotting logic
- Difficult to maintain consistent theming across charts
