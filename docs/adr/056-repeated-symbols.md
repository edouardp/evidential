---
status: accepted
date: 2026-10-14
deciders: edouard
---

# ADR-056: Repeated Symbols

## Context and Problem Statement

Some tables repeat a mark a number of times: The Economist's "same rate in
consecutive quarters" draws 13 squares for a value of 13, its medal tables draw
one square per medal, and a rating draws stars. Today the only per-cell
visualisations are `bar`, `color`, `chip`, `sparkline` and `delta` — none repeats
a glyph, emoji or image a variable number of times.

## Decision Drivers

- One primitive should cover repeated squares, medals, star ratings and emoji.
- It is a **presentation** of a number, not a new value: sorting, search,
  statistics and export must be unchanged.
- Alignment (left / right / center) is part of the layout, as for any column.
- It should compose with the existing kinds and the group builders.

## Decision Outcome

Chosen option: a new visualisation, `viz="symbols"`.

`col.symbols(name, ...)` draws the (rounded) value as that many repeated
**glyphs** — or `<img>` elements when `image=` is given. The options, in
`symbol_options`:

| option | meaning |
| --- | --- |
| `symbol` | the filled glyph (default `"●"`) — `"■"`, `"★"`, `"▲"`, any emoji |
| `shape` | draw a CSS box instead of a glyph — `"square"`, `"rounded"`, `"circle"` |
| `empty` | the glyph for the unfilled slots (used with `max`) |
| `max` | draw this many slots — `value` filled, the rest `empty`; a floor, not a cap |
| `image` | an image URL/data-URI to repeat instead of a glyph |
| `color` / `empty_color` | the filled / unfilled colour |
| `size` / `gap` | the glyph size and spacing, in `em` |

The usual `align` (`"left"` / `"right"` / `"center"`) positions the run.

`col.repeat(...)` is an alias, and `col.rating(name, max=5, symbol="★",
empty="☆", color="#f59e0b")` is the star-rating shorthand. `Column.symbols(...)`
is the chain method, so a kind can be refined:
`col.number("twice").symbols(symbol="■", color="#2EC1D3")`.

Pair a number with its repeated marks by grouping both under a shared header
(ADR-040): `col.subcolumns("Twice", [col.integer("twice"),
col.symbols("twice", ...)])`.

### Consequences

- Good, because one option set covers squares, medals, stars and emoji, and the
  same column still sorts/searches/exports as a number.
- Good, because `max` + `empty` gives ratings (`★★★☆☆`) without a second feature.
- Good, because `align` makes a run left-, right- or center-aligned like any
  other cell content.
- Good, because `shape=` draws a **CSS box** (square / rounded / circle), which is
  pixel-exact and font-independent — a glyph's shape and width vary by font.
- Note: `max` is a floor — a value above it draws more filled glyphs rather than
  overflowing or truncating; clamp in SQL if a cap is wanted.
- Note: the value is *rounded* to the nearest integer before repeating, so a
  fractional count draws the nearest whole number of marks.

## More Information

- `src/evidential/_column.py` (`symbols`, `repeat`, `rating`, `Column.symbols`),
  `src/evidential/configuration.py` (`SymbolOptions`),
  `frontend/src/visualizations.js` (`renderSymbols`), `frontend/src/cells.js`,
  `frontend/src/table.css`.
- `frontend/test_table.js`, `notebooks/36_repeated_symbols.py`.
- Extends [ADR-020](020-bar-visualisation-geometry.md) and
  [ADR-043](043-column-kinds.md).
