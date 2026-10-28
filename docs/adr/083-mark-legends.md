---
status: accepted
date: 2026-10-28
deciders: edouard
---

# ADR-083: Mark Legends

## Context and Problem Statement

Colour-coded marks expose sources and fills but no visible key. Readers cannot
identify stacked-bar segments or multiple point series without prose outside
the graphic. Keys written separately can drift from their marks. The table's
title area has space on the right, including when multiple columns need keys.

## Decision Drivers

- Derive colour keys from the same definitions as their marks.
- Keep title and subtitle on the left, with compact legends on the right.
- Share one fluent API across stacks, overlays, points, ranges and strips.
- Match the actual rendered column headings and preserve source identities.
- Adapt to available width without adding horizontal overflow.
- Preserve the boundary between data and presentation metadata.

## Considered Options

1. Require hand-written captions listing colour meanings.
2. Add a legend beneath each column header.
3. Collect opted-in column legends in the table's title area.

## Decision Outcome

Chosen option: **3**. `MarkColumn.legend(labels=True, *, outline=False)` adds a colour key for the
whole presentation column. The titlebar contains the existing title/subtitle
block and one accessible legend region, without a redundant visible title.
One group per opted-in visible column is labelled with the same heading resolver
as the table header (including explicit titles, title formatting, all caps,
stub headings and subcolumn joins).

Source headings supply default entry names; an explicitly configured source
column title is used when available separately from the compound mark column.
The compound slot's title never replaces its first segment's identity.
Strip category keys come from the declared `colors` mapping, independently of
the currently visible rows. Lists override names in declaration order;
source/category mappings override selected names. A `None` name omits an entry,
so a connecting range can be left out of a key for overlaid points.
`False` disables the column's legend. Enabled legends are validated both in
builders and canonical dictionaries, and revalidated when columns change.

Fills use a shared mark-colour resolver. Swatches retain theme tokens and
bar/range opacity; point swatches are circular. Explicit negative fills receive
a separate named negative entry. Per-row colour references are rejected: a
colour column alone does not supply category identities. This version does not
add continuous gradient keys or infer categorical chip legends.

The titlebar and keys use flexbox with wrapping. Column and entry names use mid-dark
grey (a theme-aware muted text colour). Each column gets its own row:
`Column name: <wrapping keys>`. Swatch/label pairs never shrink or split across
lines; only complete pairs wrap, with a space between entries and no leading
separator on a wrapped line. Stack/bar swatches are square; point swatches
retain circular geometry. The key is inset from the table's right edge and
entry text stays within its padded boundary. The whole key can move
below the title when space is limited.
`outline=True` on any enabled column draws one thin, theme-aware border around
the combined key. `legend_options.outline` stores this presentation setting
separately from entry-name overrides, and does not outline individual groups.
Keys contain text labels, with decorative swatches hidden from assistive
technology. Legends do not participate in sorting, selection, statistics or
the raw data, and do not change with row search or pagination.

### Consequences

Legends require no separate colour configuration and remain correct after
column visibility, title or theme updates. Immutable label metadata adds a
small canonical configuration surface. Shared series/name/fill helpers provide
a basis for richer per-mark tooltips, but this decision does not change tooltip
content or introduce another tooltip specification. Header/footer placement,
cross-column deduplication, categorical per-row colour keys and continuous
legends remain separate decisions.

## More Information

- [Legend notebook](../../notebooks/54_legends.py).
- [ADR-084: Named Point Series](084-named-point-series.md).
- [Colour-key request](https://github.com/edouardp/evidential/issues/1).
- [Related tooltip request](https://github.com/edouardp/evidential/issues/2).
- [ADR-058: Encoding-Based Columns](058-encoding-based-columns.md).
