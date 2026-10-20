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

- Ticks are computed with a 1/2/2.5/5×10ⁿ "nice" step over the marks' domain
  (`marksDomain`), so the axis lines up with the bars; the label is formatted
  with the column's own format code.
- The axis is a body row rendered before the data rows (or after, for
  `"bottom"`), spanning each axis column; gridlines are drawn inside the marks
  cell behind the marks.
- `axis` and `gridlines` are independent: either may be used alone.
- Axis positions are independent per column; top and bottom scales can coexist.
  Axis and mark tracks share the same padded horizontal area, leaving room for
  endpoint tick text. Gridlines and reference rules join across adjacent data
  rows. Integer ticks have no inferred decimal suffix unless explicitly formatted.

### Consequences

- Good, because a bar or point can now be read to a value, not just labelled.
- Good, because the axis shares the marks' domain, including a fixed domain and
  (for linear scales) `include_zero`.
- Note: ticks use a 1/2/2.5/5×10ⁿ step on a linear scale and a power-of-ten
  ladder (with 2× and 5× subdivisions) on a log scale, so the axis lines up
  with the marks in both cases.
- Note: the axis row is presentational and does not take part in row numbering
  or alternating shading.

## More Information

- `src/evidential/marks.py` (`scale`),
  `src/evidential/configuration.py` (`ScaleSpec`),
  `frontend/src/visualizations.js` (`marksDomain`, `niceTicks`, `renderMarks`),
  `frontend/src/table.js` (`_renderAxisRow`), `frontend/src/table.css`.
- `tests/test_marks.py`, `frontend/test_table.js`,
  `notebooks/41_column_scales.py`.
- Extends [ADR-058](058-encoding-based-columns.md); implements the design
  system's "Column Scales".
