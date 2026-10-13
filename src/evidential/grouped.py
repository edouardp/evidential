"""DuckDB helpers that produce Evidence-style total/subtotal tables.

The headline helper, :func:`grouped_table`, runs one ``GROUPING SETS`` query
over a base query and post-processes the result into the row metadata the
browser needs to render collapsible groups, subtotals and a grand total.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .aggregations import apply_aggregations
from .data import jsonify
from .table import EvidentialTable

__all__ = ["grouped_table", "simple_table", "decorate_grouped_rows"]

_ALIAS_RE = re.compile(r"\s+as\s+([A-Za-z_][\w]*)\s*$", re.IGNORECASE)
_SEP = "\x1f"


def _parse_measure(measure: Any) -> tuple[str, str]:
    """Return ``(alias, expression)`` for a measure specification."""
    if isinstance(measure, tuple) and len(measure) == 2:
        return str(measure[0]), str(measure[1])
    if isinstance(measure, Mapping):
        if len(measure) != 1:
            raise ValueError("mapping measures must contain exactly one alias/expression")
        alias, expression = next(iter(measure.items()))
        return str(alias), str(expression)
    text = str(measure).strip()
    match = _ALIAS_RE.search(text)
    if match:
        return match.group(1), text[: match.start()].strip()
    alias = re.sub(r"[^\w]+", "_", text).strip("_") or "measure"
    return alias, text


def _key(path: Sequence[Any]) -> str:
    return _SEP.join(json.dumps(jsonify(value), default=str) for value in path)


def decorate_grouped_rows(
    rows: Sequence[Mapping[str, Any]],
    dims: Sequence[str],
    *,
    subtotals: bool = True,
    total: bool = True,
    subtotal_position: str = "bottom",
    total_position: str = "bottom",
    total_label: str = "Total",
) -> list[dict[str, Any]]:
    """Turn DuckDB ``grouping()`` output into render-ready grouped rows.

    Rows must contain ``__g{index}`` columns (from ``grouping(dim)``). Returns
    rows annotated with ``render_type`` (``cell_data``/``row_subtotal``/
    ``row_total``), ``__level``, ``__group_key``, ``__ancestors`` and
    ``__parent_key``, ordered so subtotals sit above or below their group.
    """
    decorated = [dict(row) for row in rows]
    n = len(dims)
    for row in decorated:
        present = [row.pop(f"__g{index}", 1) == 0 for index in range(n)]
        row["__present"] = present
        row["__level"] = sum(present)
        for index in range(n):
            if not present[index]:
                row[dims[index]] = ""

    total_rows = [row for row in decorated if row["__level"] == 0]
    other_rows = [row for row in decorated if row["__level"] != 0]
    top = subtotal_position != "bottom"

    def sort_key(row: Mapping[str, Any]) -> list[tuple[int, str]]:
        key: list[tuple[int, str]] = []
        for index in range(n):
            if row["__present"][index]:
                key.append((1, json.dumps(jsonify(row[dims[index]]), default=str)))
            else:
                key.append((0, "") if top else (2, ""))
        return key

    other_rows.sort(key=sort_key)

    def finalize(row: dict[str, Any]) -> dict[str, Any]:
        present = row["__present"]
        path = [row[dims[index]] for index in range(n) if present[index]]
        level = row["__level"]
        if level == n:
            row["render_type"] = "cell_data"
        elif subtotals:
            row["render_type"] = "row_subtotal"
            row["__group_key"] = _key(path)
        row["__ancestors"] = [_key(path[:size]) for size in range(1, level)]
        row["__parent_key"] = _key(path[: level - 1]) if level > 1 else None
        row.pop("__present", None)
        return row

    for row in other_rows:
        finalize(row)
    for row in total_rows:
        row["render_type"] = "row_total"
        row["__level"] = 0
        row["__group_key"] = "__total__"
        row["__ancestors"] = []
        row["__parent_key"] = None
        row[dims[0]] = total_label
        row.pop("__present", None)

    ordered = list(other_rows)
    if total_rows:
        ordered = (total_rows + ordered) if total_position == "top" else (ordered + total_rows)
    return ordered


def grouped_table(
    connection: Any,
    sql: str,
    dimensions: Sequence[str],
    measures: Sequence[Any],
    *,
    subtotals: bool = True,
    total: bool = True,
    subtotal_position: str = "bottom",
    total_position: str = "bottom",
    total_label: str = "Total",
    total_measures: Mapping[str, str] | None = None,
    aggregations: Any = None,
    weight_columns: Mapping[str, str] | None = None,
    dimension_config: Mapping[str, Mapping[str, Any]] | None = None,
    measure_config: Mapping[str, Mapping[str, Any]] | None = None,
    **table_options: Any,
) -> EvidentialTable:
    """Run a grouped query and return an :class:`EvidentialTable`.

    ``sql`` is the base relation (any ``SELECT``), ``dimensions`` are grouping
    columns, and ``measures`` are aggregate expressions such as
    ``"sum(total_amount) as revenue"``. Subtotals for every prefix of
    ``dimensions`` and (optionally) a grand total are generated with a single
    ``GROUPING SETS`` query.
    """
    if not dimensions:
        raise ValueError("grouped_table requires at least one dimension")
    if not measures:
        raise ValueError("grouped_table requires at least one measure")

    dims = list(dimensions)
    parsed_measures = [_parse_measure(measure) for measure in measures]

    grouping_cols = ", ".join(f"grouping({dim}) AS __g{index}" for index, dim in enumerate(dims))
    measure_columns: list[str] = []
    for alias, expression in parsed_measures:
        total_expression = (total_measures or {}).get(alias)
        if total_expression:
            # Use a different aggregation for the grand total row.
            measure_columns.append(
                f"CASE WHEN grouping({dims[0]}) = 1 THEN ({total_expression}) ELSE ({expression}) END AS {alias}"
            )
        else:
            measure_columns.append(f"{expression} AS {alias}")

    # Weighted aggregations need each measure's weights summed per detail group.
    weight_aliases: dict[str, str] = {}
    for alias, weight_column in (weight_columns or {}).items():
        hidden = f"__w_{alias}"
        measure_columns.append(f"sum({weight_column}) AS {hidden}")
        weight_aliases[alias] = hidden

    measure_cols = ", ".join(measure_columns)

    sets: list[str] = []
    if subtotals:
        sets.extend("(" + ", ".join(dims[:size]) + ")" for size in range(len(dims), 0, -1))
    else:
        sets.append("(" + ", ".join(dims) + ")")
    if total:
        sets.append("()")

    query = f"""
        WITH __base AS (
            {sql}
        )
        SELECT {", ".join(dims)}, {measure_cols}, {grouping_cols}
        FROM __base
        GROUP BY GROUPING SETS ({", ".join(sets)})
    """
    rows = [jsonify(row) for row in connection.sql(query).to_arrow_table().to_pylist()]
    ordered = decorate_grouped_rows(
        rows,
        dims,
        subtotals=subtotals,
        total=total,
        subtotal_position=subtotal_position,
        total_position=total_position,
        total_label=total_label,
    )
    if aggregations is not None:
        ordered = apply_aggregations(
            ordered,
            aggregations,
            [alias for alias, _ in parsed_measures],
            weight_aliases or None,
        )
    for row in ordered:
        for hidden in weight_aliases.values():
            row.pop(hidden, None)

    measure_aliases = [alias for alias, _ in parsed_measures]

    from .data import make_column

    columns: list[dict[str, Any]] = []

    for dim in dims:
        overrides = dict((dimension_config or {}).get(dim, {}))
        overrides.pop("name", None)  # a col.* builder carries its name; the key is the name
        overrides.setdefault("type", "string")
        overrides.setdefault("align", "left")
        columns.append(make_column(dim, **overrides))
    for alias in measure_aliases:
        overrides = dict((measure_config or {}).get(alias, {}))
        overrides.pop("name", None)
        overrides.setdefault("type", "number")
        overrides.setdefault("align", "right")
        columns.append(make_column(alias, **overrides))

    table_options.setdefault("show_total_row", total)
    table_options.setdefault("collapsible", subtotals)
    if table_options.get("group_type") == "section":
        table_options["collapsible"] = False
    if table_options.get("subtotal_position") is None:
        table_options["subtotal_position"] = subtotal_position
    return EvidentialTable(rows=ordered, columns=columns, **table_options)


def simple_table(connection: Any, sql: str, **table_options: Any) -> EvidentialTable:
    """Run ``sql`` on a DuckDB connection and wrap the arrow result."""
    return EvidentialTable(connection.sql(sql), **table_options)
