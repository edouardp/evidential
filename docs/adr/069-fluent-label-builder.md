---
status: accepted
date: 2026-10-24
deciders: edouard
---

# ADR-069: Fluent Label Builder

## Context and Problem Statement

Mark labels used dictionaries and a long `.label(...)` keyword list. Adding
placement preferences and typography makes those declarations harder to read.
The user requested `label.fmt("num0").bold().auto_position("inside end").colour("black")`
and reuse of the existing fluent text API.

## Decision Drivers

- Match text formatting and typography without copying their implementation.
- Keep labels reusable and immutable, with typed completion.
- Retain explicit placement preferences and current mapping declarations.
- Apply the same validation and rendering to every label entry point.
- Avoid exposing column operations such as aggregation or heatmaps on labels.

## Considered Options

1. Add every styling option to the mark constructor's keyword arguments.
2. Subclass the full column builder for annotations.
3. Introduce a dedicated mapping builder and extract shared typography methods.

## Decision Outcome

Chosen option: **3**. The public `evidential.label` namespace starts a fluent
chain and returns an immutable `Label`, also exported from the package.
`Label` implements `Mapping`, so existing mark normalization accepts it directly.
With no explicit binding, it labels the mark's own value. `source`, `text` and
`value` replace each other's bindings. Every refinement returns a fresh spec.

`Column` and `Label` share the private `TextStyle` implementation for formatting,
font selection, weight, italics, text color and figure style. Subclasses select
their existing wire keys, keeping the column schema stable. Label `color` and
`colour` alias `font_color`; the column's existing `color` heatmap remains a
separate operation. Column-only features such as wrapping are not label methods.

Fixed `position` disables automatic fitting. `auto_position` requires a preferred
inside/outside start/end pair and uses [ADR-068](068-automatic-bar-label-placement.md).
Positions accept spaces, underscores and hyphens, serialized as underscores.
Alignment accepts begin/center/end and left/right aliases. Labels also expose
prefix, suffix, minimum width and fixed-label overflow. Stacked bars accept a
label specification in `labels`, applying it independently to every segment;
`share` selects each segment's fraction of the total.

The builder and the existing dictionaries and mark `.label(...)` refinement use
one normalizer and `EncodingLabel` schema. The renderer shares font and figure
style handling with cells, and one label typography helper handles standalone
and stack labels. Automatic fitting measures text after applying typography.

### Consequences

Existing declarations continue to work. Label typography adds optional fields
to the wire schema. The shared typography base preserves immutable subclass
return types. Automatic placement stays bar-specific; other marks retain fixed
placement. This introduces a focused public namespace rather than extending the
column builder with annotation-only methods.

## More Information

- `src/evidential/_text_style.py`, `src/evidential/_label.py`, `src/evidential/label.py`.
- `frontend/src/mark-labels.js`, `frontend/src/visualizations.js`.
- `tests/test_label.py`, `frontend/test_mark_labels.js`, browser conformance tests.
