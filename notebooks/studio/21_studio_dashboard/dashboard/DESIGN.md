# Dashboard view

## Project intent

- **Audience**: an analyst reviewing NYC-style trip revenue by city.
- **Goal**: show the KPIs and the underlying rows from the same filtered data,
  and keep the table fully interactive.
- **Notebook**: `notebooks/21_studio_dashboard.py`.
- **Runtime**: **Server** — the view mounts the live `EvidentialTable` anywidget,
  which needs a Python kernel.

## Notebook targets

| Host | Notebook source | What it shows |
| --- | --- | --- |
| `<marimo-cell name="region_filter">` | `region_filter` cell | A native marimo dropdown. |
| `<marimo-cell name="revenue_table">` | `revenue_table` cell | The live `EvidentialTable` widget. |
| `mo-value="kpis.cities"` … | `kpis` dict in the `kpis` cell | Filtered key figures. |

## Notes for the next agent

- The KPI numbers are projected with `mo-value` and formatted in the browser
  with `Intl.NumberFormat`; the notebook owns the value, the view owns its
  presentation.
- Keep the `mo-value` hosts in authored HTML so Studio can authorize each
  selector.
- The widget ships its own CSS; the view only supplies page chrome and the
  projection-host skeleton.
