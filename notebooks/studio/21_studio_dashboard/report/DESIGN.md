# Report view

## Project intent

- **Audience**: a reader who wants the numbers, not an interactive table.
- **Goal**: render the same notebook results with the page's own markup, so it
  is a candidate for a static (Prepared or Browser) export.
- **Notebook**: `notebooks/21_studio_dashboard.py`.

## Notebook targets

| Host | Notebook source | What it shows |
| --- | --- | --- |
| `mo-value="kpis.cities"` … | `kpis` dict | The key figures. |
| `mo-value="filtered"` | `filtered` list | The rows, rendered by the view's JS. |

## Notes for the next agent

- This view deliberately does **not** project the `EvidentialTable` widget; it
  formats and draws the projected values itself. That keeps it usable in every
  runtime, including a zero-Python export.
- The dashboard view in `../dashboard/` shows the complementary approach: let
  the notebook's widget do the rendering.
