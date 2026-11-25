---
status: accepted
date: 2026-11-25
deciders: edouard
---

# ADR-103: Retire SQL Table Builders

## Context and Problem Statement

Four public builders generate SQL for grouping, reshaping, comparing periods,
or applying query clauses, then construct an Evidential table. SQL engines
and DataFrame libraries already provide these operations. Reports can render
their prepared result with explicit columns and a row layout.

## Decision Drivers

- Keep data shaping in the query or DataFrame that defines the report.
- Give report authors control of column names, grouping, and aggregate semantics.
- Remove duplicate query generation and automatic schema discovery.

## Considered Options

1. Keep the SQL builders and their generated columns and rows.
2. Deprecate the builders and provide transitional aliases.
3. Remove the builders and construct tables from data shaped upstream.

## Decision Outcome

Remove `comparison_table`, `grouped_table`, `pivot_table` and `query_table`
from the public API. Remove `simple_table` because callers can already use
`EvidentialTable.from_duckdb` or pass a relation to `EvidentialTable`.
Keep `date_range_sql` as a standalone predicate generator for authored queries,
including the live date-range selector. Keep in-memory grouping and the table's
row-layout and column-group rendering.

### Consequences

- Existing callers must move aggregation, filtering, and comparison logic
  into their SQL or DataFrame code and declare the resulting columns.
- Authors can compute non-additive totals from the original records, such as
  with SQL `GROUPING SETS`. Row layouts can summarize additive measures from
  prepared detail rows.
- The table continues to render authored columns, marks, groups and summaries.

## More Information

- Supersedes [ADR-009](009-grouping-sets-for-grouped-totals.md) and
  [ADR-035](035-correct-pivot-aggregations.md).
- Updates the SQL helper decision in [ADR-002](002-display-only-widget.md)
  and the comparison helper decision in [ADR-048](048-fluent-derived-columns.md).
- The [API examples](../../notebooks/49_api_screenshots.py) demonstrate
  SQL preparation and explicit table presentation.
