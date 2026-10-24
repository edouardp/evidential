"""DuckDB pivot helper.

:func:`pivot_table` aggregates the original records at every dimension/pivot
level, then projects those results into columns. It groups the resulting
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
from .marks import rebind_measure
from .table import EvidentialTable

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
) -> EvidentialTable:
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
    combos = [tuple(row.get(col) for col in pivot_cols) for row in combo_rows]

    select_parts: list[str] = list(dims)
    flags = [f"__g{index}" for index in range(len(dims))]
    select_parts.extend(flags)

    inner_measures = [f"{expression} AS {_quote(alias)}" for alias, expression in parsed_measures]
    weights = dict(weight_columns or {})
    inner_weights = {alias: f"__w_{index}" for index, (alias, _) in enumerate(parsed_measures) if alias in weights}
    inner_measures.extend(f"sum({weights[alias]}) AS {_quote(hidden)}" for alias, hidden in inner_weights.items())

    used_names = {name.casefold() for name in dims}

    def unique_name(preferred: str) -> str:
        name = preferred
        suffix = 2
        while name.casefold() in used_names:
            name = f"{preferred}__{suffix}"
            suffix += 1
        used_names.add(name.casefold())
        return name

    # Reserve total names first so a category named "Total" cannot take them.
    totals = (
        {alias: unique_name(f"{alias}__{total_label}") for alias, _ in parsed_measures} if show_total_column else {}
    )
    weight_aliases: dict[str, str] = {}

    def add_projection(name: str, alias: str, condition: str) -> None:
        # GROUPING SETS already computed exactly one result per output cell.
        # max only projects it; it never combines aggregate values.
        select_parts.append(f"max({_quote(alias)}) FILTER (WHERE {condition}) AS {_quote(name)}")
        if alias in inner_weights:
            hidden = unique_name(f"__w_{name}")
            select_parts.append(f"max({_quote(inner_weights[alias])}) FILTER (WHERE {condition}) AS {_quote(hidden)}")
            weight_aliases[name] = hidden

    # (column name, header group, headline measure alias)
    pivoted: list[tuple[str, str, str]] = []
    for alias, _ in parsed_measures:
        for combo in combos:
            condition = "__pivot_total = 0 AND " + " AND ".join(
                f"{column} IS NOT DISTINCT FROM {_sql_literal(value)}"
                for column, value in zip(pivot_cols, combo, strict=True)
            )
            label = _label(combo)
            name = unique_name(f"{alias}__{label}")
            add_projection(name, alias, condition)
            pivoted.append((name, label, alias))
        if show_total_column:
            name = totals[alias]
            add_projection(name, alias, "__pivot_total = 1")
            pivoted.append((name, total_label, alias))

    sets: list[str] = []
    levels = list(range(len(dims), 0, -1)) if subtotals else [len(dims)]
    if total:
        levels.append(0)
    for size in levels:
        sets.append("(" + ", ".join([*dims[:size], *pivot_cols]) + ")")
        if show_total_column:
            sets.append("(" + ", ".join(dims[:size]) + ")")

    group_cols = ", ".join([*dims, *pivot_cols])
    query = f"""
        WITH __inner AS (
            SELECT {group_cols}, {", ".join(inner_measures)},
                   {", ".join(f"grouping({dim}) AS {flag}" for dim, flag in zip(dims, flags, strict=True))},
                   grouping({pivot_cols[0]}) AS __pivot_total
            FROM (
                {sql}
            ) AS __base
            GROUP BY GROUPING SETS ({", ".join(sets)})
        )
        SELECT {", ".join(select_parts)}
        FROM __inner
        GROUP BY {", ".join([*dims, *flags])}
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
        specs = aggregations
        if isinstance(aggregations, Mapping):
            specs = {
                name: aggregations.get(name, aggregations[alias]) if alias in aggregations else aggregations[name]
                for name, _, alias in pivoted
                if name in aggregations or alias in aggregations
            }
        ordered = apply_aggregations(
            ordered,
            specs,
            [name for name, _, _ in pivoted],
            weight_aliases or None,
        )
    for row in ordered:
        for hidden in weight_aliases.values():
            row.pop(hidden, None)

    # ---- columns -----------------------------------------------------------
    columns: list[dict[str, Any]] = []
    for dim in dims:
        overrides = dict((dimension_config or {}).get(dim, {}))
        overrides.pop("name", None)  # a col.* builder carries its name; the key is the name
        overrides.setdefault("type", "string")
        overrides.setdefault("align", "left")
        columns.append(make_column(dim, **overrides))

    def make_measure_column(name: str, group: str, alias: str) -> dict[str, Any]:
        overrides = dict((measure_config or {}).get(alias, {}))
        overrides.pop("name", None)
        overrides.setdefault("type", "number")
        overrides.setdefault("align", "right")
        overrides.setdefault("column_group", group)
        return make_column(name, **rebind_measure(overrides, alias, name))

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
    return EvidentialTable(rows=ordered, columns=columns, **table_options)
