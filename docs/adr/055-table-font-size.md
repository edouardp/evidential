---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-055: Table-level `font_size` (Absolute or Relative)

## Context and Problem Statement

The table font size is fixed at **0.75rem** (Tailwind's `text-xs`, Evidence's
density). A dense table wants exactly that, but a small table (a league table, a
few KPI rows) reads better a little larger. `theme={"font_size": …}` could
change it, but it is buried in the theme map and absolute-only — there is no way
to say "one step bigger than the shared baseline".

## Decision Drivers

- A small table should be able to sit slightly above the baseline without
  restating the base value.
- A dense table keeps the default.
- One obvious option, consistent with the rest of the table options.

## Decision Outcome

Chosen option: a top-level `font_size` option, absolute or relative.

- **Absolute** — any CSS length (`"14px"`, `"1rem"`) sets the table font size
  directly.
- **Relative** — a number, or a `"+2"` / `"-1"` string, is added to the shared
  baseline in **0.0625rem (1px) steps**: `+2` → baseline + 0.125rem.

The CSS gains `--et-font-size-base: 0.75rem` (the baseline) and
`--et-font-size: var(--et-font-size-base)`. The renderer sets `--et-font-size`
from `fontSizeValue(opts.font_size)` (falling back to `theme.font_size`), where

```js
fontSizeValue("+2")  -> "calc(var(--et-font-size-base, 0.75rem) + 0.125rem)"
fontSizeValue("14px") -> "14px"
```

so a relative value scales with the baseline rather than a hard-coded number.
`font_size` overrides `theme.font_size`; the two are otherwise interchangeable.

### Consequences

- Good, because a small table reads `font_size="+1"` and a dense one leaves it
  out, both relative to one baseline.
- Good, because an absolute value still works for an exact size.
- Note: the step is 1px (0.0625rem) — a deliberately small increment; `+4` is
  the old 0.75rem → 1rem jump. **Everything** scales together — header, body,
  controls, and the title / subtitle / caption / footer chrome — because each is
  sized in `em` against `--et-font-size`, not a fixed rem.

## More Information

- `src/evidential/configuration.py` (`TableOptions.font_size`),
  `frontend/src/table.js` (`fontSizeValue`), `frontend/src/table.css`.
- `frontend/test_table.js`, `tests/test_column_builder.py`.
- Relates to [ADR-013](013-ala-typography-defaults.md).
