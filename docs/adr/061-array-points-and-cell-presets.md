---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-061: Array Points, Cell Presets, and Icon Maps

## Context and Problem Statement

The V2 scope of the API specification lists three presentation gaps that the
first encoding pass did not cover:

- an array of observations in one row, drawn as one marker each
  (`points('observations')`), so a row's distribution sits on the same scale as
  its bar;
- sparkline point-only and marker styles, and a **signed** area fill that
  distinguishes gains from losses;
- a boolean written as a checkmark and label rather than `true`/`false`;
- a **category mapped to an icon** (`col.icons`), the design system's "icon
  mapped from the underlying data".

## Decision Drivers

- A distribution is a *presentation* of an array value, not a new data shape.
- The array column already exists (`col.array`) and is the natural input for
  both a sparkline and a strip of points.
- The design system calls a boolean "a checkmark or `Active` label".
- The value stays the source of truth: sorting, search, statistics and export
  keep using the underlying number/boolean.

## Decision Outcome

Chosen option: extend the existing marks and options rather than add new types.

- **`col.points(source, size=, color=)`** adds a `points` mark encoding: one
  marker per element of the array `source`, positioned on the column's shared
  scale. It chains after a bar (`col.bar('mean').points('observations')`) or
  stands alone (`col.points(...)`, type `array`).
- **`col.sparkline(type="points")`** draws only markers; **`markers=True`** adds
  a dot at every point on a line/area and **`markers="ends"`** only the
  endpoints; **`marker_color=`** colours them, and a per-point `color` key on the
  data (computed upstream in SQL/Python) wins per marker; **`signed=True`**
  splits an area fill at the zero baseline into the accent colour above and the
  negative colour below.
- **`col.boolean(..., true_text=, false_text=, true_symbol=, false_symbol=)`**
  writes `✓ Active` / `✗ Inactive`. The symbol is green when true and red when
  false (`--et-positive` / `--et-negative`).
- **`col.icons(name, map=...)`** (`.icons(...)` on a column) maps each category
  to a glyph or image URL/data-URI; an unmapped value falls back to its text.

All three are presentation options on an existing value; none changes the data
or the column's type for sorting/export.

### Consequences

- Good, because a row's distribution can be read against its mean or target
  without a second column.
- Good, because the boolean column keeps its data type while reading as a status.
- Note: `points` accepts a plain list of numbers (or `{value: …}` / `{x: …}`
  objects); a shared `x`-axis is the column's scale, so it is not a
  free-form scatter with an independent x series.
- Note: the sparkline remains its own coordinate system; combining it with a
  scalar mark in one column is still not allowed (specification §5.1).

## More Information

- `src/evidential/marks.py` (`points`), `src/evidential/_column.py`
  (`Column.points`, `sparkline`, `boolean`),
  `src/evidential/configuration.py` (`SparklineOptions`, `BooleanOptions`).
- `frontend/src/visualizations.js` (`renderMarks`, `renderSparkline`),
  `frontend/src/cells.js`, `frontend/src/color.js`, `frontend/src/table.css`.
- `tests/test_marks.py`, `tests/test_column_builder.py`,
  `frontend/test_table.js`, `notebooks/37_encoding_marks.py`,
  `notebooks/40_sparklines_and_booleans.py`.
- Extends [ADR-058](058-encoding-based-columns.md) and
  [ADR-022](022-type-driven-column-defaults.md); implements specification
  §6.5 (V2).
