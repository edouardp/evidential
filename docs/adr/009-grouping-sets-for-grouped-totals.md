---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-009: GROUPING SETS for Grouped Totals

## Context and Problem Statement

Grouped tables need a subtotal per dimension prefix and a grand total, with
collapsible groups. How do we compute the subtotals and get their hierarchy to
the renderer?

## Decision Drivers

- One round-trip and a small result set.
- One grouping model shared by database and in-memory data.
- Keep aggregations correct (subtotals of averages are not averages of averages).

## Considered Options

1. One `GROUPING SETS` query, then decorate rows in Python.
2. Separate queries per subtotal level, stitched together.
3. Group entirely client-side in the browser.

## Decision Outcome

Chosen option: "One `GROUPING SETS` query plus a Python decoration pass". The
query adds `grouping(dim) AS __gN` flags; `decorate_grouped_rows` turns them into
`render_type`, `__level`, `__group_key`, `__ancestors` and `__parent_key`, and
orders subtotals above or below their group. `grouped_records` reuses the same
decoration for in-memory rows, so the renderer has exactly one model.

### Consequences

- Good, because subtotals and the grand total come from one query.
- Good, because the Python pass is metadata-only unless the user asks for a
  different aggregation.
- Good, because database and in-memory grouping render identically.
- Bad, because `grouped_table` owns the SQL, so unusual queries need the
  `query_table` escape hatch.

## More Information

- [Technical architecture §4.3](../technical-architecture.md)
- Related: [ADR-002](002-display-only-widget.md), [ADR-019](019-accordion-indentation.md)
- Pivot totals extend this decision in [ADR-035](035-correct-pivot-aggregations.md).
