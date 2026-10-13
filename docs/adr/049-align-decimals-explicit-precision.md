---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-049: `align_decimals` Respects an Explicit Precision

## Context and Problem Statement

`align_decimals=True` (ADR-013) pads a numeric column to a common precision so
decimal points line up. It computed that precision from the **raw** values'
decimal places and applied it to the column's base format, overriding whatever
precision the format asked for. Two things were wrong:

- `col.percent("share", decimals=1)` (`fmt="pct1"`) rendered three decimals: the
  raw fraction `0.1115` has four places, and `withDecimals` rebuilt `pct1` as
  `pct3` (capped at 3). A fixed format was being widened.
- A percent format renders `value * 100`, so the raw fraction's decimal places
  are two more than the rendered percentage's.

## Decision Drivers

- An explicit precision is already aligned; padding must not undo it.
- Auto base formats (`num`, `pct`, `usd`, …) do need padding.
- The rendered precision, not the raw value's, is what aligns.

## Decision Outcome

Chosen option: "explicit precision wins; scale the auto percent base".

`withDecimals(format, decimals)` now:

1. keeps a format that already carries a precision digit (`num2`, `pct1`,
   `usd0`, …) unchanged — it is already aligned;
2. pads only an **auto** base format (`num`, `pct`, `usd`, …) to the observed
   precision;
3. for the `pct` base, subtracts 2 from the observed places before padding,
   because the rendered value is `value * 100` (clamped to 3).

So `col.percent("share", decimals=1)` renders `45.0%` / `11.2%` under
`align_decimals=True`, while a `fmt="num"` column with `1.5` / `12.25` / `3`
still pads to `1.50` / `12.25` / `3.00`.

### Consequences

- Good, because an explicit format is honoured under `align_decimals`.
- Good, because an auto percent column aligns on the rendered percentage.
- Note: `align_decimals` is effectively a no-op for a column whose format
  already fixes the precision — which is the intent (it is already aligned).

## More Information

- `frontend/src/rows.js` (`withDecimals`), `frontend/src/derived.js`.
- `frontend/test_rows.js`, `frontend/test_table.js`.
- Refines [ADR-013](013-ala-typography-defaults.md).
