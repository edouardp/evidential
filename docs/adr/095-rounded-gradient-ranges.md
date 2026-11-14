---
status: accepted
date: 2026-11-14
deciders: edouard
---

# ADR-095: Rounded Ranges with Numeric Gradients

## Context and Problem Statement

Weather-style low–high intervals need pill-shaped ends and a shared temperature
palette. Restarting the full palette at each row's endpoints would assign
different colors to the same temperature. Existing ranges have solid colors
and optional endpoint decorations; their point overlays must keep working.

## Decision Drivers

- Preserve existing range defaults and ordered endpoint semantics.
- Reuse numeric palettes, explicit value stops, alpha and bound validation.
- Keep geometry, colors and overlays independent.
- Avoid per-row measurement or extra layout passes.

## Considered Options

1. Restart a CSS gradient across each range's own bounds.
2. Paint the visible interval from a shared numeric x-value lookup.
3. Introduce a separate weather encoding or chart widget.

## Decision Outcome

Chosen option: **2**. `cap="round"` rounds the interval inside its endpoints.
Edges created by clipping remain square. Existing line/dot caps and overflow
arrows remain independent options. Equal endpoints retain the existing one-pixel minimum;
missing endpoints suppress the interval.

`MarkColumn.gradient(scale=, stops=, min=, max=, midpoint=)` refines only the last
range. It uses the existing `.color()` argument vocabulary and stores a nested
`gradient` color-options mapping in that encoding. Other marks keep their own
colors. Gradient bounds default to the column's coordinate domain, including
shared domains. Explicit bounds keep color meanings stable through filtering.
Color lookup clamps at its bounds; alpha exposes the underlying table backdrop.
Solid color bindings and gradients on the same range are mutually exclusive.
Categorical legends require fixed colors and reject numeric gradient marks.

The renderer samples the common lookup into a CSS gradient cropped to the
visible interval. It samples at most 33 regular positions plus explicit palette
anchors, including narrow value-stop bands. Log/reversed coordinates project
those anchors through the existing scale. Caps/arrows sample their visible
endpoint and direction chevrons/tooltips sample the visible midpoint. Shared
Python validation for numeric gradients serves both ranges and sparklines.

### Consequences

A thin background range, a colored foreground range and independent points can
compose the reference treatment without a new chart kind. Painting uses bounded
sampling plus supplied palette anchors and needs no resize observer. CSS RGB
interpolation between samples approximates the existing LCH lookup. The range
keeps its original values for inspection, including when clipped or reversed.

## More Information

- [ADR-073](073-directional-ranges.md) covers negative colors and direction.
- [ADR-090](090-sparkline-y-color-encodings.md) covers numeric sparkline colors.
- Notebook 48 demonstrates rounded ranges and point overlays.
- Notebook 61 demonstrates historical monthly weather with a city chooser.
- Notebook 50 supplies the generated README example and screenshot.
