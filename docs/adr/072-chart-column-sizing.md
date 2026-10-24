---
status: accepted
date: 2026-10-25
deciders: edouard
---

# ADR-072: Chart Column Sizing

## Context and Problem Statement

Browser automatic table layout treats absolutely positioned marks as having
almost no intrinsic width. A short question column could consequently occupy
more space than a diverging stacked bar, and numeric columns received surplus
space that charts needed for readable marks and labels.

## Decision Drivers

- Useful defaults across mixed text, number and chart tables.
- Preserve native table semantics, grouped headers and physical sub-columns.
- Respect fixed-size sparklines and existing table width and stretch settings.
- Avoid measurement loops, resize observers and per-notebook workarounds.

## Considered Options

1. Require explicit widths in every notebook.
2. Measure all cell content and assign fixed widths in JavaScript.
3. Use native table layout with intrinsic content columns and flexible charts.

## Decision Outcome

Chosen option: **3**. Tables containing flexible charts receive a `colgroup`
whose ordinary columns request their minimum intrinsic width. Mark columns
and legacy bars retain automatic widths and share surplus space. Row numbers
and link indicators are ordinary compact columns. Spanners do not replace the
underlying physical column definitions.

Mark tracks have a minimum width of `10rem`; stacked bars use `18rem` because
several segment labels share one coordinate area. Fixed-size sparklines, chips,
symbols and color fills use their intrinsic content widths rather than growing
as charts. Tables without flexible charts keep their existing layout.

`stretch=False` still uses intrinsic table sizing, including chart minimums;
otherwise charts expand within the available table width. When the minimum
content cannot fit, the existing scroller provides horizontal scrolling.

### Consequences

Text and numeric columns no longer absorb surplus width in mixed chart tables.
Long unwrapped text and headers still contribute their actual minimum content
width. The policy does not promise every segment label will fit: existing label
placement and omission rules continue to apply. On narrow screens, charts may
require horizontal scrolling sooner than the former `60px` minimum.

## More Information

- `frontend/src/column-sizing.js` and `frontend/src/table.css`.
- `frontend/test_column_sizing.js` and browser column-sizing regressions.
- `notebooks/42_stacked_bars.py` demonstrates both stretch modes.
