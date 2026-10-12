---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-029: Native Header Tooltip on the Whole Cell

## Context and Problem Statement

[ADR-025](025-immediate-column-tooltip.md) replaced the native `title` tooltip
on the header **ⓘ** with a custom, fixed-position tooltip shown on
`mouseenter`/`focus`, to remove the browser's ~1s delay and the `help` cursor.
In practice the custom tooltip only appeared when the pointer was over the small
**ⓘ** glyph, added scroll/resize/re-render bookkeeping, and is bespoke
JavaScript for a platform feature. Column descriptions are short, and the whole
header cell is a more natural hover target.

## Decision Drivers

- The description should appear when hovering the **whole header cell**, not just
  a small glyph.
- Prefer the platform tooltip over bespoke positioning code.
- Keep the **ⓘ** as a visual marker for assistive technology.

## Considered Options

1. Native `title` set on the `<th>` (the whole cell).
2. Keep the custom tooltip but attach it to the cell instead of the icon.
3. A CSS-only `::after` tooltip.

## Decision Outcome

Chosen option: "Native `title` on the `<th>`". `_renderHeader` sets `title` on
the whole header cell when the column has `info`; the **ⓘ** stays as a marker
with `role="img"` and `aria-label` (and `cursor: help`), but carries no `title`
of its own. The custom `showTooltip`/`hideTooltip` code, its scroll/resize
listeners and the `.et-tooltip` styles are removed.

Option 2 was rejected as the same bespoke machinery for little gain. Option 3
was already rejected in ADR-025 (a sticky header clips an absolutely-positioned
`::after`).

### Consequences

- Good, because the whole header cell is the hover target.
- Good, because it is the platform tooltip — no positioning, scroll or resize
  bookkeeping, and it cannot be clipped by the scroller.
- Good, because `aria-label` keeps the description available to assistive
  technology.
- Bad, because the native tooltip delay returns (accepted: the descriptions are
  short and rarely needed mid-interaction).
- Note: this supersedes ADR-025.

## More Information

- [Technical architecture §6.5](../technical-architecture.md)
- `frontend/src/table.js` (`_renderHeader`)
- Related: [ADR-023](023-duckdb-column-comments.md), [ADR-024](024-arrow-field-metadata.md),
  [ADR-025](025-immediate-column-tooltip.md)
