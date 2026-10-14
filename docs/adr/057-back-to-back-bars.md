---
status: accepted
date: 2026-10-14
deciders: edouard
---

# ADR-057: Back-to-Back Bars — Direction and Benchmark Rules

## Context and Problem Statement

The centred bar (ADR-052) covers signed deviation: a zero line, the bar growing
left or right by sign. The other recurring *Economic* / Economist chart is
**back-to-back** (a "tornado"): two bar panels mirrored about a central label
column — one grows **right** from its left edge, the other **left** from its
right edge — often with a vertical **benchmark rule** (a median or target) drawn
down each panel. The existing bar only fills from the left, so the mirrored half
was inexpressible, and there was no way to draw a value-anchored rule at all.

## Decision Drivers

- Mirroring is a *presentation* of the same bar, not a new visualisation.
- A benchmark rule belongs to the column, is stated once, and lines up with the
  bars on their own scale.
- The same colour should be able to key both panels.
- Keep the bar's existing options, colours and label behaviour.

## Decision Outcome

Chosen option: three more `bar_options`, exposed through `.bar(...)`:

- **`direction="left"`** — the bar fills from the **right** edge and grows left
  (`.et-bar-fill-left`); `"right"` (the default) is unchanged. The `reference`
  rule mirrors with it.
- **`reference=N`** — a 1px vertical rule at value `N` on the bar's own scale
  (`.et-bar-reference`), full height so it reads as one line down the column.
  `reference_color` sets its colour (default a muted teal); `reference_label`
  adds a caption, shown once on the last row (`.et-bar-reference-label`) so it
  does not repeat, and anchored to the nearer edge so it stays inside the column.
- **`color="@column"`** — the `@column` reference convention (ADR-051): each bar
  takes its colour from that column's per-row value, instead of one fixed colour.
  Internally this sets `bar_options.bar_color_column`.

The bar's label is placed by the ordinary column `align`, so pairing a leftward
bar with `align="left"` and a rightward one with `align="right"` puts the values
at the outer edges of a back-to-back table.

### Consequences

- Good, because the mirrored league table is now expressible with the existing
  bar cell, colours and metrics — no new visualisation, no new data shape.
- Good, because a benchmark rule is reusable beyond back-to-back (any bar column
  can carry a target line).
- Note: the rule is a *presentation* — it is drawn from the column's own
  min…max (or `fit_to_data`), so it only lines up when the reference is on the
  same scale as the values, which is the intended use.
- Note: `reference_label` is shown by CSS on `tbody tr:last-child`, so with
  paging it appears on the last row of each page.

## More Information

- `frontend/src/visualizations.js` (`renderBar`, `referenceMarks`),
  `frontend/src/table.css`, `src/evidential/_column.py` (`bar`),
  `src/evidential/_column_options.py`, `src/evidential/configuration.py`
  (`BarOptions`).
- `frontend/test_table.js`, `tests/test_column_builder.py`.
- Demo: [`notebooks/34_centered_bars.py`](../../notebooks/34_centered_bars.py).
- Extends [ADR-020](020-bar-visualisation-geometry.md) and
  [ADR-052](052-centered-bar.md); uses [ADR-051](051-at-column-reference.md).
