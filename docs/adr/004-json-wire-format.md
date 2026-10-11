---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-004: JSON Wire Format for Rows, Columns and Options

## Context and Problem Statement

anywidget transports state from Python to the browser as JSON. We must decide
what crosses the boundary and how the renderer is configured.

## Decision Drivers

- The browser must render without calling back into Python.
- The payload should be inspectable and easy to debug.
- Configuration should be separate from data.

## Considered Options

1. Three traits: `rows`, `columns`, `options` (plus `loading`).
2. One opaque `data` blob.
3. Have the browser read the Python object's schema lazily.

## Decision Outcome

Chosen option: "Three traits". `rows` is a list of JSON-safe dicts, `columns` is
a list of sparse column definitions, and `options` holds table-level settings.
`loading` is a separate boolean so a live update can dim the table without
touching the rows. Renderer metadata (see [ADR-006](006-hidden-helper-columns.md))
is underscore-prefixed to avoid clashing with data columns.

### Consequences

- Good, because the payload is plain JSON and easy to log.
- Good, because options can change without re-sending rows.
- Good, because the renderer is a pure function of the three traits.
- Bad, because anything non-serialisable (callables, `Decimal`) must be
  resolved in Python first (see [ADR-005](005-layer-responsibilities.md)).

## More Information

- [Technical architecture §5](../technical-architecture.md)
