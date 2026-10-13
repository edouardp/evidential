---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-053: Named Colour Scales and matplotlib Colour Names

## Context and Problem Statement

Two gaps in the colour vocabulary:

- **Gradients.** Only six named scales existed (`green`, `blue`, `red`,
  `orange`, `purple`, `grey`/`gray`), all two-stop sequential ramps. The
  familiar matplotlib colormaps (`viridis`, `Blues`, `RdBu`, …) were absent.
- **Single colours.** `chroma-js` accepts the ~147 CSS/X11 names (`steelblue`,
  `rebeccapurple`) but not matplotlib's — `tab:blue` and `C0`–`C9` failed.

Worse, an **unknown scale name failed silently**: `resolvePalette` returned
`undefined` and the column fell back to the default light-blue ramp, so a typo
rendered blue with no warning.

## Decision Drivers

- The names people already reach for (matplotlib) should work.
- A typo should fail loudly, not render the wrong thing.
- Keep the bundle small; one source of truth for the names.

## Decision Outcome

Chosen option: "curated matplotlib colormaps + names, validated at both ends".

- **`COLORMAPS`** (in `frontend/src/color.js`) adds 30 matplotlib colormaps —
  the perceptually-uniform `viridis`/`magma`/`plasma`/`inferno`/`cividis`, 16
  sequential (`Blues`, `Reds`, …, `YlOrRd`) and 9 diverging (`RdBu`, `RdYlBu`,
  `RdYlGn`, `coolwarm`, `bwr`, `Spectral`, `PiYG`, `PRGn`, `BrBG`). Each is
  stored as **9 sampled stops** (chroma interpolates between them, visually the
  256-entry LUT). `COLOR_SCALES = { ...COLOR_PRESETS, ...COLORMAPS }` (37 names),
  looked up case-insensitively, so `Viridis` and `viridis` both work. Diverging
  maps pair with `midpoint=`.
- **matplotlib colour names** — `TABLEAU` (`tab:blue`…`tab:cyan`), `C0`–`C9`
  (indexing the Tableau palette) and the single-letter `BASE_COLORS`
  (`b`, `g`, `r`, `c`, `m`, `y`, `k`, `w`) live in `NAMED_COLORS`.
  `resolveColor(name)` maps them to hex; anything else passes through (so a CSS
  name or hex still works). It is applied to the bar colours.
- **Validation.** `configuration.COLOR_SCALES` mirrors the names, and
  `_normalize_column_options` raises `Unknown colour scale 'x'; did you mean …?`
  for a named scale that is not known (a **list** of colours is still left to
  chroma). The frontend also throws in `buildColorVizScale` for the same case,
  so the silent fallback is gone. `tests/release/test_color_scales.py` parses
  the JS and asserts the two lists match, so they cannot drift.

`C0`–`C9` are pinned to matplotlib's **default** prop cycle (`tab:blue` …
`tab:cyan`); a different rcParams cycle is not reflected.

### Consequences

- Good, because `scale="viridis"`, `scale="RdBu"`, `bar_color="tab:blue"` and
  `bar_color="C0"` now work.
- Good, because a mistyped scale fails fast with a suggestion instead of
  silently rendering the default ramp.
- Good, because the cmaps are ~2–4 KB total, not the ~170 of matplotlib.
- Note: the curated set is not exhaustive — add more by appending a stop list to
  `COLORMAPS` and the matching name to `COLOR_SCALES` (the release test enforces
  the pair).

## More Information

- `frontend/src/color.js` (`COLOR_PRESETS`, `COLORMAPS`, `COLOR_SCALES`,
  `NAMED_COLORS`, `resolveColor`), `frontend/src/visualizations.js`,
  `src/evidential/configuration.py`, `src/evidential/_column_options.py`.
- `frontend/test_color.js`, `tests/release/test_color_scales.py`,
  `tests/test_column_builder.py`.
- Relates to [ADR-008](008-chroma-js-colours.md).
