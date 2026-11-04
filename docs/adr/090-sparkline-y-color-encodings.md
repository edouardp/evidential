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
- Color continuous graphics by height without assigning colors to outgoing intervals.

## Considered Options

1. Add separate gradient parameters to every sparkline style.
2. Paint continuous lines/areas with a vertical SVG gradient in data-y space.
3. Reuse color declarations and look up each observation's y value.

## Decision Outcome

Chosen options: **3 for discrete marks, 2 for continuous graphics**. On a sparkline, `.color()` preserves the visualization
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

Each bar/dot uses its own observation's y. Lines and areas paint a continuous
vertical gradient in the chart's data coordinates, including along slopes
between observations. The initial outgoing-interval approach was replaced on
2026-11-04: a point has no ownership of the following interval. The same height
now has the same color across every run in a chart. Missing observations break
runs; no segment bridges a gap. Color bounds clamp colors without altering
coordinates or references.

SVG gradients use `userSpaceOnUse`, anchored to the same y transform as the
geometry. A bounded set of samples approximates the shared LCH lookup in SVG's
RGB interpolation, retaining exact palette, midpoint and explicit stop anchors.
This preserves close stops used for sharp threshold bands. Explicit-stop scales
disable Chroma's quantized cache, which otherwise conflates nearby values.
Alpha is emitted as stop opacity. Gradient IDs use a document-wide counter
shared across independently loaded widget bundles.

Area-only `fill_opacity` accepts a scalar in [0, 1] or a `(baseline, edge)` pair.
The pair ramps opacity from the reference (zero by default, clamped to the
plotted range) toward each end of the plotted y range, multiplying any color
alpha without changing the outline. Plain areas retain default 0.22 opacity;
y-gradient areas default to 1 so explicit alpha colors control their fill.
Thus a stock-style constant outline can have a transparent-baseline fill,
while a single `.color(stops=...)` declaration can express signed/severity bands
or transparent-to-green with red only above a threshold.

An explicit observation `color` overrides lookup on bars, dots and change
rectangles. On lines/areas it applies only to visible markers. Visible markers
also honor `marker_color` before lookup. Tooltip swatches follow the painted
line/area lookup or visible marker, rather than an invisible observation override.

Change palettes preserve ADR-070's whole-steady-interval midpoint and delta
semantics. Bounds must contain that interval; an explicit midpoint must match
its center. Explicit value/color stops instead define a direct lookup without
an implicit neutral plateau. Explicit colors/gradients override ordinary
signed-area default fills. Overall constant colors and gradients cannot conflict
silently.

### Consequences

- Authors use the established gradient API rather than a second vocabulary.
- Line/area colors vary continuously with y and can switch sharply at explicit
  thresholds; one path per run retains compact geometry and preserves gaps.
- Vertical paint adds a bounded number of stops per chart, independent of the
  number of observations. Explicit anchors are retained. Domain inference stores
  just the extrema; ordinary areas without a gradient retain their solid fill.
- Notebook 40 compares all styles and demonstrates vertical fades, thresholds,
  severity bands and clamping; notebook 50 generates the README examples.
- Notebook 60 shows explicit observation colors produced in SQL: windowed
  team maxima/minima highlight every tied biggest win/heaviest loss in a full
  football season's bar sparklines. Its offline snapshot stores raw fixtures,
  so the same query computes colors on either data source at execution time.
  Available league/year windows are discovered from scored national fixtures;
  July–June/calendar-year controls update the existing widget in a separate
  reactive cell. Recorded coverage is displayed instead of implying that every
  selectable date window is a complete official season.

## More Information

- [ADR-070](070-change-sparklines.md), [ADR-071](071-shared-numeric-domains.md).
- `src/evidential/_sparkline.py`, `frontend/src/sparkline-colors.js`.
- `tests/test_sparkline_colors.py`, `frontend/test_sparkline_colors.js`.
