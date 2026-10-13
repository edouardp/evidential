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
