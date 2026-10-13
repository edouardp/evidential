---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-038: Typed Configuration with Early Runtime Validation

## Context and Problem Statement

Configuration dictionaries accepted unknown keys and invalid values silently.
The default dictionary, accepted-key list, documentation, and browser consumers
could drift, and typos were difficult to diagnose in a notebook.

## Decision Drivers

- Reject unknown table, column, and nested visualization settings early.
- Preserve Evidence aliases and valid anywidget trait arguments.
- Provide public types without adding a runtime validation dependency.
- Keep one accepted table schema and one default mapping.

## Considered Options

1. Continue using unrestricted dictionaries.
2. Add a third-party validation library or replace dictionaries with dataclasses.
3. Define public `TypedDict` schemas and validate their normalized dictionaries.

## Decision Outcome

Chosen option: public `TableOptions` and `ColumnOptions` types with nested
schemas in `configuration.py`. Runtime validation checks keys, literals,
scalar types, sequences, mappings, required fields, and non-finite numeric
configuration. Errors identify the property path and suggest nearby names.
The accepted table-key set derives from the type rather than a second list.

Validate column settings after alias normalization, through construction,
refresh, `set_column`, and `make_column`. Validate table updates before state
changes. Constructors continue forwarding recognized anywidget trait arguments.
Raw dictionary inputs remain supported; callers may annotate them with the
public types for editor assistance.

### Consequences

- Good, because misspelled options fail where they are supplied.
- Good, because schemas serve both Python typing and runtime checks.
- Bad, because previously ignored unknown keys now raise exceptions.
- Bad, because new configuration features must update their schemas.

## More Information

- Extends [ADR-003](003-evidence-compatible-api.md) and
  [ADR-036](036-persistent-column-configuration.md).
