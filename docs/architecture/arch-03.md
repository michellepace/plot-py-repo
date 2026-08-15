# ARCHITECTURE 3 - Complete and Accurate Against Codebase as of `2025-10-05`

Eight modules, one direction of travel. Git history becomes a CSV, the CSV becomes a
DataFrame, the DataFrame becomes three WebP charts. Nothing flows backwards.

## 🔄 DATA FLOW

```text
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │    Git repo     │     │  repo_history   │     │    DataFrame    │     │   3 × .webp     │
  │                 │────▶│      .csv       │────▶│                │────▶│                │
  │  every commit   │     │  1 row per file │     │  __init__.py    │     │  1400 × 1000 px │
  │  in history     │     │  per commit     │     │  rows dropped   │     │                 │
  └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
     git ls-tree             10 columns              pandas.read_csv         plotly.express
     git show                UTF-8 text              typed on load           kaleido, scale=2
     ast + tokenize

  ╰──────────── git_history.py ─────────────╯     ╰─────── visualise.py + chart_*.py ───────╯
                count_lines.py                                  theme_plotly.py
```

The CSV is the seam. Everything left of it is Git and text parsing; everything right of it
is pandas and Plotly. That split is why `--csv` can replay the second half alone, and why
chart work never waits on a full history walk.

### The CSV contract

| Column | Meaning |
| --- | --- |
| `repo_name` | Resolved directory name of the analysed repo |
| `commit_date` | Git author date, `YYYY-MM-DD HH:MM:SS +ZZZZ` |
| `commit_id` | Short commit hash |
| `filedir` | `src` or `tests` — the only two trees walked |
| `filename` | Basename only, path discarded |
| `code_lines` | Everything not a docstring or standalone comment, blanks included |
| `docstring_lines` | Module, class, and function docstrings, via AST |
| `comment_lines` | Standalone `#` comments only, via tokeniser |
| `total_lines` | As counted in an IDE |
| `documentation_lines` | `docstring_lines + comment_lines`, precomputed for charting |

Two invariants hold on every row, and the charts rely on both:

```text
  code_lines + docstring_lines + comment_lines  ==  total_lines
  docstring_lines + comment_lines               ==  documentation_lines
```

They hold because every line is classified exactly once: AST claims docstring lines first,
the tokeniser claims standalone comments next, and everything still unclaimed — including
blank lines — falls through to code.

## ⚙️ EXECUTION FLOW

```text
  cli.main()
   │  argparse:  repo_path (default ".")  ·  --csv FILE  ·  --output-dir DIR
   │  guard:     repo_path and --csv are mutually exclusive
   │
   ├── ① Git analysis ─ skipped entirely when --csv is given
   │    │
   │    └─ git_history.generate_csv(repo_path, output_dir) ─▶ csv_path
   │         ├─ get_commits()          git log --format=%h %ai
   │         ├─ files per commit       git ls-tree -r --name-only <sha> src/ tests/
   │         ├─ content per file       git show <sha>:<path>
   │         ├─ counts per file        count_lines.classify_lines(content)
   │         └─ append one CSV row per file per commit
   │
   └── ② Visualisation ─ runs in both modes
        │
        └─ visualise.create_charts(csv_path, output_dir)
             ├─ _load_csv()             pandas.read_csv with explicit dtypes
             ├─ _exclude_filenames()    drops __init__.py rows
             │
             ├─▶ chart_evolution.create()         ─▶ repo_evolution.webp
             ├─▶ chart_evolution_commit.create()  ─▶ repo_evolution_commit.webp
             └─▶ chart_breakdown.create()         ─▶ repo_breakdown.webp
```

`visualise.py` orchestrates and holds no chart logic — it loads, filters, and delegates to
three interchangeable chart modules that share `theme_plotly.py` for a common look.
Adding a fourth chart touches it in exactly one place.

## 📐 DESIGN RULES IN FORCE

- **One module, one purpose** — a module walks Git, counts lines, orchestrates, draws one
  chart, or themes. Never two.
- **Pure where it counts** — `count_lines.classify_lines()` is string in, three integers
  out. It is the most-tested module (20 of 59 tests) precisely because it is pure.
- **No Git library** — history is read with `git ls-tree` and `git show` subprocess calls,
  so there is no dependency to keep current.
- **Fail loudly, skip quietly** — a missing repo or unreadable CSV exits with a message;
  an individual unreadable commit or file is skipped so one bad blob cannot end a run.

**Known deviation:** the project rule is to handle errors at the CLI boundary, but
`git_history.generate_csv()` and `visualise._load_csv()` both print and `sys.exit(1)`
directly. Consolidating those into `cli.py` is the outstanding cleanup.
