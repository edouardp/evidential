---
status: accepted
date: 2026-11-01
deciders: edouard
---

# ADR-088: Measured Pages for Expanded Tables

## Context and Problem Statement

Expanded tables estimated their page size from the first body row. Wrapped
cells and synthetic headings/summaries invalidate that estimate. The inline
"never shrink" height baseline also prevented the body from shrinking after
viewport or header changes, causing overflow or clipped footer controls.
GitHub issue [#3](https://github.com/edouardp/evidential/issues/3) records the
Playwright reproductions.

## Decision Drivers

- Use the available dialog width and height for complete rows.
- Reserve all heading levels, statistics, axes, notes and navigation.
- Keep record order and exact boundaries when adjacent pages fit different counts.
- Preserve inline page size and location when closing the dialog.
- Bound measurement work and avoid observer/render feedback loops.

## Considered Options

1. Continue estimating every row from the first row's height.
2. Use the tallest observed row and change a global fixed page size.
3. Measure rendered pages and retain explicit record-offset boundaries.

## Decision Outcome

Chosen option: measured pages with record-offset boundaries in expanded mode.
Inline mode retains its configured fixed-size pagination and height baseline.
Expanded mode drops that baseline and the inline width constraint. Flex layout
reserves the natural height of chrome and gives the remaining height to the body.

`TableViewport` measures the whole table and body, including synthetic rows and
top/bottom axes. It estimates capacity from that body, then brackets a fitting
page with at most twelve measurement/render probes. Stable geometry is cached,
and resize notifications schedule coalesced work outside observer delivery.
Changes to root/table size, data, page, statistics or viewport trigger refitting.

`ExpandedPages` records visited page starts and capacities. Changing the current
capacity preserves its start and invalidates only subsequent boundaries. Moving
forward starts at the exact previous end; moving backward restores a visited
capacity. Filtering, sorting or changing the underlying projection resets this
history. Display-row projection receives detail bounds before decorating them
with section headings, continuations and summaries.

[ADR-089](089-collapsible-display-sections.md) extends these offsets to display
slots when groups are closed: each closed group counts as one slot while its
heading height is measured normally. Folding resets the measured page history.

Expanded navigation shows the current page and exact record range, with Previous
and Next controls. It does not invent a total page count: unvisited pages can fit
different numbers of records. Inline navigation retains its exact page fraction.

### Consequences

- Good, because variable-height data and synthetic rows no longer overflow an
  otherwise feasible expanded page, and resizing can both shrink and grow it.
- Good, because fitting cannot skip records by multiplying a changed capacity
  by the current page index.
- Good, because closing restores the inline page and configured sizing.
- Bad, because variable pages cannot display an exact final page count without
  rendering the entire dataset in advance.
- A header plus a single record taller than the available height cannot fit as
  a complete page. Keep that one record accessible with native scrolling rather
  than truncating its content or hiding navigation.

## More Information

- Extends [ADR-037](037-renderer-module-boundaries.md).
- Preserves the display-only row projection in
  [ADR-064](064-display-only-row-layout.md).
- Covered by frontend controller/pagination tests and Playwright regression
  tests in `tests/browser/test_fullscreen_fitting.py`.
