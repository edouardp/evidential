"""Query-decorating helpers.

Evidence's ``where`` / ``having`` / ``order`` / ``limit`` / ``qualify`` /
``date_range`` props are applied when building SQL. :func:`query_table` wraps a
base relation with those clauses, and :func:`date_range_sql` renders Evidence's
date-range presets to a DuckDB boolean expression.
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Mapping
from typing import Any

from .table import EvidentialTable

__all__ = ["query_table", "date_range_sql"]


def _quoted(column: str) -> str:
    if re.fullmatch(r"[A-Za-z_][\w.]*", column):
        return column
    return '"' + column.replace('"', '""') + '"'


def _date_literal(text: str, *, end: bool = False) -> tuple[str, str]:
    """Validate an ISO date/time; date-only ends include that whole day."""
    try:
        value = (
            dt.date.fromisoformat(text) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else dt.datetime.fromisoformat(text)
        )
    except ValueError as error:
        raise ValueError(f"Invalid date in date_range: {text!r}") from error
    operator = "<="
    if end and not isinstance(value, dt.datetime):
        value += dt.timedelta(days=1)
        operator = "<"
    return f"TIMESTAMP '{value.isoformat()}'", operator


def date_range_sql(spec: str, column: str) -> str | None:
    """Return a SQL condition for an Evidence date-range ``spec`` (or ``None``).

    Accepts presets (``last 7 days``, ``month to date``, ``previous year``),
    dynamic windows (``Last 90 days``), custom ranges (``2020-01-01 to
    2023-03-01``) and partial ranges (``from 2020-01-01``, ``until 2023-03-01``).
    """
    text = str(spec).strip()
    lower = text.lower()
    col = _quoted(column)
    if lower in ("", "all time"):
        return None

    unit_by_prefix = {
        "week": "week",
        "month": "month",
        "quarter": "quarter",
        "year": "year",
    }

    # `<unit> to date` must be checked before the generic `X to Y` range.
    match = re.fullmatch(r"(week|month|quarter|year)\s+to\s+date", lower)
    if match:
        unit = unit_by_prefix[match.group(1)]
        return f"{col} >= date_trunc('{unit}', CURRENT_DATE) AND {col} < CURRENT_DATE + INTERVAL '1 day'"

    # Custom explicit dates.
    match = re.fullmatch(r"from\s+(\S+)", lower)
    if match:
        literal, _ = _date_literal(text[match.start(1) : match.end(1)])
        return f"{col} >= {literal}"
    match = re.fullmatch(r"until\s+(\S+)", lower)
    if match:
        literal, operator = _date_literal(text[match.start(1) : match.end(1)], end=True)
        return f"{col} {operator} {literal}"
    match = re.fullmatch(r"(\S+)\s+to\s+(\S+)", lower)
    if match:
        start, _ = _date_literal(text[match.start(1) : match.end(1)])
        end, operator = _date_literal(text[match.start(2) : match.end(2)], end=True)
        return f"{col} >= {start} AND {col} {operator} {end}"

    # Dynamic "last N <unit>".
    match = re.fullmatch(r"last\s+(\d+)\s+(day|week|month|quarter|year)s?", lower)
    if match:
        return f"{col} >= now() - INTERVAL '{match.group(1)} {match.group(2)}'"

    match = re.fullmatch(r"previous\s+(week|month|quarter|year)", lower)
    if match:
        unit = unit_by_prefix[match.group(1)]
        return f"date_trunc('{unit}', {col}) = date_trunc('{unit}', CURRENT_DATE) - INTERVAL '1 {unit}'"

    match = re.fullmatch(r"next\s+(week|month|quarter|year)", lower)
    if match:
        unit = unit_by_prefix[match.group(1)]
        return f"date_trunc('{unit}', {col}) = date_trunc('{unit}', CURRENT_DATE) + INTERVAL '1 {unit}'"

    match = re.fullmatch(r"this\s+(week|month|quarter|year)", lower)
    if match:
        unit = unit_by_prefix[match.group(1)]
        return f"date_trunc('{unit}', {col}) = date_trunc('{unit}', CURRENT_DATE)"

    fixed = {
        "today": f"{col} >= CURRENT_DATE AND {col} < CURRENT_DATE + INTERVAL '1 day'",
        "yesterday": (f"{col} >= CURRENT_DATE - INTERVAL '1 day' AND {col} < CURRENT_DATE"),
        "last 7 days": f"{col} >= now() - INTERVAL '7 days'",
        "last 30 days": f"{col} >= now() - INTERVAL '30 days'",
        "last 3 months": f"{col} >= now() - INTERVAL '3 months'",
        "last 6 months": f"{col} >= now() - INTERVAL '6 months'",
        "last 12 months": f"{col} >= now() - INTERVAL '12 months'",
    }
    if lower in fixed:
        return fixed[lower]

    raise ValueError(f"Unrecognised date_range: {spec!r}")


def query_table(
    connection: Any,
    sql: str,
    *,
    where: str | None = None,
    qualify: str | None = None,
    order: str | None = None,
    limit: int | None = None,
    date_range: str | Mapping[str, Any] | None = None,
    date_column: str | None = None,
    **table_options: Any,
) -> EvidentialTable:
    """Wrap ``sql`` with optional ``WHERE`` / ``QUALIFY`` / ``ORDER`` / ``LIMIT``.

    ``date_range`` (a preset string, or ``{"range": ..., "date": ...}``) adds a
    date filter; the column comes from ``date_column`` or the mapping's ``date``.
    """
    conditions: list[str] = []

    if date_range is not None:
        spec = date_range
        column = date_column
        if isinstance(date_range, Mapping):
            spec = date_range.get("range", "")
            column = column or date_range.get("date")
        if not column:
            raise ValueError("date_range requires a date column (date_column= or date_range['date'])")
        condition = date_range_sql(str(spec), str(column))
        if condition:
            conditions.append(condition)

    if where:
        conditions.append(f"({where})")

    clauses: list[str] = []
    if conditions:
        clauses.append("WHERE " + " AND ".join(conditions))
    if qualify:
        clauses.append("QUALIFY " + qualify)
    if order:
        clauses.append("ORDER BY " + order)
    if limit is not None:
        clauses.append(f"LIMIT {int(limit)}")

    query = "SELECT * FROM (\n" + sql + "\n) AS __base"
    if clauses:
        query += "\n" + "\n".join(clauses)
    return EvidentialTable(connection.sql(query), **table_options)
