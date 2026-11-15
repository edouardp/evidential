---
status: accepted
date: 2026-11-15
deciders: edouard
---

# ADR-097: Shared Marker Shapes and Rotation

## Context and Problem Statement

Point marks only draw circles, repeated symbols have three CSS shapes, and
ratings depend on the chosen font's star glyphs. Adding distinguishable point
shapes should give these APIs a common contract, including outlines, rotation,
legends, overlapping colors and related sparkline markers.

## Decision Drivers

- Choose shapes that remain distinguishable at small table sizes.
- Keep names typed and rotation arbitrary without expanding an enum per angle.
- Preserve default circles and existing point/series outline defaults.
- Reuse geometry across point marks, legend keys and repeated shapes/ratings.
- Preserve raw observations and bounded pixel-cluster behavior.

## Considered Options

1. Encode angles in names such as `triangle270` and `cross45`.
2. Add independent CSS polygons or Unicode glyphs to each renderer.
3. Share typed shape names and SVG paths with a separate numeric angle.

## Decision Outcome

Chosen option: **3**. `MarkerShape` is a public Literal of `circle`, `square`,
`rounded`, `triangle`, `diamond`, `cross`, `star` and `bar`. Rounded squares
remain for compatibility. Triangles are equilateral, rotate about their centroid and point up at zero; diamonds
are narrower than a square rotated 45°. Stars have five points. Bars are vertical
at zero degrees; rotate them 90° for a horizontal bar. Regular polygons
that resemble circles at these sizes are excluded.

`angle=` is clockwise degrees, finite and normalized modulo 360. Circle rotation
has no visible effect. Size is the nominal unrotated bounding box, in pixels for points
and em for repeated symbols; rotation may extend beyond that box. The same
`outline=True|False|color` contract applies to every geometric shape. Existing
outline defaults remain: direct scalar/array points use their theme outline;
named point series and sparkline markers default to no outline.

A shared frontend path registry draws noncircle points, legend keys, geometric
symbols, star ratings and visible sparkline markers. Default scalar circles
retain their lightweight native CSS rendering. Familiar filled/hollow Unicode
geometric glyphs resolve to the shared paths; arbitrary text/emoji and images
retain their existing modes. Explicit shape takes precedence over glyph choice.
Rating empty slots remain hollow shapes; disabling outlines also hides those
hollow strokes. Repeated-symbol size is applied once, fixing the previous
container-times-symbol scaling.

Point clusters group only equal shape, effective angle and size, with the
existing one-pixel bound over the whole cluster. Noncircle composites clip
colored sectors to the same marker path and preserve outline segments. Sector
boundaries stay in screen coordinates even for rotated shapes, except bars:
their colors occupy equal end-to-end bands along the long axis. At zero degrees
the first declared point occupies the top band; subsequent colors follow below.
The bands rotate with the bar, and each band retains its member's outer outline.
Mixed geometries
keep their original nodes and declaration order. Composites occupy the position
of their last member, preserving paint order against later marks. The sort/sweep remains bounded
by O(n log n), and resize recalculates the presentation without changing data.

Sparkline point/line/area markers use the same options, while bar/change styles
reject them. Visible shaped endpoints and invisible observation hit targets
share explicit observation metadata so nearest-x tooltips include both.

### Consequences

Shapes can reinforce color without divergent APIs or a font dependency. The
small-size and rotation matrix in notebook 62 makes practical legibility easy
to inspect. Python validation is shared by builders, mappings and updates;
frontend, browser and notebook tests cover geometry, outlines, glyph aliases,
cluster compatibility, scale/tooltip behavior and em sizing. The existing
frame-inclusive browser benchmark checks layout/clustering costs.

## More Information

- [ADR-084](084-named-point-series.md) covers named point series.
- [ADR-086](086-segmented-overlapping-points.md) covers pixel-bounded overlaps.
- [Marker demo](../../notebooks/62_marker_shapes.py).
- [Graphics API](../api/API.md#visualisations).
