---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-013: A List Apart Typography as Defaults

## Context and Problem Statement

A table's readability is mostly typography: alignment, figures, rules and white
space. These are cheap to get right and expensive to ignore, but most table
libraries leave them to the user.

## Decision Drivers

- Readable output with no configuration.
- Independent, well-argued guidance rather than personal taste.
- Overridable when a font or brand requires it.

## Considered Options

1. Adopt Richard Rutter's "Web Typography: Tables" principles as defaults.
2. Use the browser's defaults.
3. Ship an opinionated, heavily styled theme.

## Decision Outcome

Chosen option: "ALA principles as defaults": text left-aligned and numbers
right-aligned by column type; headings aligned with their data; **lining
tabular numerals** by default (`font-variant-numeric: lining-nums tabular-nums`)
with a `figure_style` escape hatch for fonts whose oldstyle figures are wanted;
`align_decimals`; `stretch=False` for content-sized columns; minimal furniture
(`row_lines=False`, no frame); and white space or group-size stripes for
grouping.

### Consequences

- Good, because the default output is readable without tuning.
- Good, because fonts that default to oldstyle figures are corrected.
- Good, because each principle has an explicit option to opt out.
- Bad, because the defaults differ from raw browser behaviour and from some
  other table libraries.

## More Information

- [Design & DX §4.10](../design-and-dx.md#410-typography-is-a-feature)
- Richard Rutter, [*Web Typography: Designing Tables to be Read, Not Looked At*](https://alistapart.com/article/web-typography-tables/)
- `notebooks/19_typography.py`
