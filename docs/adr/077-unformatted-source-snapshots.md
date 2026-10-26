---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-077: Unformatted Source Snapshots

## Context and Problem Statement

Analysts need to inspect table data in Marimo's ordinary grid without number
formatting, blank predicates, text transforms or visual encodings. The synced
`rows` may already contain transformed values and callable mark helper fields.
Live tables and SQL helpers should expose the same inspection API.

## Decision Drivers

- Return data independently of any display library or optional dataframe extra.
- Preserve hidden source fields and original detail order.
- Prevent snapshot edits from mutating table state, including nested arrays.
- Reuse the retained source snapshot and successful-update boundary.
- Avoid query execution or changes to the widget's state when reading data.

## Considered Options

1. Return synced `rows` directly.
2. Return a pandas or Arrow table, requiring a dataframe dependency.
3. Return a detached list of unformatted source records.

## Decision Outcome

Chosen option: **3**. `EvidentialTable.raw` deep-copies the retained normalized
source records before presentation preparation. Subclasses, including
`LiveEvidentialTable`, inherit the property. Constructors and SQL helpers that
return an `EvidentialTable` gain the same behavior without separate adapters.

The snapshot includes hidden source fields and excludes generated mark helpers
and synthetic display rows. Browser filters, sort and paging do not affect it.
It reflects the current successful Python data update; reading it never queries
the database. SQL helper results retain their existing aggregation/pivot shape.

Values retain existing JSON-boundary normalization, including ISO date/time
strings, decimal-to-float conversion and nulls for nonfinite numbers. The API
does not promise the original input container or its schema. Marimo accepts
the records directly through `mo.ui.table(table.raw, selection=None)`.

### Consequences

Raw-grid inspection works without pandas, Arrow or Marimo as runtime
dependencies. Reading `.raw` allocates a deep copy proportional to source data;
snapshots remain safe to edit and stable after later refreshes. Native dataframe
types and empty schemas are not retained by this record-based interface.

## More Information

- `src/evidential/table.py` retains source records and implements `.raw`.
- `tests/test_raw.py` covers input types, presentation isolation, live updates,
  helper results and Marimo grid construction.
- [Marimo table inputs](https://docs.marimo.io/api/inputs/table/).
