# ARCHITECTURE 3 - Complete and Accurate Against Codebase as of `2025-10-02`.

```
cli.py
  │
  │ (arg parsing: repo_path, --csv, --output-dir)
  │
  └──> visualise.py (ORCHESTRATOR) ✅
         │
         ├─ _load_and_exclude_files(csv_path, filenames) ✅
         │    • Read CSV once
         │    • Exclude rows with specified filenames
         │    • Return filtered DataFrame
         │
         └─ create_charts(csv_path, output_dir) ✅
               │ Calls _load_and_exclude_files()
               │
               ├──> chart_evolution.py ✅
               │      └─ create(df, output_path)
               │           ├─ _prepare_data(df) → df_prepared
               │           │    Transform by date and category mapping
               │           └─ _plot_and_save(df_prepared, path)
               │                Stacked area chart with theme
               │
               ├──> chart_breakdown.py ✅
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
CSV file → _load_and_exclude_files() ✅ → filtered_df
                                                      │
                                                      ├──> chart_evolution.create(df, path) ✅
                                                      ├──> chart_breakdown.create(df, path) ✅
                                                      └──> 🎯 chart_example.create(df, path)
```

**Pattern established:** `visualise.py` acts as pure orchestrator with no inline chart logic.
Data loading/filtering separated into `_load_and_exclude_files()` helper.
Each chart module follows consistent structure: `create()` → `_prepare_data()` → `_plot_and_save()`.
