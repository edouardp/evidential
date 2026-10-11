"""Data conversion helpers for :class:`evidence_tables.EvidenceTable`.

The widget exchanges plain JSON with the browser, so this module normalises the
common Python data containers (Arrow tables, pandas DataFrames, DuckDB
relations, lists of dicts) into ``(rows, columns)`` where every value is
JSON-serialisable.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from typing import Any

__all__ = [
    "make_column",
    "infer_columns",
    "normalize_data",
    "jsonify",
]


def jsonify(value: Any) -> Any:
    """Recursively convert a value into something JSON can serialise."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if value == value else None  # NaN -> None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, dt.timedelta):
        return value.total_seconds()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, Mapping):
        return {str(k): jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonify(v) for v in value]
    # numpy / pyarrow scalars expose `.item()` / `.as_py()`.
    for attr in ("as_py", "item"):
        method = getattr(value, attr, None)
        if callable(method):
            try:
                return jsonify(method())
            except Exception:  # pragma: no cover - defensive
                return str(value)
    return str(value)


def make_column(name: str, *, type: str = "string", **overrides: Any) -> dict[str, Any]:
    """Return a column definition in the widget's wire format."""
    column: dict[str, Any] = {
        "name": name,
        "title": None,
        "type": type,
        "fmt": None,
        "align": None,
        "wrap": None,
        "hide": False,
        "viz": None,
        "red_negatives": False,
        "html": False,
        "link": None,
        "link_label": None,
        "link_new_tab": False,
        "image": None,
        "column_group": None,
        "info": None,
        "repeat_values": None,
        "color_options": None,
        "bar_options": None,
        "delta_options": None,
        "sparkline_options": None,
        "viz_include_subtotals": None,
    }
    column.update(overrides)
    return {k: v for k, v in column.items() if v is not None or k in {"name", "type"}}


_ARROW_TYPE_MAP = (
    ("date", "date"),
    ("time", "date"),
    ("timestamp", "date"),
    ("bool", "boolean"),
    ("int", "number"),
    ("uint", "number"),
    ("float", "number"),
    ("double", "number"),
    ("decimal", "number"),
    ("list", "array"),
    ("large_list", "array"),
    ("struct", "object"),
    ("map", "object"),
)


def _arrow_type_name(field_type: Any) -> str:
    name = str(field_type).lower()
    for needle, mapped in _ARROW_TYPE_MAP:
        if needle in name:
            return mapped
    return "string"


def _infer_python_type(values: Iterable[Any]) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float, Decimal)):
            return "number"
        if isinstance(value, (dt.datetime, dt.date, dt.time)):
            return "date"
        if isinstance(value, (list, tuple)):
            return "array"
        if isinstance(value, Mapping):
            return "object"
        return "string"
    return "string"


def infer_columns(data: Any, rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Infer widget column definitions from a data object or sampled rows."""
    names: list[str]
    schema = getattr(data, "schema", None)
    if schema is not None and hasattr(schema, "names"):  # pyarrow-style schema
        names = list(schema.names)
        columns = []
        for field in schema:
            columns.append(make_column(field.name, type=_arrow_type_name(field.type)))
        return columns
    if hasattr(data, "columns") and not callable(data.columns):  # pandas
        names = [str(c) for c in data.columns]
    elif rows:
        names = list(rows[0].keys())
    else:
        return []
    columns = []
    for name in names:
        values = [row.get(name) for row in rows[:200]]
        columns.append(make_column(name, type=_infer_python_type(values)))
    return columns


def _merge_column_config(
    columns: list[dict[str, Any]], config: Mapping[str, Mapping[str, Any]] | None
) -> list[dict[str, Any]]:
    if not config:
        return columns
    for column in columns:
        overrides = config.get(column["name"])
        if overrides:
            column.update(overrides)
    return columns


def normalize_data(data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]] | None]:
    """Convert ``data`` into ``(rows, inferred_columns)``.

    ``data`` may be a list of mappings, an Arrow table, a pandas DataFrame, a
    DuckDB relation, or anything exposing ``to_pylist``/``to_dict``. Returns
    ``(rows, None)`` when the container has no schema information so the caller
    can fall back to explicit ``columns``.
    """
    from ._compat import arrow_table_to_rows, is_arrow_table, is_pandas_dataframe

    if data is None:
        return [], None
    if is_arrow_table(data):
        return arrow_table_to_rows(data), infer_columns(data, [])
    if is_pandas_dataframe(data):
        rows = [jsonify(record) for record in data.to_dict(orient="records")]
        columns = infer_columns(data, rows)
        return rows, columns
    # DuckDB relation / connection result.
    for method in ("to_arrow_table", "arrow", "fetch_arrow_table"):
        fn = getattr(data, method, None)
        if callable(fn):
            arrow = fn()
            read_all = getattr(arrow, "read_all", None)
            if callable(read_all):
                arrow = read_all()
            if is_arrow_table(arrow):
                return arrow_table_to_rows(arrow), infer_columns(arrow, [])
    if hasattr(data, "to_pylist"):
        raw_rows = [dict(row) for row in data.to_pylist()]
        return [jsonify(row) for row in raw_rows], infer_columns(data, raw_rows)
    raw_rows = [dict(row) for row in data]
    return [jsonify(row) for row in raw_rows], infer_columns(None, raw_rows)
