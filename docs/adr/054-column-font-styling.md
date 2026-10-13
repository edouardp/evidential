---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-054: Column Font Styling and an Empty Title

## Context and Problem Statement

Two small DX gaps in the column chain:

- **Bold / italic** required switching the column to `markdown` and embedding
  `**…**` / `*…*` in every value (which also brings markdown parsing, and is
  wrong for a label column whose data is plain text).
- **`title=""`** was ignored: the header rendering used
  `col.title || formatTitle(col.name)`, so an empty string (falsy) fell back to
  the formatted column name — there was no way to blank a header.

## Decision Drivers

- Styling is a column property, not cell content.
- A blank header should be expressible.
- Keep the option names CSS-shaped (they already are: `font`, `font_color`).

## Decision Outcome

Chosen option: `.bold()` / `.italic()` and a nullish title check.

- `Column.bold(value=True)` sets `font_weight="600"` (dropping it when
  `value=False`); `Column.italic(value=True)` sets `font_style="italic"`. The
  escape hatches `font_weight(value)` / `font_style(value)` take a raw CSS value
  (`"700"`, `"oblique"`). `font_weight` / `font_style` are new column options.
- The frontend applies them to the cell in `decorateCell`, beside `font_color`.
- The header title now uses `col.title ?? formatTitle(col.name)`, so `title=""`
  renders an empty header (only `null`/absent falls back).

This is **body-cell** styling only; the header keeps its own weight.

### Consequences

- Good, because a label column can be bold without markdown, and a data column
  can be italic.
- Good, because `title=""` blanks a header (useful for a table that already has
  its own lead-in, as in the income-statement demo).
- Note: bolding/italicising the **header** is not part of this; if needed it can
  reuse the same two options in `headers.js`.
- Note: `.bold()` uses weight `600`; use `.font_weight("700")` for a heavier one.

## More Information

- `src/evidential/_column.py` (`bold`, `italic`, `font_weight`, `font_style`),
  `src/evidential/configuration.py`, `frontend/src/cells.js`,
  `frontend/src/headers.js`.
- `frontend/test_table.js`, `tests/test_column_builder.py`,
  `notebooks/35_negatives.py`.
- Relates to [ADR-042](042-column-builder-and-settings.md).
