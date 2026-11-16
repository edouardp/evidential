---
status: accepted
date: 2026-11-16
deciders: edouard
---

# ADR-100: Shared Light and Dark Themes

## Context and Problem Statement

Table UI colours partly inherited the host, axes assumed black, and
DimensionGrid forced a white surface. Authors should not need two copies of
every column declaration. Arbitrary colour inversion would change categorical
identities, gradient ordering and intentional white or brand colours.

## Decision Drivers

- One consistent API for tables, live tables and DimensionGrid.
- Respect a notebook's explicit theme before the operating system preference.
- Preserve literal colours unless adaptation is requested, and preserve alpha.
- Keep marks, scale strips, legends and tooltip swatches in agreement.
- Preserve table state and source data when switching schemes.
- Retain the painted-background contrast implementation from ADR-099.

## Considered Options

1. Apply a CSS inversion filter to the entire widget.
2. Require light/dark pairs for every colour.
3. Separate UI tokens from data colours, with optional perceptual adaptation.

## Decision Outcome

Chosen option: **3**. `color_scheme="auto"|"light"|"dark"` is shared by
tables and DimensionGrid; `auto` is the default. Explicit widget settings win,
then host theme attributes/classes or CSS `color-scheme`, then the OS preference.
Host detection crosses shadow roots. ADR-101 extends automatic detection for
embedded islands and adds `theme_source` overrides. Changes to host attributes and OS
preferences update existing widgets; listeners are disposed with the widget.
Printing temporarily uses the light scheme and restores the previous mode.

UI surfaces, text, rules, stripes, axes, positive/negative status, focus styles,
legends, tooltips, scrollbars and fullscreen/frozen surfaces use shared tokens.
Existing `theme` overrides remain exact. The table now paints a scheme surface
by default; `theme={"background": "transparent"}` opts into host transparency.

Named palettes receive dark variants automatically. Sequential light-to-dark
palettes become surface-to-bright ramps; other palette hue/lightness sequences
remain ordered. `adapt_colors=False` preserves user literals by default.
With `True`, a monotone CIELAB lightness transform raises dark colours, preserves
hue and alpha, and reduces chroma to fit sRGB. Custom gradient anchors use the
same transformation before interpolation. Numeric bounds and threshold values
are untouched. Adaptation is deterministic, not dependent on the current page
or observed values. It cannot guarantee that every category remains perceptually
distinct, especially at small sizes or low opacity.

`color.theme(role, alpha=1)` returns a serializable semantic colour token.
Roles are `surface`, `neutral`, `text`, `muted`, `accent`, `positive`, `negative`.
Neutral means the surface, making a red–neutral–blue gradient meaningful in
both schemes. Literal white continues to mean white. `color.fixed(value)` opts
an individual literal out of adaptation. Both work anywhere a colour is
accepted, including data-supplied colours and gradient stops. Theme overrides
themselves remain ordinary CSS colours rather than semantic declarations.

Per-widget presentation compilation resolves only known colour fields and
palettes. Source rows and model metadata stay unchanged. Dynamic colour fields
and observation overrides use the same resolver via weakly associated compiled
specifications. No global rendering mode or whole-dataset recolouring is used.
Theme compilation is cached by source metadata identity and scheme. A scheme
change rebuilds presentation and colour scales while retaining sort, search,
selection, collapsed groups and pagination offsets. Search focus survives host
theme changes. Fullscreen dialogs receive the same tokens as their inline table.

### Consequences

Light and dark widgets can coexist in the same notebook. Existing literal
colours remain exact unless authors enable adaptation. Custom HTML, background
images, composite CSS border strings and arbitrary CSS variables are not
rewritten. Explicit text colours and translucent marks can still produce poor
contrast; use semantic text colours or omit explicit text colours to let the
existing painted-background contrast resolver decide.

Unit tests cover colour transforms, semantic/fixed declarations, compilation,
cache isolation, scheme precedence and lifecycle disposal. Browser tests cover
both modes, live switching, frozen/fullscreen surfaces, palette/legend/tooltip
agreement, print restoration and the shared DimensionGrid. Notebook 64 supplies
the README's executable light/dark examples.

## More Information

- [ADR-099](099-painted-background-contrast.md): alpha-aware text contrast.
- [ADR-098](098-shared-numeric-gradients.md): shared numeric gradient geometry.
- [Notebook 64](../../notebooks/64_light_dark.py): examples and live selector.
