---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-046: Temporal Kinds and Relative Time

## Context and Problem Statement

Dates, times and datetimes share one wire type (`"date"`): the frontend keys
off `/date|time/i` on the type name and the format code does the rest. Only
`col.date` existed, and there was no date-and-time format preset, so a
timestamp could not be shown with its time. Separately, "when did this happen"
reads best relative to now ("3 days ago"), which the formatter did not support.

## Decision Drivers

- Name the column's kind once (ADR-043); the type is shared, the presentation
  is the decision.
- Cover the common temporal kinds with no configuration.
- Relative time should be locale-aware and need no dependency.
- Keep one way to say each thing.

## Considered Options

1. One `col.date(name, fmt=...)` and raw format codes only.
2. Three kinds — `col.date`, `col.time`, `col.datetime` — each with a
   `relative=` parameter.
3. A `relative` visualisation instead of a format option.

## Decision Outcome

Chosen option: "three temporal kinds, with `relative=`".

- `col.date(name, *, fmt=None, relative=None, ...)` — date only (default
  `yyyy-mm-dd`).
- `col.time(name, *, fmt=None, relative=None, ...)` — time of day (default
  `hms`).
- `col.datetime(name, *, fmt=None, relative=None, ...)` — date and time
  (default the new `datetime` preset, `yyyy-mm-dd HH:MM:SS`).

All three set the wire type `"date"`. `relative` is `True` (an automatic unit)
or one of `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`,
`"year"`; there is also a `.relative(value=True)` chain method, and the option
is validated like every other. When set it wins over `fmt`.

The frontend formats with `Intl.RelativeTimeFormat` (`numeric: "auto"`), so
"yesterday"/"in 2 hours" are localised and pluralised for free. Values are
resolved to an instant by `Date.parse` first, so an ISO string with an offset
(`…Z`, `…+00:00`) stays absolute, and only then by the date-only normalization
the absolute formatters use.

Option 1 was rejected: it cannot express a timestamp, and it puts the
relative-vs-absolute decision in a raw code. Option 3 was rejected: relative
time is a rendering of a date, not a separate visualisation.

### Consequences

- Good, because the three common temporal kinds need no configuration, and the
  shared wire type keeps sorting/exports unchanged.
- Good, because relative time is locale-aware and dependency-free.
- Good, because `relative` distinguishes "a proportion"-style ambiguity the way
  `percent(whole=)` and `currency(code=)` do: the unit is explicit.
- Bad, because a `relative` column ignores `fmt` (relative text is the point).
- Note: the automatic unit converts month/year at ~30.44/365.25 days, which is
  accurate enough for "3 months ago" but not a calendar calculation.

## More Information

- `src/evidential/_column.py`, `src/evidential/configuration.py`,
  `frontend/src/format.js` (`formatRelative`), `frontend/src/cells.js`.
- `tests/test_column_builder.py`, `frontend/test_format.js`,
  `notebooks/32_column_builder.py`.
- Extends [ADR-043](043-column-kinds.md).
