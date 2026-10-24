---
status: accepted
date: 2026-10-25
deciders: edouard
---

# ADR-071: Shared Numeric Domains

## Context and Problem Statement

Separate measure columns inferred independent ranges. Repeated fixed bounds and
color scale-column references could not express a domain pooled from several
columns. The user requested fluent membership in a shared quantitative domain
so bars and background colors remain comparable across different headers.

## Decision Drivers

- Shared numerical meaning independent of presentation groups and sub-columns.
- Combined bounds across marks, scalar columns and sparkline observations.
- Optional shared palettes and diverging midpoints.
- Stable scales across pagination and column visibility changes.
- Immutable reusable configuration with the same validation on update paths.
- Explicit conflicts instead of silent per-column overrides.

## Considered Options

1. Repeat fixed bounds and palettes on every column.
2. Infer scales from column header groups.
3. Add named numeric domains with reusable fluent specifications.

## Decision Outcome

Chosen option: **3**. Every column builder exposes `.domain(name_or_spec)`.
`domain.numeric(name)` returns an immutable `Domain` mapping with `include_zero`,
`bounds`, `palette` and `midpoint` refinements. Names identify domains within one
table; an object supplies configuration rather than global mutable state.
Declarations merge only when their explicit settings agree.

Python column normalization canonicalizes the mapping. Shared preparation merges
member declarations before resolving callable bindings, and all construction
and update paths use it transactionally. Local explicit scale bounds, color
bounds/stops and sparkline color endpoints are rejected in favor of domain
bounds. Conflicting palettes, midpoints and zero policies raise errors. Axes and
gridlines remain local. The initial shared-domain implementation supports linear
scales; existing independent logarithmic scales are unchanged.

The row pipeline pools every configured member over matching detail rows before
pagination, including hidden members. Plain numeric columns contribute values,
mark columns their plotted ranges (including stack totals), and sparkline columns
their observations. No synthetic row contributes. Existing physical-column range
keys retain independent domains even when field names repeat. Rendering consumes
the pooled range without reintroducing an independent zero policy. Centered
members symmetrize the whole domain. Fixed bounds override inference.

Color encodings use the domain palette and midpoint when configured; bar and
line fill colors remain independent. Shared palettes use LCH interpolation;
conditional colors and contradictory per-column interpolation are rejected. Change sparklines also share their inclusive
steady interval with other domain members. Its values map to the palette's
midpoint, with independent ramps below/above it, through the existing color-scale
result and value-projection mechanism. Thus heatmap and change colors agree even
inside a nonzero-width neutral interval. Change members must agree on that range.

### Consequences

Filtering recomputes inferred bounds; pagination and visibility do not change
their meaning. Shared domain inference scans the participating observations in
the row-preparation cache. Existing columns without domain membership preserve
their independent behavior. A reusable object shares settings across tables,
while fixed bounds are necessary for cross-table numerical comparisons.

## More Information

- `src/evidential/_domain.py`, `src/evidential/domain.py`.
- `frontend/src/shared-domains.js`, row preparation and color-scale helpers.
- `tests/test_domain.py`, `frontend/test_shared_domains.js`, browser conformance tests.
- `notebooks/47_shared_domains.py`.
