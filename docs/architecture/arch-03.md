# ARCHITECTURE 3 (target)

```
cli.py
  │
  │ (arg parsing: repo_path, --csv, --output-dir)
  │
  └──> visualise.py (ORCHESTRATOR)
         │
         ├─ load_and_filter(csv_path) → DataFrame
         │    • Read CSV once
         │    • Apply common filters (remove __init__.py)
         │    • Return clean DataFrame
         │
         └─ create_images(df, output_dir)
               │
               ├──> chart_evolution.py
               │      │ from . import theme  ← imports theme
               │      └─ create(df, output_path)
               │           ├─ _prepare_data(df) → df_prepared
               │           │    • Extract dates
               │           │    • Group by date
               │           │    • Aggregate categories
               │           └─ _plot_and_save(df_prepared, path)
               │                • Uses theme.apply_common_layout()
               │
               ├──> chart_modules.py
               │      │ from . import theme  ← imports theme
               │      └─ create(df, output_path)
               │           ├─ _prepare_data(df) → df_prepared
               │           │    • Filter to latest commit
               │           │    • Group by module
               │           │    • Sort by line count
               │           └─ _plot_and_save(df_prepared, path)
               │                • Uses theme.apply_common_layout()
               │
               └──> chart_complexity.py (future)
                      │ from . import theme  ← imports theme
                      └─ create(df, output_path)
                           ├─ _prepare_data(df) → df_prepared
                           └─ _plot_and_save(df_prepared, path)
                                • Uses theme.apply_common_layout()

theme.py (CENTRALIZED THEMING)
  • DEFAULT_LAYOUT: width, height, template
  • apply_common_layout(fig): Apply standard settings
  • Chart modules import directly (NOT passed as parameter)
```

## DATAFRAME FLOW

```
CSV file → load_and_filter() → clean DataFrame
                                      │
                                      ├──> chart_evolution (receives full df)
                                      ├──> chart_modules (receives full df)
                                      └──> chart_complexity (receives full df)
```

Each chart decides what it needs from the full DataFrame!
