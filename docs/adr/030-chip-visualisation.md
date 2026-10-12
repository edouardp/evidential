---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-030: Chip Visualisation

## Context and Problem Statement

`viz="color"` fills the whole cell with a colour from the column's scale. Some
values read better as a **badge** — a short, rounded label whose fill carries
the colour while the surrounding cell stays neutral (an AQI score, a status, a
rating). We want the same colour rules as a colour cell, in a compact chip.

## Decision Drivers

- Reuse the existing colour-scale / conditional-colour rules — no second system.
- The text must stay legible on any fill.
- A chip looks best centred; the type default (right for numbers) should not win.

## Considered Options

1. A new `viz="chip"` that fills a rounded rectangle using `calculateColorStyles`.
2. A `chip` flag on `viz="color"` (fill the chip instead of the cell).
3. A CSS-only chip via a `::before` background.

## Decision Outcome

Chosen option: "A new `viz=\"chip\"`". `_renderCell` builds a `span.et-chip` and
fills it with `calculateColorStyles` (a `color_scale` over the range, or
`color_options.conditional_colors`), exactly as a colour cell. `calculateVizRanges`
and the color-scale build include `chip`. The text colour is `contrastTextColor`
— black or white by the fill's **luminance** (`< 0.5` ⇒ white), which is the
"white on darker, black on lighter" the chips want and is more predictable than
WCAG contrast for saturated mid-tones. `_center_chips` sets `align="center"`
unless the column asks otherwise, so the type-derived right/left default does not
win. `content_type="chip"` is an alias.

Option 2 was rejected: a chip is a distinct cell style, not a variation of the
whole-cell fill. Option 3 was rejected: the fill depends on the per-row colour,
which is data, not CSS.

### Consequences

- Good, because chips reuse every colour rule: `color_scale`, `color_stops`,
  `conditional_colors`, `scale_column`, `min`/`max`/`midpoint`.
- Good, because the contrast colour keeps a chip readable on any fill.
- Good, because chips are centred without the caller fighting the type default.
- Note: the text colour uses a luminance split rather than WCAG contrast, so a
  saturated mid-tone gets white text where the whole-cell colour viz would pick
  black.

## More Information

- [Technical architecture §6.4](../technical-architecture.md)
- `frontend/src/table.js` (`_renderCell`), `frontend/src/color.js`
  (`calculateVizRanges`, `contrastTextColor`)
- `notebooks/27_chips.py`
