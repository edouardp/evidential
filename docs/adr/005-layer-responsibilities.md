---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-005: Responsible Layers — SQL Shapes, Python Binds, the Browser Paints

## Context and Problem Statement

A table feature can be implemented in the database, in Python, or in the
browser. Without a rule, logic lands wherever it is convenient and becomes hard
to reason about. What is the rule?

## Decision Drivers

- Put each kind of work where the relevant types and capabilities live.
- Respect the JSON boundary from [ADR-004](004-json-wire-format.md).
- Keep the renderer free of business logic.

## Considered Options

1. A single rule: shaping in SQL, binding in Python, pixels in the browser.
2. Do as much as possible in Python.
3. Do as much as possible in the browser.

## Decision Outcome

Chosen option: "The three-layer rule". Data shaping (joins, window functions,
aggregates) is SQL. Anything that needs a Python callable — blank predicates,
text transforms, custom aggregations — runs in Python *before* serialisation.
Per-cell appearance (format, colour, layout) is the browser's job.

### Consequences

- Good, because the renderer stays a pure function of `(value, column_config)`.
- Good, because SQL can push heavy shaping down to the database.
- Good, because callables are never expected to cross the JSON boundary.
- Bad, because the boundary forces results to be materialised (helper columns)
  rather than computed lazily in the browser.

## More Information

- [Design & DX §4.2](../design-and-dx.md#42-three-layers-each-doing-what-it-is-good-at)
- Related: [ADR-006](006-hidden-helper-columns.md), [ADR-010](010-gt-style-location-rules.md)
