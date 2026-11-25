"""Client-side hierarchical grouping of in-memory rows.

Evidence's legacy ``groupBy`` groups a flat table by a column and shows
section/accordion groups with subtotals. :func:`grouped_records` does that in
Python for data already loaded in the notebook.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from .aggregations import resolve_aggregation
from .data import infer_columns, jsonify, make_column, normalize_data
from .table import EvidentialTable

__all__ = ["grouped_records"]


_SEP = "\x1f"


def _key(path: Sequence[Any]) -> str:
    return _SEP.join(json.dumps(jsonify(value), default=str) for value in path)


def _decorate_grouped_rows(
    rows: Sequence[Mapping[str, Any]],
    dims: Sequence[str],
    *,
    subtotals: bool = True,
    subtotal_position: str = "bottom",
    total_position: str = "bottom",
    total_label: str = "Total",
    combined: bool = False,
) -> list[dict[str, Any]]:
    """Turn grouped detail and summary records into render-ready rows.

    Rows must contain ``__g{index}`` columns indicating which dimensions are present. Returns
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
            if combined:
                # The section label and its summary share one row.
                row["__combined"] = True
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


def _sort_key(values: Sequence[Any]) -> tuple[str, ...]:
    return tuple("" if value is None else str(value) for value in values)


def grouped_records(
    data: Any = None,
    *,
    rows: Sequence[Mapping[str, Any]] | None = None,
    group_by: str | Sequence[str],
    measures: Sequence[str] | None = None,
    aggregations: Any = "sum",
    subtotals: bool = True,
    total: bool = True,
    subtotal_position: str = "bottom",
    total_position: str = "bottom",
    total_label: str = "Total",
    combined: bool = False,
    dimension_config: Mapping[str, Mapping[str, Any]] | None = None,
    measure_config: Mapping[str, Mapping[str, Any]] | None = None,
    **table_options: Any,
) -> EvidentialTable:
    """Group flat rows client-side and return an :class:`EvidentialTable`.

    ``group_by`` is one or more dimension columns; ``measures`` defaults to the
    numeric columns not used as dimensions. Each subtotal/total is computed from
    the group's detail values using ``aggregations`` (a built-in name, a
    callable, or a mapping from measure to either).
    """
    if rows is not None:
        raw_rows = [dict(row) for row in rows]
        normalized = [jsonify(row) for row in raw_rows]
        maybe_columns: list[dict[str, Any]] | None = infer_columns(None, raw_rows)
    else:
        normalized, maybe_columns = normalize_data(data)

    dims = [group_by] if isinstance(group_by, str) else list(group_by)
    if not dims:
        raise ValueError("grouped_records requires at least one group_by column")

    if maybe_columns is None:
        maybe_columns = infer_columns(None, normalized)
    by_name = {column["name"]: column for column in maybe_columns}

    if measures is None:
        measures = [
            column["name"] for column in maybe_columns if column["type"] == "number" and column["name"] not in dims
        ]
    measures = list(measures)
    if not measures:
        raise ValueError("grouped_records found no numeric measures; pass measures=[...]")

    def aggregate_for(measure: str):
        spec = aggregations.get(measure, "sum") if isinstance(aggregations, Mapping) else aggregations
        return resolve_aggregation(spec)

    detail = sorted(normalized, key=lambda row: _sort_key([row.get(dim) for dim in dims]))

    annotated: list[dict[str, Any]] = []

    def g_flags(level: int) -> dict[str, int]:
        return {f"__g{index}": 0 if index < level else 1 for index in range(len(dims))}

    for row in detail:
        entry = dict(row)
        entry.update(g_flags(len(dims)))
        annotated.append(entry)

    if subtotals:
        for level in range(1, len(dims)):
            groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
            for row in detail:
                key = tuple(row.get(dim) for dim in dims[:level])
                groups.setdefault(key, []).append(row)
            for key, members in groups.items():
                entry: dict[str, Any] = {dim: key[index] for index, dim in enumerate(dims[:level])}
                for measure in measures:
                    values = [m.get(measure) for m in members if m.get(measure) is not None]
                    entry[measure] = aggregate_for(measure)(values, None) if values else None
                entry.update(g_flags(level))
                annotated.append(entry)

    if total:
        entry = {}
        for measure in measures:
            values = [row.get(measure) for row in detail if row.get(measure) is not None]
            entry[measure] = aggregate_for(measure)(values, None) if values else None
        entry.update(g_flags(0))
        annotated.append(entry)

    ordered = _decorate_grouped_rows(
        annotated,
        dims,
        subtotals=subtotals,
        subtotal_position=subtotal_position,
        total_position=total_position,
        total_label=total_label,
        combined=combined,
    )

    def build_column(name: str, default_type: str, default_align: str, overrides: Mapping[str, Any]) -> dict[str, Any]:
        source = dict(by_name.get(name, {}))
        source.update(overrides)
        source.pop("name", None)
        source.setdefault("type", default_type)
        source.setdefault("align", default_align)
        return make_column(name, **source)

    columns: list[dict[str, Any]] = []
    for dim in dims:
        columns.append(build_column(dim, "string", "left", (dimension_config or {}).get(dim, {})))
    for measure in measures:
        columns.append(build_column(measure, "number", "right", (measure_config or {}).get(measure, {})))

    table_options.setdefault("show_total_row", total)
    table_options.setdefault("collapsible", subtotals)
    if table_options.get("group_type") == "section":
        table_options["collapsible"] = False
    table_options.setdefault("subtotal_position", subtotal_position)
    return EvidentialTable(rows=ordered, columns=columns, **table_options)
