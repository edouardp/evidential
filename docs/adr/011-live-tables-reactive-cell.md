---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-011: Live Tables Use a Persistent Widget and a Reactive Cell

## Context and Problem Statement

A live table re-runs a parameterised query when a control changes, preserving
sort, search and page state. In Marimo, referencing a control from a cell
registers a dependency and re-runs that cell. If the widget is created in that
cell, every change recreates it and the table visibly disappears and reappears.

## Decision Drivers

- Preserve interaction state across re-queries.
- Avoid recreating the widget on every control change.
- Work both inside Marimo and in plain ipywidgets hosts.

## Considered Options

1. Persistent widget plus a separate reactive cell calling `set_controls(...)`.
2. Create the widget and its controls in one cell.
3. Bind controls to the widget instance (`bind_controls=True`).

## Decision Outcome

Chosen option: "Persistent widget plus a reactive cell". The widget is created
once in a cell that references no control; a second cell calls
`set_controls(...)`, which re-runs the query in place. Parameters are always
bound as SQL parameters, never spliced into SQL text. `bind_controls=True`
remains as a fallback for hosts without reactive cells.

### Consequences

- Good, because sort, search, collapse and page state survive a re-query.
- Good, because the table stays on screen instead of flashing.
- Good, because filters cannot inject SQL.
- Bad, because the "do not reference the controls" rule is easy to break and
  produces a confusing visual bug.

## More Information

- [Design & DX §4.8](../design-and-dx.md#48-live-tables-work-with-marimos-reactivity-not-against-it)
- `notebooks/03_live_drilldown.py`, `notebooks/04_live_demo.py`
