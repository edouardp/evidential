---
status: accepted
date: 2026-11-15
deciders: edouard
---

# ADR-098: Shared Numeric Gradients and Scale Strips

## Context and Problem Statement

Ranges already support numeric gradients, and sparklines and cell backgrounds
use the same palette vocabulary through `.color()`. Bars and points would benefit
from that lookup too. Readers also need a compact key showing how colors map to
values. The implementation was reviewed visually and merged into main.

## Decision Drivers

- Keep one gradient vocabulary across numeric visualizations.
- Anchor colors to values, independent of row endpoints and clipping.
- Preserve existing solid/categorical color and observation override behavior.
- Explain continuous color on the numeric scale without adding synthetic rows.
- Keep lookup work bounded and reuse scales across point arrays.

## Considered Options

1. Add distinct palette options to every numeric visualization.
2. Restart a gradient across each mark's local bounds.
3. Extend the common numeric lookup and expose its key on `.scale()`.

## Decision Outcome

Chosen option: **3**. `.gradient(scale=, stops=, min=, max=,
midpoint=)` configures the last numeric mark: bar, point, points, range, box plot
or density band. Scalar backgrounds and sparklines accept the same method;
their existing `.color()` declarations remain supported. Gradient and solid color
bindings on one mark are mutually exclusive. Categorical stacks/strips and
repeated symbols/ratings/chips retain their existing APIs.

Horizontal spans paint along numeric x. Points, caps, medians, outliers and
tooltip swatches sample the value lookup. Sparklines use numeric y: bars join
lines/areas in painting a continuous vertical gradient, while points/change
markers sample observation colors. Explicit per-observation colors still override
bars and markers. Gradient bars honor declared alpha directly; solid bars retain
their prior opacity. Density profiles keep their existing opacity masks.

Color bounds default to coordinate bounds for marks; explicit bounds stabilize
meaning through filtering. Out-of-range lookup clamps. Reversed/log coordinates
project the same palette anchors. Shared helpers cache the lookup per encoding
within a track and sample 33 positions plus exact anchors, as in ADR-095.

`.scale(gradient=True)` enables ticks and adds a three-pixel color strip at the
row boundary, outside the body. The strip uses the last gradient-configured mark
in declaration order; later solid overlays do not replace it. A missing gradient
or explicit `axis=False` is an error. `gradient=False` disables only the strip.
The strip uses the same projected numeric lookup, including transparent stops;
categorical `.legend()` remains separate. Endpoint labels align inward without
moving ticks away from their exact numeric positions.

Centered bars paint their zero line in a cell-clipped foreground guide layer.
Points and value labels remain above it; ordinary reference bands, rules and
gridlines stay behind marks. Guides cannot intercept hover or add row overflow.

### Consequences

The same declaration produces comparable colors across supported visuals, with
an optional compact numeric key. Box plots and density bands now also support
reversed coordinates. Bounded CSS sampling approximates LCH interpolation; this
does not promise an exact color at every subpixel. Notebook 63 and generated
README examples provide visual review, with unit/browser tests covering
clamping, alpha, constant/missing data, log/reversed scales, tooltip swatches,
label contrast, guide paint order and row overflow.

## More Information

- [ADR-090](090-sparkline-y-color-encodings.md) covers sparkline y colors.
- [ADR-095](095-rounded-gradient-ranges.md) introduced range gradient painting.
- [Notebook 63](../../notebooks/63_visual_gradients.py) compares the visuals.
- [Graphics API](../api/API.md#visualisations) documents the public methods.
