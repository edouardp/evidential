---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-041: Adaptive Symbol Footnotes

## Context and Problem Statement

Footnote marks used an accent color and help cursor, making plain superscripts
look interactive. The default numeric scheme did not match the preferred
publication style. The existing symbol scheme repeated six single marks without
distinguishing later notes.

## Decision Drivers

- Render footnote marks as plain superscripts in the surrounding text color.
- Prefer distinct single symbols, add doubles beside singles only as needed.
- Keep cell and footer marks identical after deduplicating note text.
- Retain explicitly requested numeric and letter schemes.

## Considered Options

1. Continue numbering all notes by default.
2. Use a fixed sequence of singles followed by doubles.
3. Adapt an interleaved single/double sequence to the distinct note count.

## Decision Outcome

Chosen option: symbols are the default. The ordered list is `*`, `†`, `‡`, `§`,
`¶`, `#`, `+`, `◆`, `◇`, `△`. Up to ten distinct notes use only singles. With
more notes, the earliest symbols gain doubles immediately after their singles.
Eleven notes therefore use `*`, `**`, `†`, `‡`, `§`, `¶`, `#`, `+`, `◆`, `◇`, `△`.
Twenty notes use every single/double pair. Further notes use `1`, `2`, `3`, …

`footnotes.js` owns mark selection and final cell labeling. Cells first collect
note text and place empty superscript markers with note indexes. After all rows
are rendered, the distinct note count determines the sequence for both cells
and the footer. Duplicate notes keep a shared index. As before, notes are local
to the rendered rows; paging, filtering or collapsing can change the sequence.
Static source notes remain unmarked and do not consume symbol slots.

Marks inherit the surrounding color, have normal weight and a default cursor,
and retain their tooltip. They remain outside per-cell links. Explicit
`footnote_marks="numbers"` or `"letters"` keeps the existing scheme.

### Consequences

- Good, because repeated notes and their footer entries share one mark.
- Good, because additional notes never reuse a symbol already assigned.
- Good, because decorative marks no longer look like links.
- Bad, because adding notes beyond ten can change earlier marks.
- Bad, because numeric fallback starts at one after the symbol budget is spent.

## More Information

- Extends [ADR-010](010-gt-style-location-rules.md).
- [README footnotes](../../README.md#presentation-parts).
