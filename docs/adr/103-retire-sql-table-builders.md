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

### Migration examples

Assume `orders(category, sold_on, sales)` is available on DuckDB connection
`con`. Run the replacement SQL with `con.sql(...)` and pass the relation and
explicit `columns` to `EvidentialTable`.

| Before | After |
| --- | --- |
| `comparison_table(con, "SELECT * FROM orders", ["category"], ["sum(sales) AS sales"], date_column="sold_on", compare_vs="prior year")` | `SELECT category, sum(sales) FILTER (WHERE year(sold_on) = 2024) AS current_sales, sum(sales) FILTER (WHERE year(sold_on) = 2023) AS prior_sales FROM orders WHERE year(sold_on) IN (2023, 2024) GROUP BY category` |
| `grouped_table(con, "SELECT * FROM orders", ["category"], ["sum(sales) AS sales"])` | `SELECT category, sum(sales) AS sales FROM orders GROUP BY category` then pass `row_layout=rows.Rows().grand_summary()`. |
| `pivot_table(con, "SELECT *, year(sold_on) AS yr FROM orders", ["category"], ["yr"], ["sum(sales) AS sales"])` | `SELECT category, sum(sales) FILTER (WHERE year(sold_on) = 2024) AS sales_2024, sum(sales) FILTER (WHERE year(sold_on) = 2023) AS sales_2023 FROM orders GROUP BY category` |
| `query_table(con, "SELECT * FROM orders", where="sales > 0", order="sales DESC", limit=10)` | `SELECT * FROM orders WHERE sales > 0 ORDER BY sales DESC LIMIT 10` |

The comparison and pivot examples use fixed years. Derive the year from your
data if the report should roll forward. For comparison deltas, calculate
`current_sales - prior_sales` and divide by `nullif(prior_sales, 0)` for the
relative change.

`simple_table` is gone. Use `EvidentialTable.from_duckdb(con, sql)`.
The `evidential.grouped.decorate_grouped_rows` module export is also gone.
Use `row_layout` to declare display headings and summaries.

## More Information

- Supersedes [ADR-009](009-grouping-sets-for-grouped-totals.md) and
  [ADR-035](035-correct-pivot-aggregations.md).
- Updates the SQL helper decision in [ADR-002](002-display-only-widget.md)
  and the comparison helper decision in [ADR-048](048-fluent-derived-columns.md).
- The [API examples](../../notebooks/49_api_screenshots.py) demonstrate
  SQL preparation and explicit table presentation.
