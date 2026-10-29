---
status: accepted
date: 2026-10-29
deciders: edouard
---

# ADR-087: Searchable, Cross-Filtered Dimension Grid

## Context and Problem Statement

Ranked category bars are useful inputs alongside an Evidential table. A fixed
top-ten list hides low-ranked categories, while fitting twenty dimensions into
the available width makes labels unreadable. Hierarchical fields such as AWS
service and usage type must constrain each other from the source records.

## Decision Drivers

- Keep the familiar horizontal arrangement of independent dimension lists.
- Support mouse scrolling, complete-domain string search and many dimensions.
- Keep selections typed, removable and reactive in marimo.
- Avoid transporting source records or rendering every category button.
- Preserve the table renderer's display-only responsibility.

## Considered Options

1. Add a special table presentation and filter its already-limited rows.
2. Send all source records to a browser-side facet engine.
3. Add a separate anywidget with Python aggregation and virtualized browser lists.

## Decision Outcome

Chosen option: **3**. `DimensionGrid` normalizes the same input containers as
the table, infers string dimensions or accepts explicit fields/display names,
and computes `sum`, `count`, `mean`, `min` or `max`. A numeric metric defaults
to `sum`; no metric means record count. No DuckDB dependency is introduced.

Selections are OR within a dimension and AND across dimensions. Each category
list applies all selections except its own dimension's filter. This
disjunctive faceting keeps alternatives available without breaking hierarchy:
selecting RDS constrains usage types to those belonging to RDS. Incompatible
selections remain in the list and removable with an unavailable metric. Empty
selection means the entire source. Null is a distinct selectable category.
Multiple selection is enabled by default: each click toggles a category without
modifier keys. `multiple=False` opts into one selection per dimension.

Only aggregate categories, options and typed selections are synchronized.
Python keeps original records and exposes detached `.raw` and `.filtered`
snapshots. `.where()` produces a quoted SQL predicate with bound parameters
for linked relations at the same dimension grain. SQL strings and expressions
are not accepted as metric specifications; callers precompute those in SQL.

The browser owns transient search and scroll state. Search covers all available
categories, not a truncated ranking; it narrows choices rather than selecting
records by substring. The search icon replaces the heading with an input and
close button. Blur restores the heading, retaining the query and a small active
indicator. Selected values remain in the same ranked list, including when
they do not match the search. Selecting a row does not promote it to the top
or change the scrolling position. Bold text and a full-height, six-pixel dark
red strip on the left identify selected rows without shifting their labels.

Each dimension has slim native vertical scrollbars and wheel scrolling with
a fixed-row virtual window and small overscan. The outer strip has native horizontal scrolling,
arrow navigation and minimum column widths. Keyboard navigation reaches
off-screen categories. Search inputs and scroll state survive facet updates.
The dedicated bundle reuses formatting and safe DOM helpers while leaving the
table lifecycle independent. Both bundles are committed and package-checked.
The slicer uses a white surface and dark text, matching the table examples
regardless of the browser's preferred colour scheme.
Its inherited font and `0.75rem` baseline match the table. Compact 20px rows
share one JavaScript height constant with CSS through a custom property so
virtualized scrolling and rendered geometry stay aligned. Titles are bold;
availability and selection counts are centered below each dimension.

### Consequences

The new input complements the display widget in ADR-002; it does not add query
execution or filtering responsibilities to `EvidentialTable`. Marimo creates
each widget once and updates linked results in separate reactive cells.

Aggregation scans the in-memory normalized source in O(records × dimensions)
per selection and sends the complete aggregate category domain. Virtualization
bounds DOM work, not Python memory or wire payload size. Large fact tables
should be preaggregated at the required dimension grain before constructing
the grid; sum/count weights compose, but precomputed means require careful
weighting. A database-paged backend would be a separate future decision.

Notebook 56 links the committed Needful Things orders to monthly sales.
Notebook 57 replaces the synthetic stress example with the local processed
`aws-cur-example` product: nine useful dimensions, cost-driver totals, daily
trends and individual line items. Additive cost is preaggregated at the full
filter grain for the slicer; linked results filter the original line items
before aggregation. Detail row limits do not affect totals or shares, and
usage quantities are grouped within billing units.

Unit and live-browser tests cover aggregation, hierarchy, safe
SQL, complete search, wheel scrolling, keyboard navigation and overflow.

## More Information

- [Evidence dimension grid](https://legacy-docs.evidence.dev/components/inputs/dimension-grid/).
- [Demo notebook](../../notebooks/56_dimension_grid.py).
- [ADR-002: Display-Only Widget](002-display-only-widget.md).
- [ADR-011: Persistent Widgets and Reactive Cells](011-live-tables-reactive-cell.md).
