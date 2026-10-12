---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-019: Indent Dimension Cells in Accordion Groups

## Context and Problem Statement

In an accordion group, a subtotal row shows the group's dimension value and its
detail rows repeat the *parent* dimension with no visual cue that they belong to
the group. The hierarchy is invisible, especially when the parent value is
repeated verbatim.

## Decision Drivers

- The nesting must be visible without adding columns or colour.
- Match Evidence's established behaviour so the two tables read the same.
- Do not change row height or cell width.

## Considered Options

1. Indent dimension cells, as Evidence's `getIndentAmount` does.
2. Hide repeated parent values on detail rows.
3. Do nothing.

## Decision Outcome

Chosen option: "Indent dimension cells". Detail rows indent their *parent*
dimension columns but not the leaf dimension; subtotal rows indent their
ancestor columns. Non-dimension columns are never indented, and section mode
(merged `rowspan` cells) is unaffected. The indent is applied to the cell's
`padding-left`, so it does not change the row height or the table width.

### Consequences

- Good, because parent/child relationships are visible at a glance.
- Good, because it matches Evidence's rendering.
- Good, because a namespace change (adding `dimCount`) also made the section
  path robust when all groups are collapsed.
- Bad, because the rule is subtle: indenting the *parent* on detail rows is
  counter-intuitive until you see it.

## More Information

- Group chevrons are native buttons with `aria-expanded`; keyboard activation
  restores focus after the table is rebuilt.
- [Design & DX §4.6](../design-and-dx.md#46-grouping-is-one-sql-query-plus-a-decoration-pass)
- Related: [ADR-009](009-grouping-sets-for-grouped-totals.md)
- `notebooks/13_hierarchical_rows.py`
