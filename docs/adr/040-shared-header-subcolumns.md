---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-040: Shared-Header Sub-columns

## Context and Problem Statement

Economic tables often show a right-aligned fixed-precision number beside a
left-aligned period, sometimes followed by a centered chip. Existing column
spanners leave each member's header and ordinary spacing visible. Template
merging loses the independent alignment and visualization of each member.

## Decision Drivers

- Support two, three, or more independently formatted members.
- Compose with nested spanners, hiding, sorting, statistics and empty states.
- Keep one data column per member for search, exports and runtime updates.
- Keep layout rules testable without DOM geometry.

## Considered Options

1. Merge values into a template cell.
2. Add nested table data and a separate composite-cell renderer.
3. Add shared-header metadata to existing physical columns.

## Decision Outcome

Chosen option: `ColumnOptions.subcolumn_group`, a shared display label. Members
with the same label and full `column_group` path cluster at their first
occurrence. With `order_columns_by_group=False`, only contiguous members merge.
One leaf header spans the members, replacing their individual visible titles.
Members can use `font_color` (alias `color`) for gray reporting periods; location
style rules take precedence. Body cells use narrow internal padding and retain
their own formats, alignment, colour, links and visualizations. Singleton groups retain the shared label and
ordinary outer padding. Hiding members recalculates spans and boundaries.

`headers.js` owns column ordering, the pure header plan, header rendering and
member decoration. `rows.js` re-exports existing layout helpers for compatibility.
Shared headers sort on the first visible member, including its `sort_by`;
keyboard focus survives rerendering. Physical body indexes and header spans let
`TableViewport` measure actual frozen-column edges. A header crossing the frozen
boundary scrolls as a whole; a fully frozen span sticks. Frozen counts include
row numbers as before. Sticky header levels use cumulative measured heights.

`statistics.js` renders one summary cell per displayed leaf header, spanning
its physical members. A small centered dot button cycles through visible
members and wraps. Each widget stores the selected member by name under the
run's first physical column. Missing members fall back to the first visible
member, and obsolete group entries are pruned. Paging, sorting, data refreshes
and toggling statistics preserve available selections. Cycling updates only
the cell, retains keyboard focus, and schedules frozen-offset recalculation.

If any visible group has multiple members, every summary gets a fixed footer
area; ordinary and singleton columns have blank, noninteractive footers. Summary
content reserves enough height for numeric statistics so cycling to shorter
text summaries does not move the controls or data rows. Without multi-member
groups, summaries have no additional footer. Numeric formatting and dataset
statistics continue to belong to each physical column.

### Consequences

- Good, because existing column schemas and data traits remain sufficient.
- Good, because arbitrary member counts share one layout implementation.
- Good, because independent numeric alignment and chip rendering are preserved.
- Bad, because shared headers expose one sort action for several members.
- Bad, because callers must choose matching precision and alignment explicitly.

## More Information

- [Demo notebook](../../notebooks/30_subcolumns.py).
- Extends [ADR-037](037-renderer-module-boundaries.md) and
  [ADR-038](038-typed-configuration-validation.md).
