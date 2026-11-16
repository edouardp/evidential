---
status: accepted
date: 2026-11-16
deciders: edouard
---

# ADR-102: DuckDB 2 Relation Results

## Context and Problem Statement

The dependency refresh selects DuckDB 2.0. Relations no longer have cursor-like
`fetchone()` or `fetchmany()` methods. DB-API connections still support these
methods, but a partially consumed result prevents other work on that connection.
Our OECD inventory read one aggregate row without exhausting its cursor, then
tried to create another view. Other demos called the removed relation method.
Parameterized live tables used DB-API results, whose Arrow conversion now copies
rows and emits a warning.

## Decision Drivers

- Support the updated dependency environment and existing DuckDB 1 installations.
- Preserve SQL parameter binding, query results, missing values and empty results.
- Use relations for table/Arrow output without a DB-API intermediate copy.
- Avoid a compatibility layer that restores removed methods or patches DuckDB.

## Considered Options

1. Pin the development lockfile to DuckDB 1 and defer compatibility.
2. Reintroduce cursor-like relation methods through a local adapter.
3. Use the supported relation and fully consumed result APIs directly.

## Decision Outcome

Chosen option: **3**. Parameterized live table queries use
`con.sql(statement, params=values)` and retain the same bound values. Notebook
query helpers that return tables use relations and `to_arrow_table()`; helpers
building records read `relation.columns` and `fetchall()`.

Queries known to return a single aggregate or unique row read
`fetchall()[0]`. The OECD duplicate check already has `LIMIT 1` and uses the
returned list directly so an empty result remains valid. DB-API aggregate reads
also consume their complete result before the connection is reused. Schema and
mutation commands continue using `execute()`, as do deliberate DB-API examples
that fully consume their result. No arbitrary large query is fetched solely to
obtain its first row.

The existing `duckdb>=1.3` package constraint is retained: these relation APIs
are supported by DuckDB 1 as well as 2. The development lockfile moves to 2.0.
Compatibility is checked on 2.0 and the previous locked 1.5.6 version rather
than branching behavior based on version numbers.

### Consequences

Parameter binding and the public Evidential API remain unchanged. Notebook
aggregates and empty-result checks use explicit result semantics; reusing the
OECD connection no longer encounters an unfinished cursor. Parameterized live
table refreshes avoid DuckDB 2's DB-API-to-Arrow copy. Existing query regression
tests exercise both empty and populated data, duplicate rejection, and repeated
queries. A live-table test treats the copy warning as an error and covers
parameter updates through an empty result while retaining the schema.

## More Information

- [Executing SQL in Python](https://duckdb.org/docs/2.0/guides/python/execute_sql).
- [Relational API](https://duckdb.org/docs/2.0/clients/python/relational_api).
- [DB-API result ownership and Arrow output](https://duckdb.org/docs/clients/python/dbapi).
