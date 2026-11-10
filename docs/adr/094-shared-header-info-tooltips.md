---
status: accepted
date: 2026-11-10
deciders: edouard
---

# ADR-094: Shared Header Info Tooltips

## Context and Problem Statement

Column descriptions used native browser titles under ADR-029, while data cells
and graphics now share a widget-owned tooltip under ADR-085. The different
appearance, delay and keyboard behavior make descriptions feel inconsistent.

## Decision Drivers

- Reuse the existing tooltip controller and its safe multiline presentation.
- Keep the entire header cell as the hover target, including its info marker.
- Support focus and touch without interfering with header sorting.
- Retain the same clipping, fullscreen, dismissal and cleanup behavior as data cells.

## Considered Options

1. Keep native header titles alongside the shared data tooltip.
2. Add another custom controller only for header descriptions.
3. Register description-bearing headers with the existing tooltip controller.

## Decision Outcome

Choose option 3, superseding ADR-029. The header builder supplies description
cells to an inspection callback; the renderer registers them in the existing
weak inspection registry. This keeps header layout independent of tooltip state
and avoids a circular dependency between headers and inspection.

Headers with info are focusable even when sorting is disabled. Their descriptions
use plain text with newlines, the normal table/column `text_delay`, and immediate
keyboard/touch inspection. The info glyph retains its accessible description and
help cursor. Managed header titles are removed so there is no competing native
tooltip. Enter/Space sorting remains unchanged. No public API is added.

### Consequences

- One tooltip per widget serves data, graphics and header descriptions.
- Existing delay settings, Escape dismissal, rerender cleanup and fullscreen
  popovers apply equally to header descriptions.
- Standalone header DOM construction does not own inspection state or listeners.
- Regression tests cover hover, focus, sorting, nonsortable headers, delay
  overrides, multiline text safety and fullscreen dismissal.

## More Information

- [ADR-029](029-native-header-tooltip.md)
- [ADR-085](085-data-tooltips.md)
- [Tooltip demo](../../notebooks/55_tooltips.py)
