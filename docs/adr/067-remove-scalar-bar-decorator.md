---
status: accepted
date: 2026-10-24
deciders: edouard
---

# ADR-067: Remove the Scalar Bar Decorator

## Context and Problem Statement

ADR-066 made mark factories consistent but retained `.number(...).bar()` as a
second way to declare a labeled bar. The user explicitly requested its removal
now that bar marks own their value labels. Retaining the decorator leaves two
different public models for the same display.

## Decision Drivers

- Make bars quantitative marks with explicit annotations.
- Keep scalar formatting separate from declaring a visual encoding.
- Preserve intentional mark composition and immutable refinement.
- Migrate maintained examples and generated measure columns completely.

## Considered Options

1. Keep the scalar decorator indefinitely.
2. Deprecate it and retain another compatibility implementation.
3. Remove it and migrate declarations to bar marks with explicit labels.

## Decision Outcome

Chosen option: **3**, as requested by the user.

Remove `Column.bar` and the unused classic bar factory in `_column.py`.
Scalar factories (`number`, `integer`, `currency`, `percent`, `auto`, etc.) no
longer offer `.bar()`. There is no forwarding shim or silent conversion.

```python
col.bar("sales", format="usd0", label=True, color="#93c5fd")
col.bar("growth", format="pct1", label=True, center=True)
col.bar("current", label=True).bar("previous").point("target")
```

`MarkColumn.bar(source, ...)` still appends a mark, and its source-free form
refines the last bar. Labels belong to their individual marks. Formatting and
cell styling continue to refine the resulting mark column.

Migrate notebooks and documentation while preserving currency/percentage
formatting and numeric labels. Pivot outputs rebind references to the measure
to each projected field. Comparison tables rebind prior-period marks and keep
change columns free of the original measure's encodings and scale. Independent
field bindings and literal label/color values are not renamed.

### Consequences

This intentionally breaks calls to the removed scalar decorator. Their direct
replacement is `col.bar(source, format=..., label=True, ...)`. Existing raw
Evidence-style `viz="bar"` dictionaries remain accepted; this decision removes
the redundant fluent API, not the dictionary ingestion contract.

Tests assert that scalar builders have no `bar` attribute, verify mark
composition, check projected measure bindings and prevent maintained notebooks
and executable documentation examples from reintroducing the old declaration.

## More Information

- Updates [ADR-066](066-consistent-public-api-preparation.md) and the
  compatibility clause of [ADR-058](058-encoding-based-columns.md).
- [Public API](../api/API.md#consistent-option-names-and-updates).
- `tests/test_api_consistency.py`, `tests/test_pivot.py`,
  `tests/test_comparison.py`, `tests/release/test_documentation.py`.
