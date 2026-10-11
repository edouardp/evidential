---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-002: Display-Only Widget, Not a Query Builder

## Context and Problem Statement

Evidence's `DataTable` is inseparable from its SQL query builder: dimensions,
pivots, measures, date ranges and comparisons are all driven from the component.
We are bringing the table to Marimo, where the analyst already writes SQL and
already has cell reactivity. How much of Evidence's query layer should we
reimplement?

## Decision Drivers

- Avoid duplicating SQL and Marimo reactivity.
- Accept data that never touched a database (lists, DataFrames, Arrow).
- Keep the renderer small, predictable and testable.
- Preserve the ability to express Evidence's query-builder features.

## Considered Options

1. Display-only widget; shaping stays in SQL (with Python helpers that build it).
2. Port Evidence's query builder into Python.
3. Embed a JavaScript query engine in the browser.

## Decision Outcome

Chosen option: "Display-only widget", because the renderer should be a pure
function of the rows it is given, and Marimo already owns reactivity. Evidence's
query features are offered as SQL-building helpers (`grouped_table`,
`pivot_table`, `query_table`, `comparison_table`, `date_range_sql`) and as live,
parameterised re-querying (`LiveEvidenceTable`).

### Consequences

- Good, because the same widget renders rows from DuckDB, pandas or a list.
- Good, because the renderer stays small and has one grouping model.
- Good, because there is no second, Python-side query language to learn.
- Bad, because there is no dimension/measure UI; users write SQL for that.
- Bad, because some Evidence features (comparison tooltips) need extra plumbing.

## More Information

- [Design & DX §4.1](../design-and-dx.md#41-display-only-not-a-query-builder)
- Related: [ADR-009](009-grouping-sets-for-grouped-totals.md)
