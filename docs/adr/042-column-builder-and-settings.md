---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-042: The `col` Column Builder and the `settings` Bundle

## Context and Problem Statement

The typed `TableOptions` / `ColumnOptions` (ADR-039's configuration module) made
the option *keys* completable, but configuring still means writing nested dicts
by hand. Marimo's completion is driven by the Python language server, so the
goal is an API whose shape the editor can enumerate as you type.

## Decision Drivers

- Completion and signature help in the notebook editor.
- Reuse and composition: a column, or a whole settings bundle, used across
  several tables.
- Typos should fail with a suggestion, not silently.
- One obvious way to set each thing; no parallel APIs.

## Considered Options

1. A `col.*` factory returning an immutable, chainable `Column`, plus a
   `settings(**TableOptions)` bundle.
2. A token list (Altair-style): `options=[opt.title("…")]`, `columns=[col.…]`.
3. Keep only the typed dicts and document them.

## Decision Outcome

Chosen option: "`col` + `settings`".

`col.text` / `number` / `date` / `boolean` / `array` / `sparkline` / `chip` /
`delta` / `link` / `markdown` / `image` / `logo` return an immutable `Column`;
chain methods (`.fmt()`, `.bar()`, `.color()`, `.delta()`, `.sparkline()`,
`.chip()`, `.group()`, `.info()`, …) return a **new** column, so a spec can be
reused. A `Column` is a `Mapping`, so it is accepted anywhere a column
definition is — `columns=[col.number("sales").bar(...)]` **and**
`column_config={"sales": col.number("sales").bar(...)}`. Factories default the
`type` by kind (`delta` → `number`, `chip` → `string`, `sparkline` → `array`) so
an explicit column keeps a sensible type instead of falling back to `string`.

`settings(**options)` validates against `TableOptions` and returns a bundle that
can be splatted (`**REPORT`) or passed as `settings=REPORT`, with per-table
keywords overriding the bundle. Both paths raise `unknown_option`, which
suggests the closest known key.

Option 2 was rejected: a token list is a second way to set every option, it
loses call-site signature help, and it needs a parallel `opt.*` namespace for the
~40 table options. Option 3 was rejected because it leaves the user writing
unbounded nested dicts.

### Consequences

- Good, because `col.` and `settings(` complete in the editor, and a
  `Column`'s chain completes the next method.
- Good, because a column or a settings bundle is reusable and composable.
- Good, because unknown keys fail with "did you mean …".
- Bad, because the builder is a second spelling next to `column_config`; the
  mapping protocol keeps them the same value type, but there are still two ways
  to write a column config.
- Note: `columns=[...]` replaces the inferred columns, so a column whose type the
  factories cannot know (e.g. a delta over a numeric column) must be built from
  the matching factory (`col.number(...).delta(...)`), or the type defaults by
  kind.

## More Information

- `src/evidential/column.py`, `src/evidential/configuration.py`
- `notebooks/32_column_builder.py`
