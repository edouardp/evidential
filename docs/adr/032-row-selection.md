---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-032: Row Selection Drives the Notebook

## Context and Problem Statement

The widget was one-way: Python → browser. We want a table to **drive** the
notebook — click a country row, get its id in a variable, and have a second table
re-query on it. Two things are needed: a click that reaches Python, and Marimo
treating that value as a cell dependency.

Marimo's `mo.ui.anywidget` wraps a widget with `on_change=None`, and a raw
`traitlets` change made by the browser does **not** re-run dependent cells (the
Python value stays stale). A mechanism was needed that Marimo already reacts to.

## Decision Drivers

- Reuse Marimo's reactivity; no new element type or polling.
- Keep the widget a pure function of its rows (see ADR-002).
- The clicked value must cross the boundary reliably.

## Considered Options

1. A `select` option: the row click sets a synced `selected` trait and calls
   `model.save_changes()`; Python reads `table.widget.selected`.
2. A Marimo custom UI element (register a component with an `on_change`).
3. Poll the trait from a cell with `mo.ui.refresh`.

## Decision Outcome

Chosen option: "A `select` option + `selected` trait". Marimo's comm handler
(`WIDGET_COMM_MANAGER.receive_comm_message`) already maps a widget **update**
message to `set_ui_element_value` for the element that owns the comm, and re-runs
the cells that depend on it. The only missing piece was that
`model.set(key, value)` alone does not send the update — the Jupyter widgets
protocol needs `model.save_changes()`. So the renderer, when the column named by
`select` exists, marks the row clickable, sets `selected` to that row's key and
saves it. Clicking the selected row clears it; `EvidenceTable(..., selected=...)`
preselects.

Option 2 was rejected as more machinery for the same result. Option 3 was
rejected: polling is slower and re-runs cells that did not change.

### Consequences

- Good, because a table can drive a drill-down with ordinary Marimo reactivity —
  only the cells that read `selected` re-run, and the source table is not
  re-created.
- Good, because `select` reuses the existing per-row machinery (like `link`), and
  the selected row is marked (`.et-row-selected`).
- Note: the value sent is the widget's **whole synced state**, not just the key;
  the sync traits are small, so this is fine.
- Note: the renderer must call `save_changes()` — a trait set without it updates
  only the browser.
- Bad, because the table is no longer strictly display-only; the back-channel is
  a deliberate, narrow exception, and ADR-002's "no query builder" decision still
  stands.

## More Information

- `frontend/src/table.js` (`_renderRow`, `render`), `src/evidence_tables/table.py`
  (`selected`)
- [Technical architecture §6.5](../technical-architecture.md)
- `notebooks/29_row_selection.py`
