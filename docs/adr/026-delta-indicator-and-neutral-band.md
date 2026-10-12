---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-026: Delta Indicator After the Value, Dash for Neutral

## Context and Problem Statement

The delta (`viz="delta"`) put the ▲/▼ indicator *before* the value (`"▲ 12.0%"`),
showed an arrow even for a value within the neutral band (coloured grey but still
▲/▼), and accepted the neutral band only as `neutral_range=[lo, hi]` or
`neutral_min`/`neutral_max`. The indicator reads better after the number, a
neutral value should not look like a rise or fall, and a one-string range is
easier to write.

## Decision Drivers

- Read a column of changes as values, not as arrows.
- A value within the neutral band must be visibly distinct (no arrow).
- A neutral band should be expressible in one config line.
- Green/red must be flippable for measures where lower is better.

## Considered Options

1. Indicator after the value; a dash when neutral; a `"lo:hi"` range string;
   `down_is_good` flips the colours.
2. Keep the indicator first and colour neutral grey while still showing ▲/▼.
3. Show only a dash (no value) for a neutral cell.

## Decision Outcome

Chosen option: "Indicator after the value, dash when neutral". `_renderDelta`
renders the value then the indicator (`"12.0% ▲"`; `symbol_position="left"`
restores the old order), uses a grey dash (`"3.0% –"`) inside `neutral_range`,
and colours by direction — green for an increase, red for a decrease — unless
`down_is_good` flips them. `neutral_range` accepts a `"lo:hi"` string, a
`[lo, hi]` pair, a single ±value, or `neutral_min`/`neutral_max`; these keys work
at the top level of `column_config` / `measure_config` as well as inside
`delta_options`. The indicator lives in a fixed-width (`1em`) box, because ▲, ▼
and – have different advance widths and the numbers must still line up.

Option 3 was rejected: the magnitude of a neutral change is still useful.

### Consequences

- Good, because a change column scans as numbers with a compact direction cue.
- Good, because neutral values are unmistakable and cheap to configure.
- Good, because costs/error rates can mark a decrease as good.
- Bad, because a neutral cell still shows its (small) value next to the dash;
  set `show_value=false` for a bare dash.

## More Information

- [Technical architecture §6.2](../technical-architecture.md)
- `frontend/src/table.js` (`_renderDelta`, `_neutralBounds`)
- `notebooks/11_comparisons.py`
