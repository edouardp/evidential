---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-022: Derive Default Column Format and Alignment from the Data Type

## Context and Problem Statement

A table should look sensible with no configuration. DuckDB result relations
carry exact types (`relation.types`, and an Arrow schema with `INTEGER`,
`DECIMAL(p, s)`, `DATE`, `LIST`, `STRUCT`, …), but inference only produced a
coarse display type (`number`/`string`/`date`), leaving `fmt` and `align` unset.
The auto `num` format then chose decimals from the column's *magnitude*, so an
integer count such as `12` rendered as `12.0`. A list or struct column was also
mis-typed as `number`, because matching the substring `int` found the element
type inside `list<item: int32>`.

## Decision Drivers

- Sensible defaults with no `column_config`.
- Use the exact type the database already returns.
- Keep it overridable per column.

## Considered Options

1. Derive `type`, `fmt` and `align` from the source data type.
2. Keep the coarse type and leave formatting entirely to the auto-scaling
   format.
3. Require every column to be configured explicitly.

## Decision Outcome

Chosen option: "Derive from the data type". `data.py` maps the **outer** Arrow
type to a display type and a default presentation:

| Data type | `type` | default `fmt` | `align` |
| --- | --- | --- | --- |
| `INTEGER`/`BIGINT` | `number` | `num0` | right |
| `DECIMAL(p, s)` | `number` | `num{s}` | right |
| `DOUBLE`/`FLOAT` | `number` | auto | right |
| `DATE`/`TIMESTAMP` | `date` | — | left |
| `VARCHAR` | `string` | — | left |
| `BOOLEAN` | `boolean` | — | left |
| `LIST` | `array` | — | left |
| `STRUCT`/`MAP` | `object` | — | left |

Non-Arrow sources (lists of dicts, pandas after conversion) use the same rules
from the first values, including whether a numeric column is wholly integral.

### Consequences

- Good, because DuckDB/Arrow results render well by default (`count(*)` →
  `25,670`, not `12.0`).
- Good, because nested types are no longer misclassified as `number`.
- Good, because `column_config` still overrides every default.
- Bad, because integer columns no longer auto-scale units (`25,670`, not
  `26k`); set `fmt="num"` to restore auto-scaling.
- Bad, because the mapping must list Arrow type families as Arrow evolves.

## More Information

- [Technical architecture §4.2](../technical-architecture.md)
- `src/evidence_tables/data.py` (`_arrow_column_spec`, `_python_column_spec`)
- Related: [ADR-007](007-ssf-format-codes.md)
