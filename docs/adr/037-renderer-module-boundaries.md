---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-037: Separate Renderer Processing, Cells, and Lifecycles

## Context and Problem Statement

The renderer grew to nearly two thousand lines spanning row processing, cell
visualizations, layout, interaction, and asynchronous lifecycle management.
Changes were difficult to test without constructing the entire widget.

## Decision Drivers

- Preserve rendering and interaction behavior during the refactor.
- Test data processing without DOM or widget-model dependencies.
- Give timers, animation frames, and observers explicit owners.
- Keep the shipped artifact a single ESM bundle.

## Considered Options

1. Retain a single renderer class.
2. Split the class into inheritance or prototype mixins.
3. Use pure processing functions, cell renderers, and lifecycle controllers.

## Decision Outcome

Chosen option: explicit module boundaries. `rows.js` processes records without
mutating them; `cells.js` formats and decorates cells; `visualizations.js`
renders bars, deltas, and sparklines; `dom.js` supplies presentation utilities.
`interactions.js`, `loading.js`, and `viewport.js` own event behavior and
asynchronous work. Controllers receive callbacks and DOM nodes rather than the
entire renderer. `table.js` orchestrates model state, headers, rows, and chrome.

Private forwarding methods and the legacy fullscreen-state alias have been
removed from `EvidentialTableRenderer`. The renderer calls the owning helpers
and controllers directly. Internal helpers are imported from their defining
module rather than re-exported through unrelated modules. Documentation lives
beside the implementation it describes. Tests exercise controls and controller
behavior rather than keeping old renderer wrappers alive.

The existing anywidget entry point and bundle remain unchanged. Controllers
dispose timers, observers, and scheduled layout frames when the widget closes.

### Consequences

- Good, because pure row functions and lifecycles can be tested independently.
- Good, because cell content branches retain common final decoration.
- Bad, because maintainers must understand the explicit module interfaces.

## More Information

- Extends [ADR-005](005-layer-responsibilities.md).
- Builds on [ADR-010](010-gt-style-location-rules.md) and
  [ADR-014](014-committed-frontend-bundle.md).
