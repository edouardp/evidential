---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-047: Inference-Preserving Column Specs

## Context and Problem Statement

The type-driven defaults (ADR-022) and metadata descriptions (ADR-023/024) are
computed from the data and applied when a column is inferred. An **explicit**
column (`columns=[...]` or a mapping without a `type`) restates it, so listing
or reordering columns threw the inference away: a bare name (`columns=["gdp"]`)
forced `string`, and a mapping without a `type` did the same. Migrating the
notebooks to the fluent `col.*` style needs a way to include a column — to
order it, or to change one thing about it — without restating what it is.

## Decision Drivers

- The fluent chain should be the way to configure every column.
- Listing columns should be about order and annotation, not retyping.
- One rule for "what is this column": if you don't say, we infer.

## Considered Options

1. Require every listed column to name an explicit kind.
2. `col.auto(name, **overrides)` returns a spec with no `type`, resolved from the
   inferred definition; a spec with no `type` (including a bare name) does the
   same.

## Decision Outcome

Chosen option: "an explicit `col.auto`, and no `type` means infer".

`col.auto(name, **overrides)` returns an immutable `Column` with **no `type`**.
`_coerce_columns` resolves any spec with no `type` — a `col.auto`, a bare name,
or a mapping without a `type` — by starting from the inferred definition for
that name, then applying the spec's own options over it. In `column_config`,
where options are merged onto the inferred column (ADR-036), an auto value keeps
the inferred type already: `column_config={"gdp": col.auto("gdp").fmt("usd0")}`.

So all of these preserve the inferred type, format, alignment and `info`::

    columns=["city", col.auto("gdp").bar(color="#93c5fd"), col.auto("year")]
    column_config={"gdp": col.auto("gdp").fmt("usd0")}

The resolution normalizes the spec's aliases **before** merging, because the
inferred definition carries explicit ``False`` defaults that would otherwise
shadow a camelCase alias (`redNegatives`). As part of the migration,
`Column.fmt_column(column)` was added (Evidence's ``fmtColumn`` — a per-row
format code) — the one column option that lacked a chain method.

### Consequences

- Good, because `columns=[...]` becomes a way to order and annotate, and the
  fluent chain is the way to change anything.
- Good, because `col.auto` is the explicit spelling of the same rule, and it
  reads well in a `column_config`.
- Bad / note: a bare name in `columns=[...]` changes from `string` to inferred,
  and a mapping without a `type` likewise. For a name that is not in the data,
  the fallback is still `string`.
- Good, because the notebooks can move to the fluent style without losing the
  type-driven defaults.

## More Information

- `src/evidential/_column.py` (`auto`), `src/evidential/table.py`
  (`_with_inferred`).
- `tests/test_column_builder.py`, `notebooks/08_column_options.py`.
- Relates to [ADR-022](022-type-driven-column-defaults.md),
  [ADR-036](036-persistent-column-configuration.md) and
  [ADR-042](042-column-builder-and-settings.md).
