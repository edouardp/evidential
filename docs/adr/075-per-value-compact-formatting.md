---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-075: Per-Value Compact Formatting

## Context and Problem Statement

The WDI trade comparison needs amounts such as 234.5B and 1.7T in the same
column. The existing `num` preset chooses a shared unit from the column range,
which can make smaller economies' amounts difficult to read. Labels, ordinary
cells and axes need the same formatting while retaining numeric source values.

## Decision Drivers

- Select units independently for each value.
- Retain one decimal place, signed amounts and existing missing-value behavior.
- Reuse the shared formatter across display surfaces.
- Preserve existing `num` behavior and explicit SSF formats.

## Considered Options

1. Preformat amounts into strings in SQL.
2. Change the existing `num` preset to select units per value.
3. Add a `compact` format using the browser's international number formatter.

## Decision Outcome

Chosen option: **3**. `.fmt("compact")` uses a cached English
`Intl.NumberFormat` with compact notation and one decimal place. It selects
K, M, B or T per value, handles rounding across unit boundaries and ignores
the column range. Zero displays as `0`; missing, nonfinite and textual inputs
retain the shared formatter's fallback handling.

The preset applies equally to columns, fluent labels and axes. Values remain
numeric for sorting, statistics and CSV export. The `num` preset and explicit
SSF codes retain their existing behavior.

### Consequences

Mixed-magnitude amounts remain readable without SQL presentation logic or
changes to the wire format. Compact suffixes follow English international
number formatting, including uppercase K. Callers state the physical unit or
currency in the heading or label as appropriate.

## More Information

- `frontend/src/format.js` and `frontend/test_format.js`.
- `notebooks/23_wdi.py` demonstrates trade amounts and balances.
