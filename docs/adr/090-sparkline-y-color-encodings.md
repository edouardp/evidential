---
status: accepted
date: 2026-11-03
deciders: edouard
---

# ADR-090: Sparkline Y-Value Color Encodings

## Context and Problem Statement

Change sparklines supported gradients, while other styles used observation
colors only for visible markers. Bars, line strokes and area fills ignored
those colors. Extending the change-only vocabulary would duplicate the existing
fluent gradient API for cell backgrounds.

## Decision Drivers

- Reuse `.color(scale=..., min=..., max=..., midpoint=..., stops=...)`.
- Compare colors across matching rows and pages without changing coordinates.
- Preserve missing observations, change neutral bands and tooltip swatches.
- Define color ownership for intervals without inventing observations.

## Considered Options

1. Add separate gradient parameters to every sparkline style.
2. Draw a spatial SVG gradient across the whole graphic.
3. Reuse color declarations and look up each observation's y value.

## Decision Outcome

Chosen option: **3**. On a sparkline, `.color()` preserves the visualization
and stores the same `color_options` used by scalar cells. Fluent and mapping
paths share validation. Existing `color_scale`/`color_domain` keywords remain
supported across styles; conflicting declarations are rejected. Row-level
color bindings do not apply to observation arrays.

A shared preparation stage caches a lookup per physical sparkline column over
matching detail observations before pagination. Bounds are inferred separately
from coordinate baselines or fixed through `min`/`max` or explicit stops. Named
palettes, midpoints, alpha stops and clamping reuse the scalar implementation.
Constant inferred series without an explicit midpoint use the palette midpoint. Shared domains can reuse
their range and palette across scalar heatmaps and sparkline observations.

Each bar/dot uses its own observation's y. Each line interval and its area
polygon takes the starting observation's color. Missing observations break
runs; no segment bridges a gap. Uniform graphics retain their single-run
rendering. Color bounds do not alter coordinates, references or area opacity.
An explicit observation `color` overrides lookup for every style. Visible
markers also honor `marker_color` before lookup. Tooltip swatches follow the
observation or visible marker.

Change palettes preserve ADR-070's whole-steady-interval midpoint and delta
semantics. Bounds must contain that interval; an explicit midpoint must match
its center. Explicit value/color stops instead define a direct lookup without
an implicit neutral plateau. Explicit colors/gradients override ordinary
signed-area default fills. Overall constant colors and gradients cannot conflict
silently.

### Consequences

- Authors use the established gradient API rather than a second vocabulary.
- Line/area colors change by interval; smooth interpolation between
  observations is not introduced.
- Multicolor lines/areas need a primitive per interval; uniform runs retain
  their compact representation. Domain inference stores just the extrema.
- Notebook 40 compares all styles; notebook 50 generates the README examples.

## More Information

- [ADR-070](070-change-sparklines.md), [ADR-071](071-shared-numeric-domains.md).
- `src/evidential/_sparkline.py`, `frontend/src/sparkline-colors.js`.
- `tests/test_sparkline_colors.py`, `frontend/test_sparkline_colors.js`.
