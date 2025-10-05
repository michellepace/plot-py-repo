# ARCHITECTURE 1 (INITIAL COMMIT)

```text
cli.py (MULTI-COMMAND INTERFACE)
  │
  ├─ count-lines <file>
  │    └──> cmd_count_lines()
  │           └─ classify_lines(content) → print results
  │
  ├─ generate-csv [repo_path] [--output FILE]
  │    └──> cmd_generate_csv()
  │           └─ generate_csv(repo_path, output_path)
  │
  ├─ plot-evolution <csv>
  │    └──> cmd_plot_evolution()
  │           └─ print "Not yet implemented"
  │
  └─ plot-modules <csv>
       └──> cmd_plot_modules()
              └─ print "Not yet implemented"

git_history.py
  │
  ├─ get_commits(repo_path) → list[(commit_hash, timestamp)]
  │    • subprocess: git log --format=%H %ct
  │    • Returns commits newest first
  │
  └─ generate_csv(repo_path, output_path) → None
       │
       └─ for each commit:
            ├─ subprocess: git ls-tree (get Python files)
            └─ for each file:
                 ├─ subprocess: git show commit:file
                 ├─ classify_lines(content) → (doc, comm, code)
                 └─ write CSV rows (2 per file: code, docstrings_comments)

count_lines.py (PURE UTILITY - no I/O)
  │
  └─ classify_lines(content: str) → (docstring_count, comment_count, code_count)
       │
       ├─ _extract_docstring_lines(content) → set[line_numbers]
       ├─ _tokenize_content(content) → list[tokens]
       ├─ _mark_code_lines(tokens, classif)
       ├─ _mark_comment_lines(tokens, classif)
       └─ Returns counts of each category

plot_evolution.py (STUB)
  │
  └─ plot_evolution(csv_path, output_path) → NotImplementedError

plot_modules.py (STUB)
  │
  └─ plot_modules(csv_path, output_path) → NotImplementedError
```

## KEY CHARACTERISTICS

**Multi-Command CLI:**

- Four separate subcommands: count-lines, generate-csv, plot-evolution, plot-modules
- User manually chains commands together
- Workflow: `generate-csv` → `plot-evolution` → `plot-modules` (3 separate invocations)

**Separate Chart Modules (Planned):**

- `plot_evolution.py` and `plot_modules.py` existed as separate files
- Both were stubs with NotImplementedError
- Shows intent for modular chart design (similar to a3.md future)

**Utility Command:**

- `count-lines` subcommand for analyzing individual files
- Exposed `classify_lines()` functionality directly to users

**CSV Generation:**

- Same implementation as current (a2.md)
- CSV columns: datetime, commit_id, dir_group, filename, category, line_count

**Package Name:**

- Original name: `viz-python-repo` (later renamed to `plot-py-repo`)
