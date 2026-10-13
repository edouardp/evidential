---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-027: Sort a Column by Another Column's Values

## Context and Problem Statement

Clicking a header sorts by that column. Some columns have no meaningful sort
key of their own, or a key that lives elsewhere: a sparkline of a whole series
should sort by the series' overall trend (Kendall's τ), not by the array; a
formatted value should sort by its underlying number. The sort key may also be
a **helper column** that is not meant to be displayed.

## Decision Drivers

- A visual column (sparkline, bar, colour) must be orderable by the measure it
  encodes.
- The sort key may be hidden from the table.
- No new data plumbing: the values are already in each row.

## Considered Options

1. A per-column `sort_by` option naming another column; the renderer resolves
   the sort key and type from that column.
2. Make the widget sort server-side via a `default_sort`-like query parameter.
3. Require the sort key to be a visible column.

## Decision Outcome

Chosen option: "A per-column `sort_by` option". `sortRows` in `rows.js` resolves the
comparison key to `column.sort_by ?? column.name` and the type from the resolved
column. Because it reads the row objects directly, the target may be a column
with `hide=true` — present in the data but not displayed — or a field absent
from `this.columns` entirely, in which case `compareValues` infers the
comparison from the value. `sort_by` is accepted in `column_config` under
`sort_by`, `sortBy`, `sortColumn` and `sort_column`.

Option 3 was rejected: it would force a helper column into the view purely to
be sortable. Option 2 was rejected: the values are already client-side, so the
sort belongs with the other presentation logic (ADR-005).

### Consequences

- Good, because a sparkline or bar can sort by the number it draws.
- Good, because helper sort keys (e.g. a rank or score) can stay hidden.
- Good, because `default_sort` accepts the same indirection.
- Note: the header arrow stays on the clicked column, so the displayed arrow
  names the column whose values are sorted, not the key column.

## More Information

- `frontend/src/rows.js` (`sortRows`)
- `notebooks/23_wdi.py` — the sparkline column sorts by `kendall_tau`
