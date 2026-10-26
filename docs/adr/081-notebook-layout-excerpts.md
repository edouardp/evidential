---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-081: Notebook Layout Excerpts

## Context and Problem Statement

The notebook-generated README initially extracts column definitions, suitable
for graphic examples. Table layout examples need their title, notes, rules,
shading and display-row configuration instead. Their prose, real code and
images must retain the same notebook source and freshness checks.

## Decision Drivers

- Show table layout choices before cell graphics in the README.
- Extract actual source, including comments and fluent row-layout chains.
- Keep the existing column excerpt mode and image-only hero intact.
- Avoid handwritten copies of table options in documentation.
- Preserve one named-cell capture registry and provenance workflow.

## Considered Options

1. Maintain manual option snippets alongside the generated images.
2. Generate every example's entire cell, including data preparation.
3. Add an explicit complete-call extraction mode with LibCST.

## Decision Outcome

Chosen option: **3**. An optional `call` suffix on a README notebook marker
selects the cell's complete table factory call. The default selects its inline
`columns=[...]`, while `image-only` continues to suppress code. LibCST locates
the selected syntax span; the generator retains comments, quoting and fluent
chains. A CST transform replaces shared `columns` and `settings` variable
references with `...`, keeping the focus on layout options. Inline definitions
remain visible, and the running notebook still uses the original arguments. Markdown remains a
statically read literal. Missing/ambiguous cells and unknown modes fail.

Notebook 51 owns nineteen layout examples and their paired Markdown cells.
They share six records and a small width/interaction settings bundle, while
the excerpt shows every example's actual layout call. Playwright captures
those same named cells, including indented group details, centered headings
and a non-repeating group-label column, into `docs/img/layouts`. The gallery appears in the
presentation section before the cell graphics section. The existing manifest
and `make readme-check` cover the additional notebook, images and LibCST lock.

### Consequences

Layout examples can display shared column references without pretending they
are self-contained data examples; their source links open the runnable setup.
LibCST is a development dependency, adding no runtime package requirement.
Tests cover both extraction modes, Unicode/source preservation, the executed
notebook and browser output. The two-level example exposed the group builder's
replacement of child paths; it now composes paths as specified in ADR-044.

## More Information

- [Authoring guide](../notebook-documentation.md).
- [ADR-079](079-notebook-generated-readme.md), [ADR-044](044-column-group-builders.md).
- `notebooks/51_table_layouts.py`, `scripts/generate_readme.py`.
