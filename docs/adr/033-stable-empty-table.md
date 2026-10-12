---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-033: A Stable Empty Table (Placeholder Rows and an Overlay)

## Context and Problem Statement

When a table has no rows the renderer replaced the whole table with a centred
"You have no data" block: no headers, no grid, a different height. For a
**drill-down** table (ADR-032) this is jarring — the second table appears,
vanishes, changes size and shifts the page every time the selection changes. We
want the empty table to hold its place.

## Decision Drivers

- The table's headers and height must not depend on whether there is data.
- The empty grid must still read as "a table with no rows", not as an error.
- The caller should control the message and (if they want) the row count.

## Considered Options

1. Keep the headers, render blank placeholder rows, and put a translucent
   message over the body only.
2. Keep the old whole-table message block.
3. Render nothing at all (let the caller hide/show the table).

## Decision Outcome

Chosen option: "Placeholder rows + body overlay". With columns configured, an
empty table renders its normal header and `N` blank rows (`empty_rows`, else the
effective `page_size`, else 10 — capped at 200). The message is a `tbody::after`
pseudo-element with `content: attr(data-empty-message)`, `position: absolute;
inset: 0` and a 30%‑alpha surface background, so it covers the rows **but not the
sticky header**. A row's first empty cell carries a non-breaking space so its
line height matches a data row. Only when a table has **no columns** (nothing to
head) does it fall back to the flat `.et-empty` block.

Option 2 was rejected: it is the problem. Option 3 was rejected: the caller would
have to build the empty shell themselves, and the page would still jump.

### Consequences

- Good, because the table's geometry is independent of its data.
- Good, because the headers (and their column configs) are always visible.
- Good, because the caller controls the message (`empty_message`) and the height
  (`empty_rows`).
- Note: the overlay is deliberately over the cells only; the header stays fully
  legible.
- Note: `page_size="all"` or `0` has no meaningful row count, so the default
  falls back to 10.

## More Information

- `frontend/src/table.js` (`_emptyRowCount`, `_renderTable`, `_renderPlaceholderRow`)
- `frontend/src/table.css` (`.et-empty-body`)
- `notebooks/29_row_selection.py`
