"""DuckDB pivot helper.

:func:`pivot_table` builds a dimensions × pivot-values × measures table using a
two-stage aggregate (first per dims+pivots, then pivoted), groups the resulting
columns under shared headers, and reuses :func:`decorate_grouped_rows` for
subtotal/total rows.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Mapping, Sequence
from typing import Any

from .aggregations import apply_aggregations
from .data import jsonify, make_column
from .grouped import _parse_measure, decorate_grouped_rows
from .table import EvidenceTable

__all__ = ["pivot_table"]


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (dt.datetime, dt.date)):
        return f"TIMESTAMP '{value.isoformat()}'"
    return "'" + str(value).replace("'", "''") + "'"


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _label(combo: Sequence[Any]) -> str:
    return " · ".join("" if value is None else str(value) for value in combo)


def pivot_table(
    connection: Any,
    sql: str,
    dimensions: Sequence[str],
    pivots: Sequence[str],
    measures: Sequence[Any],
    *,
    subtotals: bool = True,
    total: bool = True,
    show_total_column: bool = True,
    measures_first: bool = False,
    subtotal_position: str = "bottom",
    total_position: str = "bottom",
    total_label: str = "Total",
    aggregations: Any = None,
    weight_columns: Mapping[str, str] | None = None,
    dimension_config: Mapping[str, Mapping[str, Any]] | None = None,
    measure_config: Mapping[str, Mapping[str, Any]] | None = None,
    **table_options: Any,
) -> EvidenceTable:
    """Pivot ``pivots`` into columns, aggregating each measure per pivot value.

    ``sql`` is the base relation, ``dimensions`` are the row dimensions, and
    ``measures`` are aggregate expressions (``"sum(sales) as sales"``). Each
    distinct pivot combination becomes its own column per measure, grouped under
    a header (the pivot value, or the measure when ``measures_first=True``).
    """
    if not pivots:
        raise ValueError("pivot_table requires at least one pivot column")
    if not measures:
        raise ValueError("pivot_table requires at least one measure")
    if not dimensions:
        raise ValueError("pivot_table requires at least one dimension")

    dims = list(dimensions)
    pivot_cols = list(pivots)
    parsed_measures = [_parse_measure(measure) for measure in measures]

    # Distinct pivot combinations become the pivoted columns.
    combo_query = (
        "WITH __base AS ( " + sql + " ) "
        "SELECT DISTINCT " + ", ".join(pivot_cols) + " FROM __base "
        "ORDER BY " + ", ".join(pivot_cols)
    )
    combo_rows = connection.sql(combo_query).to_arrow_table().to_pylist()
    combos = [tuple(jsonify(row.get(col)) for col in pivot_cols) for row in combo_rows]

    select_parts: list[str] = list(dims)
    select_parts.extend(f"grouping({dim}) AS __g{index}" for index, dim in enumerate(dims))

    inner_measures = ", ".join(
        f"{expression} AS {_quote(alias)}" for alias, expression in parsed_measures
    )

    # (column name, header group, headline measure alias)
    pivoted: list[tuple[str, str, str]] = []
    for alias, _ in parsed_measures:
        for combo in combos:
            condition = " AND ".join(
                f"{column} IS NOT DISTINCT FROM {_sql_literal(value)}"
                for column, value in zip(pivot_cols, combo, strict=False)
            )
            label = _label(combo)
            name = f"{alias}__{label}"
            # The inner stage already aggregated per (dims, pivots); re-aggregate
            # additively so subtotal rows sum across the pivot values.
            select_parts.append(
                f"sum({_quote(alias)}) FILTER (WHERE {condition}) AS {_quote(name)}"
            )
            pivoted.append((name, label, alias))
        if show_total_column:
            name = f"{alias}__{total_label}"
            select_parts.append(f"sum({_quote(alias)}) AS {_quote(name)}")
            pivoted.append((name, total_label, alias))

    sets: list[str] = []
    if subtotals:
        sets.extend("(" + ", ".join(dims[:size]) + ")" for size in range(len(dims), 0, -1))
    else:
        sets.append("(" + ", ".join(dims) + ")")
    if total:
        sets.append("()")

    group_cols = ", ".join([*dims, *pivot_cols])
    query = f"""
        WITH __inner AS (
            SELECT {group_cols}, {inner_measures}
            FROM (
                {sql}
            ) AS __base
            GROUP BY {group_cols}
        )
        SELECT {", ".join(select_parts)}
        FROM __inner
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
            None,
        )

    # ---- columns -----------------------------------------------------------
    columns: list[dict[str, Any]] = []
    for dim in dims:
        overrides = dict((dimension_config or {}).get(dim, {}))
        overrides.setdefault("type", "string")
        overrides.setdefault("align", "left")
        columns.append(make_column(dim, **overrides))

    def make_measure_column(name: str, group: str, alias: str) -> dict[str, Any]:
        overrides = dict((measure_config or {}).get(alias, {}))
        overrides.setdefault("type", "number")
        overrides.setdefault("align", "right")
        overrides.setdefault("column_group", group)
        return make_column(name, **overrides)

    if measures_first:
        # Group by measure: Sales > 2021 | 2022 | Total
        for alias, _ in parsed_measures:
            for name, _group, headline in pivoted:
                if headline == alias:
                    columns.append(make_measure_column(name, alias, alias))
    else:
        # Group by pivot value: 2021 > Sales | Orders, then Total > Sales | Orders
        groups: list[str] = []
        for _, group, _ in pivoted:
            if group not in groups:
                groups.append(group)
        for group in groups:
            for name, column_group, alias in pivoted:
                if column_group == group:
                    columns.append(make_measure_column(name, group, alias))

    table_options.setdefault("show_total_row", total)
    table_options.setdefault("collapsible", subtotals)
    table_options.setdefault("subtotal_position", subtotal_position)
    return EvidenceTable(rows=ordered, columns=columns, **table_options)
