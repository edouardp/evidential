---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-076: Sparkline Reference Origins

## Context and Problem Statement

The WDI trade table needs a 20-year exports/imports area sparkline with green
above 100% and red below it. Existing signed areas split at zero, which cannot
express a nonzero reference while preserving the original percentage tooltips.

## Decision Drivers

- Preserve original observations, missing calendar years and percentage tooltips.
- Keep the reference visible even when every observation lies on one side.
- Reuse signed-area coloring and the shared sparkline renderer.
- Keep factory, fluent and mapping declarations consistent.

## Considered Options

1. Subtract the reference in SQL and display transformed values.
2. Build a special renderer for the WDI notebook.
3. Add an explicit reference to ordinary sparkline settings.

## Decision Outcome

Chosen option: **3**. Ordinary sparklines accept `reference` and optional
`reference_color`. The reference draws a dashed horizontal line with a tooltip
using `y_fmt`, participates in inferred bounds and becomes the area/bar origin.
`signed=True` colors area above the reference with `color` and below it with
the theme negative color. Its default origin remains zero.

Signed fills insert exact line/reference intersections before splitting the
polygons. Missing observations still divide the series into separate runs.
Shared inferred domains include member references; explicit shared bounds
retain precedence. Origins are clamped for fill geometry, and references
outside explicit bounds are omitted. Empty series remain missing indicators.

The shared configuration validator rejects nonfinite references. Reference
colors require a reference, and change sparklines reject references because
their categorical geometry already uses an explicit steady interval.

### Consequences

Threshold comparisons retain their natural units without SQL display strings
or separate tooltip data. The WDI query creates exactly 20 ordered year/ratio
observations ending in the selected year, including null slots for absent
measures or zero imports. Ratios, current amounts and history update together
in one query while preserving the live widget.

## More Information

- `src/evidential/_sparkline.py`, public builders and configuration schema.
- `frontend/src/sparkline.js` and `frontend/src/shared-domains.js`.
- `tests/test_sparkline_reference.py`, frontend and WDI browser tests.
- `notebooks/23_wdi.py` demonstrates the 100% trade reference.
