---
status: accepted
date: 2026-10-25
deciders: edouard
---

# ADR-073: Directional Ranges for Dumbbell Plots

## Context and Problem Statement

A dumbbell connects two observations with independently styled endpoint points.
The range geometry already accepts descending endpoints, but its connector
could neither distinguish decreases by color nor indicate the change direction.
The requested reference uses a black or red connector and a central chevron.

## Decision Drivers

- Compose with the existing range and point API.
- Preserve endpoint order separately from the interval's visual bounds.
- Reuse negative color bindings and existing scale projection.
- Keep endpoint caps, clipping arrows and direction annotations independent.
- Preserve the appearance of existing ranges unless explicitly configured.

## Considered Options

1. Add a separate dumbbell encoding with duplicate endpoint and scale behavior.
2. Add direction options to range encodings and compose endpoint points.
3. Require callers to precompute colors and overlay text arrow labels.

## Decision Outcome

Chosen option: **2**. Ranges accept `color_negative` and `direction_marker=True`
through factories, fluent composition, mapping declarations and updates.

`color_negative` is selected when the second endpoint is below the first,
independent of their individual signs. It supports a constant, a per-row column
reference or a callable, reusing existing mark color preparation. Without a
negative color, the ordinary range color remains in use. Points keep their own
colors. The first and second endpoint bindings are not sorted or mutated.

The optional marker is an unfilled chevron centered on the visible connecting
range, pointing from the projected first endpoint to the projected second.
Logarithmic and reversed scales therefore preserve the displayed direction.
Equal or fully clipped endpoints have no chevron; missing endpoints suppress
the range as before. The marker uses the connector's resolved color. On filled
ranges it sits above the band rather than inheriting its translucent opacity.
It has no separate interaction or accessible label: the owning mark retains
its original endpoint values. Short spans may place the marker under endpoint
points, consistent with declared paint order.

Endpoint caps and off-scale arrows retain their existing semantics. In
particular, `cap="arrow"` marks off-scale endpoints, while `direction_marker`
indicates change within the range. Bar negative-color semantics are unchanged.

### Consequences

Existing dumbbells require only two range options to show signed change.
Validation stays shared across declaration paths. One small DOM element per
nonzero directed range uses the existing coordinate area and scales on resize;
no measurement observers or new chart domain calculation are needed.

## More Information

- `src/evidential/marks.py` and `src/evidential/configuration.py`.
- `frontend/src/visualizations.js` and `frontend/src/table.css`.
- `tests/test_dumbbell.py`, `frontend/test_dumbbell.js` and browser regressions.
- `notebooks/48_dumbbell_plots.py` demonstrates the reference and edge cases.
