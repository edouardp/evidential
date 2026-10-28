---
status: accepted
date: 2026-10-28
deciders: edouard
---

# ADR-086: Segmented Overlapping Points

## Context and Problem Statement

Opaque dots at equal or almost equal positions hide earlier series. Tooltips
can expose every value, but the visible glyph still conceals its composition.
Numeric equality alone cannot identify near-coincident positions across
different scales or table widths. Adjacent-distance clustering could merge a
long chain of observations into one misleading point.

## Decision Drivers

- Show all colours of a coincident group without changing source data.
- Use a one-CSS-pixel bound on the entire cluster, including after resizing.
- Preserve translucent compositing, marker sizes, outlines and inspection.
- Use a quick best-effort calculation instead of expensive clustering.
- Keep README images reproducible from executable notebook examples.

## Considered Options

1. Jitter points away from their numeric positions.
2. Merge numerically equal values, or connect adjacent nearby points.
3. Sweep rendered point centres and paint bounded clusters as segmented circles.

## Decision Outcome

Chosen option: **3**. After layout, the renderer measures point centres and
sorts them horizontally. A linear sweep accumulates compatible points only
while the bounding-box diagonal of the whole group remains at most one CSS
pixel. This conservative bound prevents chaining; sorting plus sweeping costs
O(n log n). Geometry reads precede glyph writes. Resizing repeats the pass.

Only opaque circular points of the same rendered size combine, and a group
must contain different fill colours. Translucent fills or mark opacity retain
ordinary compositing. Differently sized points preserve their size encoding.
Groups use equal SVG pie sectors in declaration order, starting at twelve
o'clock: two colours form vertical halves, three form thirds meeting at the
centre, and larger groups continue the same pattern. Outer arcs retain each
member's outline colour; hidden outlines remain absent.

Original point nodes, source positions and tooltip registrations survive.
They are visually hidden while a decorative composite is painted at their
mean position. Keyboard focus highlights that composite; hover inspection
still includes every underlying named value. A later layout can restore
individual dots without reconstructing data or changing legend identities.
Overlapping tooltip entries sort by numeric x-value; equal values retain
declaration order, independently of sector orientation.

### Consequences

Equal dumbbell endpoints remain distinguishable, and dense named point series
communicate coincidence before hover. No Python API flag or synthetic field
is needed. Approximate groups are bounded best-effort groups, not a statistical
aggregation, and their tooltip retains unrounded source values.

Notebook 48 prints two-, three-, four- and near-coincident examples beside their
graphics, with a translucent control. The README gallery includes sectors and
an open multiline tooltip. Its screenshot registry explicitly hovers the
named example during generation; prose and code remain notebook-derived.
Unit tests cover non-chaining and eligibility; browser tests cover sectors,
outlines, inspection, resize separation and screenshot framing.

## More Information

- [Dumbbell notebook](../../notebooks/48_dumbbell_plots.py).
- [README graphics source](../../notebooks/50_graphics_gallery.py).
- [ADR-085: Data Tooltips](085-data-tooltips.md).
- [ADR-084: Named Point Series](084-named-point-series.md).
