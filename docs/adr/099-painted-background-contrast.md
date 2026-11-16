---
status: accepted
date: 2026-11-16
deciders: edouard
---

# ADR-099: Contrast Against Painted Backgrounds

## Context and Problem Statement

Translucent fills can display as pale pink but receive white text because
chroma's luminance and contrast operations ignore alpha. Choosing against a
hard-coded white surface would fail on future dark themes, frozen cells,
stripes and host backgrounds. Inside-bar labels have another paint layer and
the solid bar's opacity to consider. Issue #8 documents the failure in 0.2.4.

## Decision Drivers

- Preserve fill transparency and explicit text/label colour choices.
- Use the actual surface, including through anywidget shadow boundaries.
- Support future dark backgrounds without a separate contrast implementation.
- Share composition while preserving existing cell and label contrast policies.
- Avoid per-cell geometry reads and rerunning data preparation for theme changes.

## Considered Options

1. Treat translucent fills as opaque, or always blend them over white.
2. Resolve only the table surface and pass it through the data render context.
3. Share source-over composition and resolve painted DOM layers after layout.

## Decision Outcome

Chosen option: **3**. Pure colour helpers composite a fill over an optional
surface before selecting text or border shades, while retaining the original
fill alpha. An absent/invalid surface falls back to white for detached callers.
Opaque colours retain the existing policies: cells choose the stronger
black/white contrast; chips and mark labels retain their luminance threshold.

`contrast.js` resolves painted surfaces independently of data preparation.
It follows opaque/translucent ancestor backgrounds through shadow hosts and
uses native `Canvas` as the final backdrop. Cell paint order matches CSS:
background, row tint, cell fill, selection tint. Browser-resolved custom/system
colours and modern colour spaces are converted to sRGB. A mark label retains
its associated bar/stack segment, allowing its fill and computed opacity to be
composited over the cell and any full-track bar background. Gradients retain
the existing label-anchor sample. This is not a general SVG scene compositor.

Automatic targets are registered separately from explicit text colours.
Computed styles, shared ancestor paints and colour conversions are cached per
refresh; colour writes follow reads and no geometry measurements are added.
The existing render/resize label pass refreshes contrast after placement.

A controller coalesces host/root theme mutations, row class changes, row hover
transitions and system colour-scheme changes into animation frames. It refreshes
only the current DOM, without invalidating ranges, grouping or data caches.
Watching the current ancestor chain also supports fullscreen relocation.
Listeners/observers are removed on disposal, and queued work becomes inert.

### Consequences

Light, dark, striped, frozen and host-coloured tables share the same paint
resolution path. This prepares contrast for dark mode without introducing a
dark-mode option or changing existing fill opacity. Arbitrary overlapping
graphics and host background images are outside this resolver's scope; those
would need an explicit scene-level model rather than per-pixel screenshots.
Unit tests cover composition, caches, native colour parsing, shadow hosts and
observer disposal. Browser tests cover the reported failure, cell/chip/row/bar
layers, explicit overrides and theme changes without rerendering data.

## More Information

- [Issue #8](https://github.com/edouardp/evidential/issues/8).
- [ADR-098](098-shared-numeric-gradients.md) covers gradient label sampling.
- [Notebook 12](../../notebooks/12_color_scales.py) compares light/dark surfaces.
