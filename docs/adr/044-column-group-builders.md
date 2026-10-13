---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-044: Column Group Builders

## Context and Problem Statement

ADR-040 gives shared-header sub-columns a per-column label: members that carry
the same `subcolumn_group` cluster and share one leaf header. ADR-042/043 add
`col.*` builders and `settings(...)`. Writing a group by hand is still
repetitive and fragile: forget `.subcolumn("Latest")` on one member and it
silently drops out; misspell the label and the group splits in two — both only
visible at render time. The same applies to a spanner (`column_group`).

## Decision Drivers

- Declare the group **once**; a member cannot lose the label.
- Keep the members adjacent by construction.
- Reuse the existing renderer (ADR-040 already clusters by label).
- Compose with the `col.*` kinds and the `settings(...)` bundle.
- One obvious way to name a group; the dict form stays for schema-driven cases.

## Considered Options

1. Keep only the per-column `.subcolumn(label)` / `.group(label)` methods.
2. A group builder returning a `Sequence[Column]` that sets the label on every
   member, accepted directly in `columns=[...]`.
3. Merge the members into one composite column.

## Decision Outcome

Chosen option: "Group builder".

`col.subcolumns(label, columns, *, group=None, highlight=None)` sets
`subcolumn_group=label` on every member (and optionally the enclosing
`column_group` and a `highlight`). `col.group(label, columns, *,
highlight=None)` sets `column_group=label` — the builder counterpart of
`column_groups={label: [...]}`. Both return a `ColumnGroup`: an immutable
`Sequence[Column]` carrying its `kind`, `label` and `members`, so it can be
splatted (`*col.subcolumns(...)`) and reads back as
`col.subcolumns('Latest', [...])`.

`columns=[...]` flattens any sequence that is neither a name (`str`) nor a
`Column`/mapping, recursively, so a group is written inline and groups nest::

    EvidentialTable(rows, columns=[
        col.text("country"),
        col.subcolumns("Latest", [
            col.number("gdp").fmt("num1").red_negatives(),
            col.text("gdp_period").font_color("#808080"),
        ], group="Economy"),
        col.group("Economy", [
            col.number("inflation"),
            col.number("unemployment"),
        ], highlight="#eef2ff"),
    ])

Members may be `col.*` columns, bare names or mappings, and may themselves be
groups. The renderer is unchanged: it already clusters equal `subcolumn_group`
labels and `column_group` paths (ADR-040), so this is purely a construction
shortcut. A `Column` is a `Mapping` and a name is a `str`, so neither is
mistaken for a group.

Option 1 was rejected: it leaves the two silent failure modes. Option 3 was
rejected in ADR-040 (it loses independent alignment and visualisation).

### Consequences

- Good, because the label and contiguity are structural: every member is
  labelled, and renaming "Latest" happens in one place.
- Good, because groups nest naturally (`group=` on a sub-column group, or a
  group inside a group) and compose with the kinds and the chain.
- Good, because the renderer and `column_groups` are untouched; the dict form
  remains for data-driven schemas.
- Bad, because `col.group` / `col.subcolumns` are a second spelling next to
  `column_groups` / `.group()` / `.subcolumn()`. The builders are the ergonomic
  path; the dict and methods remain.
- Note: `columns=[...]` now accepts nested sequences. A `Column` is a
  `Mapping`, so existing column lists are unaffected.

## More Information

- `src/evidential/column.py` (`ColumnGroup`, `subcolumns`, `group`),
  `src/evidential/table.py` (`_flatten_columns`).
- `tests/test_column_builder.py`, `notebooks/32_column_builder.py`.
- Extends [ADR-040](040-shared-header-subcolumns.md) and
  [ADR-042](042-column-builder-and-settings.md).
