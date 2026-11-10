---
status: accepted
date: 2026-10-28
deciders: edouard
---

# ADR-085: Data Tooltips

## Context and Problem Statement

Native titles reused painted labels, so unlabelled stack segments had no
tooltip, percentage labels obscured amounts, and overlapping population dots
exposed only the topmost series. Compact and rounded formats also hid source
precision. Independently maintained tooltip markup would repeat series names,
colours and formatting policies already owned by the marks.

## Decision Drivers

- Inspect underlying values independently of label visibility and placement.
- Name each series and retain units, grouping and available numeric precision.
- Collect overlapping dots without enlarging their visible geometry.
- Support multiline metadata, keyboard use, touch and themed fullscreen views.
- Keep inspection state out of raw data and remove stale state on rerenders.

## Considered Options

1. Add more native `title` strings to individual marks.
2. Create a separate fluent tooltip builder and independent series declarations.
3. Share structured inspection data and one delegated tooltip per widget.

## Decision Outcome

Chosen option: **3**. Mark renderers register structured names, values, colours
and detail rows in a weak DOM registry. A widget-owned controller renders safe
plain-text HTML with line breaks, positions it inside the viewport, and uses a
manual popover to escape scroller clipping and fullscreen stacking contexts.
Managed marks have no competing native titles. Standalone marks keep a textual
fallback. The controller clears presentation state on rerender and destruction.

Names and swatches reuse mark/legend identities. Default stack inspection
includes the category, full amount, share and total; a share-labelled or
normalised stack leads with the named share. Both halves of a neutral category
report its full value. Point inspection considers dots within its small
invisible hit allowance, preferring dots to underlying connectors. Range
inspection reports endpoints and absolute change; box plots expose their five
numbers and outliers. Observation metadata supplies match details without
queries or row lookups during hover.

Numeric inspection expands the source number's decimal spelling and adds
commas rather than applying a rounded display format. Percent values shift the
decimal spelling instead of multiplying floating-point values; currency and
unit context are retained. This preserves the precision available to the
browser; it cannot recover precision already lost during data conversion.

Scalar and graphic columns share `.tooltip()` for automatic inspection,
`.tooltip(False)` to disable inspection, `.tooltip("@field")` for row-bound text
and `.tooltip("First line\nSecond line")` for literal text. Overrides replace
all mark tooltips in the cell. They do not interpret HTML. No second builder
or independently declared series list is introduced.

Picking follows the graphic's structure. Sparklines select one nearest
observation by x-position across their full height; signed-area swatches match
the fill above or below the reference. Stacks and categorical strips select
one segment at a shared boundary. Point plots can collect multiple dots, but
large arrays must not create unbounded lists that exceed the screen. They show
up to **10 distinct entries** by default, selected by distance from the pointer
to the original point centres in screen space. This respects logarithmic scales
and remains independent of combined point glyphs. The chosen entries display in
numeric x-value order, with declaration-order ties. Deduplication does not consume
the limit. All original points and raw values remain available.

`settings(tooltips={"max_entries": 20})` changes the table default;
`.tooltip(max_entries=3)` overrides a column. Limits are positive integers.
The same selection policy applies to touch inspection and keyboard inspection;
the focused mark wins a distance tie so navigating a coincident group can reach
every entry. Geometry is measured only for a candidate group exceeding the cap.

Hover delays are seconds, configured by
`settings(tooltips={"delay": 0.8, "text_delay": 1.5})` and overridden per column
with `.tooltip(delay=..., text_delay=...)`. Defaults are instant graphics and
0.8 seconds for text. A pending delay survives motion within the same item but
is cancelled on leaving, dismissal, rerender or destruction. Once open,
inspection follows marks in the same cell immediately. Keyboard and touch
inspection bypass hover delays.

Column descriptions now use the same controller and text-delay settings,
including whole-header hover and focus when sorting is disabled. See
[ADR-094](094-shared-header-info-tooltips.md), which supersedes the native-header
decision in ADR-029. Header descriptions remain independent of data-cell
`.tooltip(False)` and literal/bound overrides.

Graphic cells receive one keyboard focus stop. Left/Right cycles through
marks, Home/End selects the first/last, and Escape dismisses inspection.
Touch inspection leaves row selection and other click handling intact.

### Consequences

Tooltips expose data even when labels are hidden or use a different format.
Every widget owns its event listeners and popup; old DOM nodes can be collected
without retaining row records. Unit tests cover data contracts and formatting;
Playwright tests cover actual hit geometry, overlap, keyboard navigation,
fullscreen and notebook rendering. Notebook 55 provides a dedicated offline
gallery, and notebook 54 retains match metadata for its categorical strips.

Inspection adds DOM metadata to displayed marks but no synthetic data fields.
Hover geometry is measured only within the current cell. Very long metadata
can still exceed a compact popup; callers should use concise field-bound text
when the automatic observation metadata is unsuitable.

## More Information

- [Tooltip notebook](../../notebooks/55_tooltips.py).
- [ADR-083: Mark Legends](083-mark-legends.md).
- [ADR-084: Named Point Series](084-named-point-series.md).
