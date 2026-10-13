---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-050: Negative Styling — `.neg(color=, bracket=)`

## Context and Problem Statement

`red_negatives` (Evidence's `redNegatives`) is a boolean: it colours negative
values the theme's red and nothing else. It cannot use another colour, and it
cannot render accounting-style brackets (`($1,234)`), which is what financial
tables usually want.

## Decision Drivers

- Names move on the fluent chain (ADR-042/043), not raw booleans.
- Colour and brackets are independent choices.
- Keep the Evidence-compatible option working.

## Decision Outcome

Chosen option: `Column.neg(color=None, bracket=False)`.

It sets three column options:

- `red_negatives=True` — negative marking is on;
- `negative_color` — the colour (when `color` is given); otherwise the theme's
  negative colour is used;
- `bracket_negatives` — when `bracket`, a negative value is wrapped in
  parentheses, replacing the sign (`-$1,234` → `($1,234)`).

So:

```python
columns=[
    col.currency("profit").neg(),                              # red negatives
    col.currency("cash_flow").neg(color="#b91c1c", bracket=True),
]
```

The frontend renders a negative cell with the `et-negative` class (its colour
comes from `--et-negative`, overridden inline by `negative_color`) and, when
`bracket_negatives` is set, replaces a leading `-` and wraps the text.

`red_negatives(...)` remains as the Evidence-compatible boolean; `.neg()` is the
richer spelling and is what the notebooks use.

### Consequences

- Good, because one method carries both choices, and the chain reads well.
- Good, because `bracket=` gives accounting formatting without a custom code.
- Good, because raw option names stay wire-stable and `redNegatives` keeps
  working.
- Note: `bracket_negatives` only brackets a value the formatter rendered with a
  leading `-`; a format that puts the sign elsewhere is left as-is.

## More Information

- `src/evidential/_column.py` (`neg`), `src/evidential/configuration.py`,
  `frontend/src/cells.js`.
- `tests/test_column_builder.py`, `frontend/test_table.js`,
  `notebooks/08_column_options.py`, `notebooks/30_subcolumns.py`.
- Relates to [ADR-042](042-column-builder-and-settings.md) and
  [ADR-043](043-column-kinds.md).
