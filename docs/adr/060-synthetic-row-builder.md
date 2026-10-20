---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-060: A Synthetic-Row Builder

## Context and Problem Statement

The grouped helpers generate a fixed shape: a subtotal for every prefix of the
grouping dimensions and a grand total, each recomputed from the detail values
with an *aggregation*. That covers hierarchical totals, but the design system
also asks for rows that the grouping helpers have no place for:

- a **section divider** that introduces a group (`North America`),
- a **summary** with a report-specific label (`Developing average`) whose values
  are computed however the author wants — e.g. the mean of each group's rows,
- a **grand total** with the same freedom.

The API specification (§9) sketches a fluent builder for exactly this and marks
the exact names as open.

## Decision Drivers

- A summary value should be expressible as a function of the group's rows, not
  only as an aggregation of one column's values.
- The row *kinds* must stay explicit so the renderer can style them and so
  sorting/export keep treating synthetic rows separately.
- The builder should not duplicate the nested-subtotal machinery that
  `grouped_records` already provides.
- Rows must remain plain dicts, so they can be inspected and tested.

## Decision Outcome

Chosen option: a small `evidential.rows` module with an immutable, fluent
`Rows` builder whose `build()` returns plain row dicts for
`EvidentialTable(rows=...)`.

```python
rows.of(detail)
    .group_by("region")
    .section()                                    # divider before each group
    .summary(label="Developing average",
             values={"debt": lambda group: sum(r["debt"] for r in group) / len(group)})
    .total(label="All regions")
    .build()
```

- `values` maps a column to a **callable** over the group's rows, a built-in
  **aggregation name** (`sum`, `mean`, `median`, `min`, `max`, `count`, …), or a
  literal. A summary or total with no `values` sums the numeric columns.
- `label` is a string or a callable over the group's rows; without one the first
  grouping dimension's value names the group.
- `.group_by(...)` sorts the detail rows and groups by the **first** dimension.
  Nested subtotals at every level remain the job of `grouped_records`.
- A summary row is emitted with `render_type="row_subtotal"` and `__level=0`
  (flat: no accordion indent, no chevron); a section with `render_type=
  "row_section"`; the total with `render_type="row_total"`. So the existing
  renderer styles them without new row kinds.
- Builder rows carry `__row_builder`, stable `__group_key` / `__parent_key`
  identities and detail `__ancestors`. Sorting stays within each section;
  search retains headings and summaries for matching detail rows. This
  metadata distinguishes flat builder summaries from accordion subtotals, so
  builder tables can paginate with continuation headings.
- `.section(values=...)` renders a combined section and summary, with values
  in their configured columns. Centered sections reject summary values.
  Summary/total labels also work when the grouping dimension is not displayed.
  Internal metadata is excluded from default numeric totals.
- Values are computed when `build()` runs. Filter the input in SQL/Python
  **before** building to calculate summaries for a filtered result. Browser
  search changes the visible detail rows and preserves precomputed summaries;
  it cannot re-execute arbitrary Python summary functions in a static export.

### Consequences

- Good, because an author can label and compute a summary however the report
  needs, including from the group's rows.
- Good, because the builder is immutable and returns ordinary dicts; it composes
  with explicit `columns=[...]`.
- Note: the builder is deliberately **not** a second nested-grouping engine.
  `grouped_records`/`grouped_table` stay the tool for hierarchical subtotals.
- Note: `__level=0` keeps a builder table flat. A table that mixes builder rows
  with a multi-level grouping should be built with `grouped_records` instead.

## More Information

- `src/evidential/rows.py` (`Rows`, `of`), `src/evidential/__init__.py`.
- `tests/test_rows.py`, `notebooks/39_synthetic_rows.py`.
- Extends [ADR-009](009-grouping-sets-for-grouped-totals.md) and
  [ADR-059](059-synthetic-row-presentation.md); implements the API
  specification §9.
