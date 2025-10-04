# ARCHITECTURE 3 - Complete and Accurate Against Codebase as of `2025-10-04`

```text
cli.py
  │
  │ (arg parsing: repo_path, --csv, --output-dir)
  │
  └──> visualise.py (ORCHESTRATOR) ✅
         │
         └─ create_charts(csv_path, output_dir) ✅
               │ Loads CSV, filters data, delegates to chart modules
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
               │           │    Filter to latest commit, group by file
               │           └─ _plot_and_save(df_prepared, path)
               │                Horizontal bar chart with theme
               │
               └──> 🎯 NEW CHART PATTERN (add charts by following this structure)
                      └─ create(df, output_path)       [REQUIRED: public API]
                           ├─ _prepare_data(df)        [transform data]
                           └─ _plot_and_save(df, path) [generate & save chart]

theme.py ✅ (CENTRALISED THEMING)
  • DEFAULT_LAYOUT: template, dimensions, legend positioning
  • apply_common_layout(fig): Apply standard settings to any chart
  • Chart modules import and call directly (not injected as parameter)
```

## DATAFRAME FLOW

```text
CSV file → visualise.create_charts() → filtered_df
                                              │
                                              ├──> chart_evolution.create(df, path) ✅
                                              ├──> chart_breakdown.create(df, path) ✅
                                              └──> 🎯 chart_example.create(df, path)
```

**Established patterns:**

- `visualise.py` orchestrates but contains no chart logic
- Each chart module follows: `create()` → `_prepare_data()` → `_plot_and_save()`
