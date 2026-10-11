---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-020: Bar Visualisation Geometry

## Context and Problem Statement

The bar visualisation (`viz="bar"`) draws a background bar behind a
right-aligned value. The first implementation used rounded corners, was cramped
against the value, and sat inside the cell padding, so it never reached the row
separators. Users expect the Evidence look: a flat, full-height bar with a
little clearance.

## Decision Drivers

- Match Evidence's visual result.
- Give the value clearance without widening the cell or changing row height.
- Keep negative bars growing from the right.

## Considered Options

1. Full-height rectangular overlay with the value inset, via negative
   margins/padding that cancel out.
2. A short bar with rounded corners, inside the cell padding.
3. A side-by-side bar and value (no overlay).

## Decision Outcome

Chosen option: "Full-height rectangular overlay". The bar cell is pulled into
the cell padding with negative margins and the value is pushed back out by the
same padding, so nothing changes size. The bar fills the row down to 2px above
and below the separators and runs to 4px from the cell edge, while the value
keeps its right padding — so for large values the bar extends past the number.

### Consequences

- Good, because the bar reads as a row-spanning magnitude, like Evidence.
- Good, because the cell and row sizes are unchanged (asserted by a test).
- Good, because negative bars simply grow from the right.
- Bad, because the CSS relies on a negative-margin/padding trick that is not
  obvious from the rule names, and it assumes the base cell padding.

## More Information

- [Design & DX §4.10](../design-and-dx.md#410-typography-is-a-feature)
- `tests/browser/test_preview.py::test_bar_fills_row_without_growing_it`
