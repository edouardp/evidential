---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-024: Read Arrow Field Metadata as Column Descriptions

## Context and Problem Statement

Parquet has file-level key/value metadata but **no standard per-column comment
field**. Column descriptions do travel, however, inside the Arrow schema:
PyArrow writes the whole schema — including per-field metadata — into the file's
`ARROW:schema` key/value entry, and reads it back. The same mechanism applies to
Feather/IPC and in-memory Arrow tables. Should those field descriptions become
the table's header descriptions, as DuckDB comments do
([ADR-023](023-duckdb-column-comments.md))?

## Decision Drivers

- Let one source (the Arrow schema) carry column documentation for file-based
  data.
- Reuse the existing `info` rendering (the ⓘ tooltip).
- Never surface metadata the reader cannot actually see.

## Considered Options

1. Map recognised Arrow field-metadata keys to `info`.
2. Read Parquet `ARROW:schema` bytes ourselves and decode them.
3. Do nothing; require explicit `column_config`.

## Decision Outcome

Chosen option: "Map recognised field-metadata keys". `_arrow_field_info` reads a
field's metadata (bytes or str keys, case-insensitive) and uses the first of
`comment`, `description`, `info`, which becomes the column's `info`. This is how
`EvidentialTable(pq.read_table("orders.parquet"))` shows documented columns.

Option 2 was rejected: decoding the `ARROW:schema` flatbuffer needs PyArrow
anyway, and DuckDB's `read_parquet` result does not carry the metadata, so there
is nothing to decode from the relation we are handed.

### Consequences

- Good, because a Parquet/Feather dataset documented with Arrow field metadata
  renders with descriptions in the header.
- Good, because it is the same `info` path as DuckDB comments and is overridden
  by `column_config`.
- Bad, because the metadata only reaches us when the file is read through
  Arrow (PyArrow); a DuckDB `read_parquet` result loses it.
- Bad, because key names are a convention (`comment`/`description`/`info`)
  rather than a Parquet standard.

## More Information

- [Technical architecture §4.2](../technical-architecture.md)
- `src/evidential/data.py` (`_arrow_field_info`)
- Related: [ADR-023](023-duckdb-column-comments.md)
