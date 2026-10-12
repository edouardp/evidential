---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-028: Column Groups from Dotted Column Names

## Context and Problem Statement

Hierarchical columns required either a `column_groups={"Group": [...]}` mapping
or a `column_group` on each column definition. That is verbose, and it
duplicates information the SQL already carries: a query can name its columns
`"GDP Measure.GDP nominal"` and the result knows its own header structure. For
the common single-level case we want the grouping for free.

## Decision Drivers

- A query should be able to carry its own header structure in the column names.
- Zero configuration for the common case.
- Explicit configuration must still win (regroup, rename, opt out).
- The leaf label should keep the existing `formatTitle` behaviour.

## Considered Options

1. Infer `column_group` from a dotted column name when none is set.
2. Keep the explicit-only mapping.
3. Add a separate column-definition key for groups, leaving names alone.

## Decision Outcome

Chosen option: "Infer `column_group` from a dotted column name". In
`_resolve_column_groups`, a column with no explicit group whose name contains a
dot takes everything before the **last** dot as its group
(`"GDP Measure.GDP nominal"` → group `"GDP Measure"`); extra dots become a
nested path (`"Root.Sub.Leaf"` → `["Root", "Sub"]`, rendered as two header
levels). Only the group is derived — the name is untouched, because the
frontend's `formatTitle` already shows the trailing segment as the leaf label.
An explicit `column_group` or a `column_groups` entry is applied first and wins.

Option 2 was rejected: it forces a parallel mapping that the names already
express. Option 3 was rejected as an unnecessary second convention.

### Consequences

- Good, because a SQL result groups itself with no Python mapping.
- Good, because dots nest, covering multi-level headers.
- Good, because explicit configuration still overrides, so nothing is lost.
- Bad, because a dotted name now *always* groups; to show one verbatim, set both
  `column_group` and `title`. A name with no dot is unaffected.
- Note: the split is on the **last** dot, matching `formatTitle`, so
  `"a.b.c"` groups under `a` > `b` and labels the leaf `c`.

## More Information

- [Design and DX §4.6](../design-and-dx.md)
- `src/evidential/table.py` (`_resolve_column_groups`)
- `frontend/src/table.js` (`groupPath`, `groupKey`)
- `notebooks/24_dotted_groups.py`
