---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-043: Column Kinds as the Entry Point

## Context and Problem Statement

ADR-042 introduced `col.*` factories and an immutable chain. The guiding
principle for the surface is **maximise discoverability, minimise
configuration**: a user should be able to say what a column *is* once and get a
sensible table. The first question — is this a number, a percent, a currency, a
delta, an image, a URL? — is the column's **kind**, and it should be the entry
point, not something assembled from a type plus a format code.

The original factories were inconsistent: `col.number` / `col.text` chose a
type, but `col.delta` / `col.chip` / `col.image` / `col.link` chose a
visualisation or content kind. "Currency" and "percent" sat awkwardly between
the two.

## Decision Drivers

- Completion in the editor should list the columns a user is likely to want.
- Common columns should need no configuration at all.
- Kinds that carry a real decision (which currency; a proportion vs an
  already-percent value) should force that decision explicitly.
- One obvious entry point; the chain refines.

## Considered Options

1. **Kinds as factories.** `col.*` names the kind and sets a baseline; the
   chain refines it.
2. **A `fmt` helper namespace only.** Keep `col.number` and add
   `fmt.currency` / `fmt.percent`; no new factories.
3. **A token list** (Altair-style `options=[opt.…]`).

## Decision Outcome

Chosen option: "Kinds as factories".

A `col.*` factory names the column's **kind** and sets its **baseline**: the
type, and a default format and/or visualisation. The kinds are:

| Kind | Baseline |
| --- | --- |
| `text`, `number`, `integer`, `percent`, `currency`, `date`, `boolean`, `array`, `flag` | type + default format |
| `bar`, `color`, `chip`, `sparkline`, `delta` | number/array/string + a visualisation |
| `link`/`url`, `image`, `logo`, `markdown`, `html` | string + content kind |

The two kinds that carry a decision make it explicit rather than guessing:

- `col.percent(name, whole=False, decimals=None)`: `whole=False` is a proportion
  (`0.153` → 15.3%), `whole=True` is an already-percent value (`15.3` →
  15.3%). Omitting `decimals` lets the renderer scale.
- `col.currency(name, code="usd", decimals=None)`: `code` is one of
  `CURRENCY_CODES` and is validated; omitting `decimals` lets the renderer
  scale.

`.fmt("…")` remains the escape hatch for codes the kinds do not cover
(`num0k`, date codes, `bytes`…). Every factory and every chain method carries a
docstring naming the option and showing an example, so the editor's completion
popup explains the API in place.

Option 2 was rejected because it leaves `percent`/`currency` off the completion
list and keeps them off the "what kind of column is this?" question. Option 3
was rejected in ADR-042.

### Consequences

- Good, because the kind list is the discovery surface: `col.` enumerates the
  columns a user reaches for.
- Good, because the common case needs no configuration (`col.currency("sales")`
  auto-scales; `col.percent("share")` picks decimals), while a real decision is
  forced (`whole=`, `code=`).
- Good, because an unknown currency or out-of-range `decimals` fails at the call
  with a suggestion, not at render.
- Bad, because some kinds overlap the chain modifiers (`col.bar` is sugar for
  `col.number(...).bar()`, `col.flag` for `.fmt("flag")`). This is deliberate:
  the factory is the fast path, the chain is the refinement, and both produce the
  same `Column`.
- Note: the kind list is curated; adding to it is a deliberate act, not an
  automatic format-per-factory.
- Note: `col.currency` defaults to the auto-scaling code, which the renderer
  may format differently in cells than in the statistics row — a pre-existing
  frontend detail, not a property of the kind.

## More Information

- `src/evidential/col.py`, `src/evidential/_column.py`,
  `tests/test_column_builder.py`
- `notebooks/32_column_builder.py`
- ADR-042 (the builder and `settings`)
