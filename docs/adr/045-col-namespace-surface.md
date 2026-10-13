---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-045: The `col` Namespace Exposes Only Chain Entry Points

## Context and Problem Statement

`col` was the implementation module (`column.py`, later `_column.py`), so
`col.` completion listed everything defined or imported there — `Column`,
`ColumnGroup`, `CURRENCY_CODES`, and transitively `Mapping`, `Any`, `Literal`,
`validate_options`. None of those can be used in the fluent chain, so they are
noise in the editor's completion popup (Marimo, VS Code, Pyright). `__all__`
does not help: editors complete module attributes, not just `__all__`.

## Decision Drivers

- Completion on `col.` should show exactly what builds a column.
- Keep the docstrings on the factories, where the editor surfaces them.
- Keep the implementation (and the return types) importable for those who need
  them, without polluting `col`.

## Considered Options

1. Keep one module and rely on `__all__`.
2. Split into a private implementation module and a thin public namespace module.
3. Make `col` an instance of a namespace class with only the factories assigned.

## Decision Outcome

Chosen option: "private implementation + thin public namespace".

- `_column.py` (private) holds `Column`, `ColumnGroup`, `CURRENCY_CODES`, the
  helpers and the factory implementations.
- `col.py` re-exports **only** the factory functions, so `dir(col)` is exactly
  the kinds: `array, bar, boolean, chip, color, currency, date, delta, flag,
  group, html, image, integer, link, logo, markdown, number, percent,
  sparkline, subcolumns, text, url`.
- `Column`, `ColumnGroup` and `CURRENCY_CODES` are exported from the top-level
  `evidential` package instead, for type annotations and reference.

Option 1 was rejected because `__all__` does not constrain attribute
completion. Option 3 works but `from evidential.col import text` no longer
works and a namespace class is less idiomatic than a module.

### Consequences

- Good, because `col.` completion is the discovery surface, and nothing else.
- Good, because the factory docstrings (and their examples) are still shown.
- Note: `col` is a public module, so anything added to it becomes part of the
  completion surface — keep only chain entry points there.
- Note: the return types moved to the top level (`from evidential import
  Column`), not into `col`.

## More Information

- `src/evidential/col.py`, `src/evidential/_column.py`,
  `src/evidential/__init__.py`.
- Extends [ADR-042](042-column-builder-and-settings.md) and
  [ADR-043](043-column-kinds.md).
