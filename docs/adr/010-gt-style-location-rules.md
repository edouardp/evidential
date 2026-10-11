---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-010: gt-Style Location-Based Rules

## Context and Problem Statement

Per-column configuration cannot express "this one cell is an outlier".
gt/Great Tables solves this with `locations`: functions that target a set of
cells, combined with `tab_style` / `tab_format` / `text_transform`. We want that
power, but rules can involve Python callables (a row predicate) and the browser
sorts and pages the table.

## Decision Drivers

- Composable, precise per-cell control.
- Python callables must work for row predicates.
- Rules must keep pointing at the same cell after sorting and paging.

## Considered Options

1. gt-style locations, resolved in Python to a stable row id.
2. CSS-selector-based rules evaluated in the browser.
3. Per-column configuration only, with hidden helper columns.

## Decision Outcome

Chosen option: "gt-style locations". `resolve_rules` attaches a stable
`__row_id` to every row and splits rules by type: `text_transform` is applied in
Python, while `tab_style`, `tab_format` and `sub_*` travel to the browser as
`{columns, rows: [__row_id...], style | fmt}`. Rules apply in order, last match
wins.

### Consequences

- Good, because a rule can target exactly the cells it names.
- Good, because predicates are ordinary Python.
- Good, because sorting and paging cannot retarget a rule.
- Bad, because a rule's row set is a snapshot of the original order, not the
  current sorted view.
- Bad, because styles and formats are resolved in two different places.

## More Information

- [Design & DX §4.7](../design-and-dx.md#47-rules-borrow-gts-location-api)
- Related: [ADR-005](005-layer-responsibilities.md)
