---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-021: Support marimo Studio Views by Projection

## Context and Problem Statement

marimo Studio turns one notebook into named views (dashboards, articles, slide
decks). A view is a separate frontend project that places the notebook's cells,
outputs and values by name. `EvidentialTable` is an interactive anywidget, so a
view needs a defined way to show it — and a view has no direct Python of its
own.

## Decision Drivers

- Let a view show the notebook's own table, interactivity intact.
- Keep the notebook the single owner of data and computation.
- Give the view control of presentation (KPIs, layout, formatting).
- Keep the committed demo verifiable without requiring Studio for validation.

## Considered Options

1. Support Studio **projections** as the integration surface, with a committed
   demo view and Server runtime.
2. Build a bespoke Studio view provider / widget for evidential.
3. Do nothing: Studio is out of scope.

## Decision Outcome

Chosen option: "Support projections". Studio already defines the contract, so
we adopt it rather than inventing one:

- A live table is projected with `<marimo-cell name="…">` (the cell that
  displays the `EvidentialTable`).
- Native controls use `<marimo-cell name="…">`.
- Single values use `mo-value="…"` and are formatted by the view's own JS.
- The demo uses the **Server** runtime, because the widget needs a kernel. A
  Prepared or Browser export additionally needs `evidential` on PyPI,
  because Studio resolves the notebook's declared dependencies when exporting.
- Views are committed next to the notebook in a configured `view_root`
  (`notebooks/studio/<notebook>/`), not under the ignored `__marimo__/`.

### Consequences

- Good, because the notebook stays the single source of truth and every result
  traces back to a cell.
- Good, because interactivity, conditional formatting and the widget's own CSS
  all survive into the view.
- Good, because `make studio-serve` / `make studio-validate` and a
  dependency-light repository test make the integration reproducible.
- Bad, because the widget is not replayable in the Prepared (zero-python)
  runtime, so a static export cannot show the live table.
- Bad, because the Browser (wasm) runtime is unavailable until the package is
  published on PyPI.
- Bad, because the demo couples the repository to Studio's fast-moving,
  exact-marimo release, so it is isolated behind `make studio-*` targets and an
  optional `studio` extra.

## More Information

- [Using EvidentialTable in marimo Studio views](../marimo-studio.md)
- The demo: `notebooks/21_studio_dashboard.py`,
  `notebooks/studio/21_studio_dashboard/dashboard/` (live widget) and
  `notebooks/studio/21_studio_dashboard/report/` (view-rendered).
- `tests/release/test_studio_views.py`
