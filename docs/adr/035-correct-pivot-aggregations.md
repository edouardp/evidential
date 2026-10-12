---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-035: Aggregate Pivot Totals from Original Records

## Context and Problem Statement

Summing previously aggregated pivot cells gives incorrect averages, extrema,
and distinct counts. Python aggregation overrides also need to address the
generated columns, and display labels may collide with total names.

## Decision Drivers

- Preserve arbitrary SQL aggregate expressions, including scalar wrappers.
- Compute each default subtotal and total from the original records.
- Keep the existing column names when they are unique.
- Preserve the shared grouped-row metadata and aggregation API.

## Considered Options

1. Restrict pivots to additive measures.
2. Parse aggregate expressions and choose an outer aggregation.
3. Aggregate every dimension/pivot level with `GROUPING SETS`, then project.

## Decision Outcome

Chosen option: aggregate each level with `GROUPING SETS`. The inner query
evaluates the original measure expressions for every dimension prefix, with
and without the pivot dimensions. The outer query projects the single result
for each cell with a filtered `max`; it does not sum aggregate results.

Python aggregation overrides expand headline measure names to their generated
pivot columns. Weight sums travel in hidden columns for the same cells, and
missing values and weights are excluded as pairs when computing weighted means.

Reserve total column names before allocating pivot names. Resolve collisions
with deterministic suffixes while keeping display groups separate from names.

### Consequences

- Good, because averages and distinct counts retain their SQL semantics.
- Good, because wrapped expressions such as `round(avg(value), 0)` work.
- Good, because a category named `Total` cannot overwrite the total column.
- Bad, because the intermediate query contains more grouping sets.
- Bad, because colliding labels require suffixed column names.

## More Information

- Extends [ADR-009](009-grouping-sets-for-grouped-totals.md).
- Overrides recompute summaries from displayed detail values, as documented in
  [the aggregation API](../../README.md#aggregations-for-subtotalstotals).
