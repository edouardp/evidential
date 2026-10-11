---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-007: SSF (Excel Format Codes) for Value Formatting

## Context and Problem Statement

Cells need `$412,300`, `21.0%`, `2024-01-01`, `12 KB`, `1.2M` and arbitrary
user-specified formats. Implementing number/date formatting correctly is a
surprisingly deep problem (negatives, thousands separators, percent scaling,
date serials).

## Decision Drivers

- Fidelity with Evidence, which formats values with SSF.
- A format language users already know.
- Low implementation and maintenance cost.

## Considered Options

1. The `ssf` package (Excel format codes), as Evidence uses.
2. A bespoke formatter.
3. Format in Python and send strings to the browser.

## Decision Outcome

Chosen option: "SSF", wrapped with generated presets (`num0…num4`, `pct0…pct3`,
currencies, `num0k`/`num1M`, dates) and auto-scaling base formats (`num`, `usd`,
`pct`) that choose decimals and units from the column range. Special codes
`bytes`, `duration`, `roman` and `flag` are handled before SSF.

### Consequences

- Good, because a format code behaves the same here as in Evidence.
- Good, because `#,##0.0`, `mmm-yy` and friends come for free.
- Good, because formatting runs in the browser, so it can respond to rules and
  column formats without a round-trip.
- Bad, because SSF is a JavaScript dependency.
- Bad, because format codes are less readable than f-strings.

## More Information

- [Design & DX §4.4](../design-and-dx.md#44-formatting-is-somebody-elses-hard-problem)
- [`frontend/src/format.js`](../../frontend/src/format.js)
