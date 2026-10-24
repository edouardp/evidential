---
status: accepted
date: 2026-10-24
deciders: edouard
---

# ADR-070: Change Sparklines

## Context and Problem Statement

The user requested small rectangular marks for increase, hold-steady and
decrease, resembling a football win/draw/loss sequence. Ordinary bar sparklines
encode magnitude by length; this display instead needs three fixed positions
and optional magnitude coloring, with a configurable neutral interval.

## Decision Drivers

- Equal rectangles, centered for steady and shifted half a height for up/down.
- An inclusive, configurable steady interval, defaulting to zero alone.
- Preserve event order, missing slots, structured input bindings and tooltips.
- Anchor the neutral color independently of asymmetric data or domain endpoints.
- Comparable colors across rows and pages, with explicit domain overrides.
- Reuse the sparkline entry point and existing color-scale implementation.

## Considered Options

1. Extend ordinary bar scaling with special baseline and clipping rules.
2. Add a separate public visualization factory and independent data parser.
3. Add `type="change"` with a dedicated renderer and shared data normalization.

## Decision Outcome

Chosen option: **3**. `col.sparkline` and the fluent `.sparkline(...)` support
`type="change"`, `steady=(low, high)`, optional `color_scale` and `color_domain`.
The Python factory and mapping preparation use one validator. The public
`SparklineType` literal alias defines line, area, bar, points and change once,
shared by the factory, fluent method and configuration schema. Change-only
settings cannot silently affect another style; incompatible geometry settings
are rejected. Palette lists and pairs are copied before storage.

Input observations are changes or signed outcomes, not absolute measurements to
difference. Every slot has equal width, including missing observations. The
shared DOM-free sparkline normalizer handles scalar, pair and structured data.
`x` labels tooltips; it does not change event spacing for this categorical
sequence. Null and invalid values leave gaps. Rectangles have equal height;
up/down shift half a rectangle height. An accessible SVG summary counts states.

Without a gradient, up/down use the theme accent/negative colors and steady is
gray; a constant `color` overrides all states. With `color_scale`, values within
the inclusive steady interval map to palette coordinate 0.5. Values below it
interpolate from 0 to 0.5, and values above it from 0.5 to 1, each using its own
domain span. Thus neutral stays the middle color on asymmetric and one-sided
input. Even palettes use their interpolated midpoint. Explicit domains must
contain the steady interval and clamp colors beyond their endpoints.

The row pipeline prepares a color function for each physical change column
across matching rows before pagination. Filters recompute inferred domains;
paging, selection and collapse reuse the cached scale. Standalone sparkline
rendering derives its scale from the supplied series. Existing line, area, bar
and point sparklines retain their geometry and normalization.

Notebook 46 reads the local football results parquet, selects a calendar year
and domestic league, and includes each participant's recorded matches in other
competitions. A searchable top table summarizes the chronological result
sequence; selecting a stable team identifier updates a second table with match
details and labeled goal-margin bars. Widget creation is independent of controls;
separate reactive cells update their existing models under `hold_sync`. A real
England 2024 snapshot provides an offline fallback, with source attribution.

### Consequences

Magnitude is conveyed only through optional color; three-position geometry stays
stable across rows. Explicit color domains permit cross-table comparisons. The
pipeline adds preparation work proportional to the matching observations only
when an inferred gradient domain is needed. The notebook's year and competition
choices follow the available local data, or the single bundled snapshot.

## More Information

- `frontend/src/sparkline-data.js`, `frontend/src/change-sparkline.js`.
- `src/evidential/_sparkline.py`, `tests/test_change_sparkline.py`.
- `frontend/test_change_sparkline.js`, browser sparkline and live notebook tests.
- `notebooks/46_change_sparklines.py`, `notebooks/sql/46_football_outcomes.sql`.
