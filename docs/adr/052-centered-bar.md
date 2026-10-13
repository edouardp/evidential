---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-052: The Centred (Diverging) Bar

## Context and Problem Statement

The bar view (ADR-020) fills from one edge: a rectangular bar behind the number,
growing right for positive and left for negative. The Economist's "league table"
bars read differently: a **centre line** (zero), the bar growing left or right by
*how much* the value is above/below zero, and the number on the **opposite** side
of the line. The two encodings answer different questions — the fill bar ranks
magnitudes, the centred bar shows signed deviation.

## Decision Drivers

- Signed deviation is a distinct, common need ("% change vs 0").
- Keep it a mode of `.bar()`, not a new visualisation.
- Reuse the existing bar cell, label and colours.

## Decision Outcome

Chosen option: `bar_options.center`, exposed as `.bar(center=True)`.

The renderer (`renderBar`), when `center` is set:

- draws a centre line at 50% of the bar area (`.et-bar-axis`);
- gives the bar half the cell per side, so its width is
  `min(100, |value| / max(|min|, |max|) * 100) / 2` percent, anchored to the
  centre — growing right for a positive value (`.et-bar-right`) or left for a
  negative one (`.et-bar-left`);
- puts the label on the opposite side of the line
  (`.et-bar-label-left` / `.et-bar-label-right`).

Colour follows the existing rule (`bar_color`, `bar_color_negative`), and
`fit_to_data` still controls the range. `pad` (a px number or a CSS length)
insets the **bar** from the top and bottom of the row; the centre line is never
padded, so it stays full height and continuous.

### Consequences

- Good, because signed deviation is now a first-class bar mode.
- Good, because it composes with the existing label, colour and `hide_labels`.
- Note: the label and the bar each get **half** the cell, so the centred cell
  has a wider `min-width` (`8rem`) and the label is `nowrap` to keep a wide value
  on its own half without riding over the bar or the neighbour.

## More Information

- `frontend/src/visualizations.js` (`renderBar`), `frontend/src/table.css`,
  `src/evidential/_column.py` (`bar`), `src/evidential/configuration.py`
  (`BarOptions`).
- `frontend/test_table.js`.
- Extends [ADR-020](020-bar-visualisation-geometry.md).
