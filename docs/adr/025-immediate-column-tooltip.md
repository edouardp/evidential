---
status: superseded by ADR-029
date: 2026-10-12
deciders: edouard
---

# ADR-025: An Immediate Custom Tooltip for Column Descriptions

## Context and Problem Statement

A column description (`info`, or a DuckDB comment / Arrow field metadata) renders
as a **ⓘ** in the header. It used the native `title` attribute, so the tooltip
appeared only after the browser's ~1s delay, and the icon set `cursor: help`
(the `?`) to hint at it. Both made a small, frequently-needed description feel
sluggish and noisy.

## Decision Drivers

- The description should appear at once on hover.
- The tooltip must not be clipped by the scroll container.
- Do not add a special cursor (the header is already a sort target).

## Considered Options

1. A custom tooltip shown on `mouseenter`/`focus`, with no `help` cursor.
2. Keep the native `title` attribute.
3. A CSS-only `::after` tooltip.

## Decision Outcome

Chosen option: "Custom tooltip". The **ⓘ** carries `aria-label` (no `title`) and
shows a single `position: fixed` element appended to `document.body` — chosen so
the scroller's `overflow` cannot clip it — on `mouseenter`/`focus`, removed on
`mouseleave`/`blur` and on scroll/resize/re-render. `cursor: help` is removed;
the cursor is left to the surrounding header.

Option 3 was rejected because an absolutely-positioned `::after` inside the
sticky header is clipped by the scroller's `overflow`.

### Consequences

- Good, because the description appears immediately.
- Good, because it is not clipped and works in the fullscreen dialog.
- Good, because `aria-label` keeps it available to assistive technology.
- Bad, because it is bespoke JavaScript rather than a platform feature.
- Bad, because a fixed tooltip must be hidden on scroll/resize to stay aligned.

## More Information

- [Technical architecture §6.5](../technical-architecture.md)
- `frontend/src/table.js` (`showTooltip`/`hideTooltip`)
- Related: [ADR-023](023-duckdb-column-comments.md), [ADR-024](024-arrow-field-metadata.md)
- **Superseded by [ADR-029](029-native-header-tooltip.md)**: the native tooltip
  is back, now on the whole header cell.
