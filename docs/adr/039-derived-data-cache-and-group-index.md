---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-039: Cache Derived Table Data and Index Group Descendants

## Context and Problem Statement

Profiling showed that every page change recomputed dataset ranges, statistics,
and decimal alignment. Python summary overrides scanned every detail row for
each measure and subtotal. Large decimal-alignment arrays could also exceed
JavaScript's function-argument limit.

## Decision Drivers

- Optimize measured costs while preserving formatting and grouping semantics.
- Make cache invalidation explicit and bound retained state to one dataset.
- Verify operation counts and output correctness rather than brittle timings.

## Considered Options

1. Recompute all derived values on every interaction.
2. Introduce virtualization or server-side paging first.
3. Cache the current dataset projection and build a group-descendant index.

## Decision Outcome

Chosen option: one projection per widget in `RowPipeline`. Rows, columns,
options, search text, sort settings, and hidden columns determine the cache key.
Pagination and selection reuse it. Group visibility has a separate revision
key, so toggling a group does not recompute statistics and scales. Every model
change for rows, columns, or options explicitly clears the cache, including
changes with the same array identity. Disposal clears retained references.
Synchronous model changes to several data traits coalesce into one render in
the next microtask; disposal suppresses queued renders. Python refreshes send
their prepared traits together with `hold_sync`.

Decimal alignment uses a streaming maximum rather than spreading an array
into `Math.max`. Python `apply_aggregations` indexes each detail row under its
ancestors once, then retrieves descendants directly for each subtotal.

### Consequences

- Good, because page navigation no longer scans the full dataset.
- Good, because descendant lookup scales with rows and hierarchy depth rather
  than the product of rows and subtotal count.
- Bad, because caches and ancestor indexes retain additional row references.
- Bad, because direct frontend data mutations must emit model change events.
- Bad, because grouped tables still render all visible rows; this is not
  virtualization.

## More Information

- [Measured scenarios and reproduction commands](../performance.md).
- Extends [ADR-037](037-renderer-module-boundaries.md) and
  [ADR-009](009-grouping-sets-for-grouped-totals.md).
