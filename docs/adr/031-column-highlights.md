---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-031: Column and Column-Group Highlights

## Context and Problem Statement

Some tables call out one column or a group of columns — a projection, a total, the
"current" period (an IMF-style "2020 Projection" band). `viz="color"` fills cells
from the data, which is a different thing: the emphasis is a fixed property of
the *column*, not of each value. We want to paint a vertical band behind a
column, or behind every column of a group.

## Decision Drivers

- An emphasis band is a column property, not a data value.
- It should work for a whole group (the spanner plus all its columns) too.
- It must not be defeated by row shading or row colours.
- Keep it a single, obvious option.

## Decision Outcome

Chosen option: a per-column **`highlight`** colour (aliases `highlightColor` /
`highlight_color`). The frontend paints it inline on the header `<th>` and every
data `<td>`, so it wins over `row_shading` and `row_conditional_colors` and reads
as a continuous vertical stripe (a row hover still tints it). A `column_groups`
entry may be a mapping, `{"columns": [...], "highlight": "#..."}`, which sets
`highlight` on each column that does not already have one — so a column can
override its group. The group **spanner** is filled only when **every** column it
spans shares the same highlight, so a single highlighted column inside a group
does not tint the spanner (matching the "projection column" look).

### Consequences

- Good, because one column option expresses the whole emphasis.
- Good, because a group is highlighted with one line, and a column inside it can
  still opt out.
- Good, because the band survives row shading and row colours.
- Note: the spanner-fill rule is derived (all spanned columns share the colour)
  rather than a separate group option; a group whose columns are highlighted
  individually gets the same spanner.

## More Information

- `frontend/src/table.js` (`_renderHeader`, `_renderRow`)
- `src/evidence_tables/table.py` (`_resolve_column_groups`)
- `notebooks/28_column_highlights.py`
