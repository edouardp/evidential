---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-006: Hidden Helper Columns for Presentation Logic

## Context and Problem Statement

Some presentation needs a value the renderer cannot derive from the displayed
cell alone: a per-row tint chosen by business logic, a per-row format code, a
footnote keyed to a cell, or the sources of a merged `low–high` column. How do
we get that value to the renderer without teaching it business rules?

## Decision Drivers

- Keep the renderer dumb and pure.
- Let SQL do what SQL is good at (CASE, joins, window functions).
- Make a new presentation idea possible without new JavaScript.

## Considered Options

1. Hidden helper columns: extra columns that are never shown but drive a shown
   column.
2. Extend the renderer with more per-column logic.
3. Mutate the displayed value in Python.

## Decision Outcome

Chosen option: "Hidden helper columns", because it turns presentation logic into
ordinary data manipulation. A column can hide itself (`hide: True`) and be
consumed by `row_conditional_colors`, `fmt_column`, `cols_merge*`, `footnote`,
`conditional_colors` and friends.

### Consequences

- Good, because the renderer is a pure function of the rows it receives.
- Good, because new presentation features usually need no JavaScript at all.
- Good, because the helper can be computed where the data lives.
- Bad, because a forgotten or mistyped helper column silently does nothing —
  the demo bug in `12_color_scales.py` was exactly this.
- Bad, because the notebook carries knowledge of both the visible and hidden
  column sets.

## More Information

- [Design & DX §4.3](../design-and-dx.md#43-hidden-helper-columns-presentation-logic-that-lives-at-render-time)
