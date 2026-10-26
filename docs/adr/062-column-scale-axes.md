---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-062: Column Scale Axes and Gridlines

## Context and Problem Statement

The design system's *Column Scales* section says: "Some visualisations benefit
from having scales to read off in the table. These can be placed above or below
the column cells … Vertical lines can optionally be drawn on the column to aid
reading what values are associated with the graphic elements." The marks API
had `reference_line`/`reference_band` but no way to read an absolute value off a
bar or point.

## Decision Drivers

- A length is only meaningful against a scale; the label gives the value but not
  the position.
- The axis must use the *same* domain as the marks (explicit `domain` included).
- The design system wants the choice of above or below, and gridlines optional.
- Ticks should round to readable numbers and use the column's format.

## Decision Outcome

Chosen option: three more keys on the shared `scale`, exposed through
`.scale(...)`:

| option | meaning |
| --- | --- |
| `axis=True` | draw a tick axis for the column |
| `axis_position="top"` (default) / `"bottom"` | place it above or below the cells |
| `gridlines=True` | draw a faint vertical line through the cells at each tick |

```python
col.bar("share").scale(domain=(0, 40), axis=True, gridlines=True, axis_position="bottom")
```

- Linear ticks use a 1/2/2.5/5×10ⁿ "nice" step over the marks' domain
  (`marksDomain`), so the axis lines up with the bars; the label is formatted
  with the column's own format code.
- Axes are header/footer metadata, outside the row content area. A top axis is
  the final header tier below its column label and above the first horizontal
  body line; a bottom axis is in the table footer below the last horizontal
  body line. Tick marks touch those lines from outside. Axes never create
  synthetic records or body rows and do not acquire shading or body boundaries.
- The top-axis tier pushes the corresponding column label upward. Labels with
  no top axis span that extra tier and remain aligned just above the first body
  line. A shared sub-column label moves up if any of its members has a top axis;
  the individual scales retain their physical column widths. When column
  statistics are present, they remain header metadata before the axis tier.
- Axis tracks retain identical horizontal padding to mark tracks. Their height
  includes both tick text and the tick itself; top and bottom cells have no
  vertical padding that could create a gap at the horizontal boundary.
- `axis` and `gridlines` are independent: either may be used alone.
- Gridlines, reference lines and reference bands use a cell-sized guide layer with inherited
  horizontal padding. The layer clips its own paint to the cell, eliminating
  fractional-pixel overflow from extending guides beyond the glyph track.
  Marks, labels and endpoint arrows retain their independent overflow behavior.
- Bands fill the cell height behind gridlines, reference rules and marks.
  Explicit band colors, including alpha, are used as supplied; only the default
  theme band mixes its color to 14% opacity. A pale user-supplied fill must not
  receive an additional fade that makes it disappear.
- Axis positions are independent per column; top and bottom scales can coexist.
  Axis and mark tracks share the same padded horizontal area, leaving room for
  endpoint tick text. Gridlines and reference rules join across adjacent data
  rows. Integer ticks have no inferred decimal suffix unless explicitly formatted.

### Consequences

- Good, because a bar or point can now be read to a value, not just labelled.
- Good, because the axis shares the marks' domain, including a fixed domain and
  (for linear scales) `include_zero`.
- Log axes label powers of ten and the domain endpoints. Intermediate ticks
  at 2–9 times each power of ten are shorter and unlabeled, preserving the
  logarithmic spacing without crowding the labels: positions are logarithms of
  the tick values, so gaps shrink toward the next decade. Major and minor tick
  marks are black. Minor ticks touch the same
  horizontal body boundary as major ticks, above or below the rows. The
  existing 1/2/5 log reference ladder remains the gridline spacing.
- Note: neither the axis tiers nor column statistics live in the data body.
  Pagination and fullscreen fitting reserve their header/footer height; frozen
  columns keep scale tracks horizontally aligned as the table scrolls.

## More Information

- `src/evidential/marks.py` (`scale`),
  `src/evidential/configuration.py` (`ScaleSpec`),
  `frontend/src/visualizations.js` (`marksDomain`, `niceTicks`, `renderMarks`),
  `frontend/src/table.js` (`_renderAxisRow`), `frontend/src/table.css`.
- `tests/test_marks.py`, `frontend/test_table.js`,
  `notebooks/41_column_scales.py`.
- Extends [ADR-058](058-encoding-based-columns.md); implements the design
  system's "Column Scales".
