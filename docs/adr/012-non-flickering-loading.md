---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-012: Non-Flickering Live Updates

## Context and Problem Statement

Dragging a slider fires many live queries. If each update clears and rebuilds
the table, the user sees a flicker or a flash of "Processing…" on every tick,
which is worse than briefly showing stale data.

## Decision Drivers

- The table's layout must not jump during an update.
- Fast updates should not show a loading state at all.
- Slow updates should communicate progress without a jarring flash.

## Considered Options

1. Clear and rebuild on every update, with a spinner.
2. Delay the overlay, keep the size stable, and fade between states.
3. Never show a loading state.

## Decision Outcome

Chosen option: "Delay, stabilise, fade". A loading state is only shown if the
update takes longer than ~180ms; when shown, the current data fades into a
dimmed "Processing…" overlay over 600ms, and the new data is revealed
immediately when it arrives. A per-page-size `min-height` baseline keeps the
table from shrinking.

### Consequences

- Good, because fast updates swap rows in place with no flicker.
- Good, because slow updates keep the table on screen and stable.
- Bad, because the renderer owns more timing state (timers, baseline height).

## More Information

- [Design & DX §4.9](../design-and-dx.md#49-loading-should-not-flicker)
- `notebooks/04_live_demo.py`
