# ARCHITECTURE 3 (current + target)

```
cli.py
  │
  │ (arg parsing: repo_path, --csv, --output-dir)
  │
  └──> visualise.py (ORCHESTRATOR)
         │
         ├─ 🎯 _load_and_filter(csv_path) → DataFrame
         │    • Read CSV once
         │    • Apply common filters (remove __init__.py)
         │    • Return clean DataFrame
         │
         └─ create_images(csv_path, output_dir)
               │ Currently: inline CSV read + filter
               │ 🎯 Target: call _load_and_filter()
               │
               ├──> chart_evolution.py ✅
               │      └─ create(df, output_path)
               │           ├─ _prepare_data(df) → df_prepared
               │           │    Transform by date and category mapping
               │           └─ _plot_and_save(df_prepared, path)
               │                Stacked area chart with theme
               │
               ├──> chart_modules.py ✅
               │      └─ create(df, output_path)
               │           ├─ _prepare_data(df) → df_prepared
               │           │    Filter to latest commit, group by module
               │           └─ _plot_and_save(df_prepared, path)
               │                Horizontal bar chart with theme
               │
               └──> 🎯 chart_example.py (future - follows same pattern)
                      └─ create(df, output_path)
                           ├─ _prepare_data(df) → df_prepared
                           └─ _plot_and_save(df_prepared, path)

theme.py ✅ (CENTRALISED THEMING)
  • DEFAULT_LAYOUT: width, height, template
  • apply_common_layout(fig): Apply standard settings
  • Relies on Plotly default colour schemes
  • Chart modules import directly (NOT passed as parameter)
```

## DATAFRAME FLOW

```
CSV file → 🎯 _load_and_filter() → filtered_df (no __init__.py)
                                      │
                                      ├──> chart_evolution.create(filtered_df, path) ✅
                                      ├──> chart_modules.create(filtered_df, path) ✅
                                      └──> 🎯 chart_example.create(filtered_df, path)
```

**Current state:** CSV loading + filtering is inline within `create_images()`

**Target state:** Extract to `_load_and_filter()` private helper function

Each chart decides what it needs from the filtered DataFrame! Chart-specific transformations happen in each chart's `_prepare_data()`.
