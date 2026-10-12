---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-008: chroma-js for Colour Scales

## Context and Problem Statement

Heatmap (`viz="color"`) cells need perceptually reasonable interpolation,
diverging scales around a midpoint, explicit value→colour stops, and a
contrast-aware choice of text colour. A subtly wrong heatmap is worse than none.

## Decision Drivers

- Match Evidence's colour output for the same `color_scale`.
- Support linear, diverging (midpoint) and explicit-stop scales.
- Choose black/white text by contrast.

## Considered Options

1. `chroma-js`, ported from Evidence's `color-scale-utils`.
2. A hand-rolled RGB/LAB interpolation.
3. `d3-scale-chromatic`.

## Decision Outcome

Chosen option: "chroma-js", because it is what Evidence uses, so the same
palette and midpoint produce the same colours, and it provides luminance and
contrast directly. `color.js` ports `createColorScale`, `calculateVizRanges`
and `colorStylesFromHex` on top of it.

Color and chip scales use inferred data bounds unless explicitly overridden.
`scale_mode` chooses chroma's interpolation mode (default `lch`); named
table-level palettes are resolved in the same way as column-level palettes.

### Consequences

- Good, because named presets (`green`, `blue`, `red`, …) and custom palettes
  behave like Evidence.
- Good, because text colour is chosen from actual contrast.
- Bad, because it adds a bundle dependency (~ tens of kB).
- Bad, because diverging-scale edge cases (midpoint outside the range) need
  explicit handling.

## More Information

- [Design & DX §4.5](../design-and-dx.md#45-colour-scales-are-ported-not-invented)
- [`frontend/src/color.js`](../../frontend/src/color.js)
