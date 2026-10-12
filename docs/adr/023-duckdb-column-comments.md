---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-023: Surface DuckDB Column Comments as Header Descriptions

## Context and Problem Statement

DuckDB supports `COMMENT ON TABLE` / `COMMENT ON COLUMN`, which is a natural
place to document a column. Can those comments become the table's header
description (the ⓘ tooltip) without the author repeating them in
`column_config`?

DuckDB exposes comments only through `duckdb_columns().comment`: they do **not**
travel with the query result or the Arrow schema the widget already consumes.
A relation built from a table or view keeps that name in `relation.alias`
(`limit`/`filter`/`project` preserve it); a raw `con.sql(...)` becomes an
unnamed query relation and loses it.

## Decision Drivers

- Let the database be the single place a column is documented.
- Never attach the wrong comment.
- Keep it overridable.

## Considered Options

1. Read comments from `duckdb_columns()` and apply them as `info` when the
   relation names its source.
2. Match result columns to catalog comments purely by column name.
3. Do nothing; require explicit `column_config`.

## Decision Outcome

Chosen option: "Read comments when the source is named". `normalize_data` reads
comments for a DuckDB relation whose `alias` is a real name (table/view
relations and their `limit`/`filter`/`select` derivatives) and sets the
column's `info`. For raw `con.sql(...)` results — where the source is unknown —
`duck.column_comments(connection, table)` returns the mapping for the caller to
merge into `column_config`.

Name-only matching (option 2) was rejected because a column name shared across
tables could attach an unrelated comment.

### Consequences

- Good, because `EvidenceTable(con.table("trips"))` shows documented columns
  with no configuration.
- Good, because `column_config` still wins, and ambiguity cannot mislabel a
  column.
- Bad, because `con.sql(...)` (the common `SELECT …`) does not get comments
  automatically; use `con.table(...)` or `duck.column_comments`.
- Bad, because it costs an extra `duckdb_columns()` query per relation.

## More Information

- [Technical architecture §4.2](../technical-architecture.md)
- `src/evidence_tables/data.py` (`_relation_column_comments`),
  `src/evidence_tables/duck.py` (`column_comments`)
- Related: [ADR-022](022-type-driven-column-defaults.md)
