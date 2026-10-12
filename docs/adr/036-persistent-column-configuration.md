---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-036: Preserve Explicit Column Configuration Across Refreshes

## Context and Problem Statement

Construction, `set_data`, and `set_column` previously normalized column options
differently. Refreshing records could lose formatting, groups, and automatic
link hiding. Generator inputs were also consumed more than once.

## Decision Drivers

- Data refreshes should preserve explicitly configured presentation.
- Evidence aliases should work through every configuration entry point.
- Inferred types should still reflect the current data schema.

## Considered Options

1. Preserve entire rendered column definitions, including inferred defaults.
2. Require callers to repeat every configuration on each refresh.
3. Retain explicit inputs and apply one normalization path to the new schema.

## Decision Outcome

Chosen option: retain explicit column definitions, overrides, and groups.
Omitting these arguments in `set_data` preserves them; supplying a replacement
updates the stored configuration. An empty override/group mapping clears that
configuration. `set_column` updates the retained overrides as well as the
current columns. Schema-derived defaults are inferred again for each dataset.

Normalize aliases and content types before merging overrides onto inferred
defaults. Materialize iterable inputs once. Apply automatic link hiding on both
construction and refresh when columns are inferred.

### Consequences

- Good, because changing rows does not unexpectedly change presentation.
- Good, because inferred defaults remain separate from explicit choices.
- Bad, because the widget retains additional Python configuration state.

## More Information

- Extends [ADR-022](022-type-driven-column-defaults.md).
- Live tables use the same refresh path as ordinary tables.
