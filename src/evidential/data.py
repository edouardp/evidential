"""Data conversion helpers for :class:`evidential.EvidentialTable`.

The widget exchanges plain JSON with the browser, so this module normalises the
common Python data containers (Arrow tables, pandas DataFrames, DuckDB
relations, lists of dicts) into ``(rows, columns)`` where every value is
JSON-serialisable.
"""

from __future__ import annotations

import datetime as dt
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from typing import Any

from ._column_options import _normalize_column_options
from .configuration import ColumnOptions, validate_options

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
        return value if math.isfinite(value) else None
    if isinstance(value, Decimal):
        return jsonify(float(value))
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
        "relative": None,
        "align": None,
        "wrap": None,
        "hide": False,
        "viz": None,
        "red_negatives": False,
        "negative_color": None,
        "bracket_negatives": False,
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
        "chip_options": None,
        "boolean_options": None,
        "viz_include_subtotals": None,
        # Sort this column by another column's values (hidden ones included).
        "sort_by": None,
        # Background highlight for the whole column (header + cells).
        "highlight": None,
    }
    column.update(_normalize_column_options({"name": name, "type": type, **overrides}))
    validate_options(column, ColumnOptions, "column")
    return {k: v for k, v in column.items() if v is not None or k in {"name", "type"}}


# Match the *outer* Arrow type only: the string form of a nested type (e.g.
# ``list<item: int32>``) contains its element type, so a substring search would
# classify a list of ints as a number.
_ARROW_TYPE_MAP = (
    ("large_list", "array"),
    ("list", "array"),
    ("struct", "object"),
    ("map", "object"),
    ("date", "date"),
    ("time", "date"),
    ("bool", "boolean"),
    ("int", "number"),
    ("uint", "number"),
    ("float", "number"),
    ("double", "number"),
    ("decimal", "number"),
)


def _arrow_head(field_type: Any) -> str:
    """The outer Arrow type name, e.g. ``list`` for ``list<item: int32>``."""
    return re.split(r"[<\[(]", str(field_type).lower(), maxsplit=1)[0]


def _arrow_type_name(field_type: Any) -> str:
    head = _arrow_head(field_type)
    for prefix, mapped in _ARROW_TYPE_MAP:
        if head.startswith(prefix):
            return mapped
    return "string"


def _column_spec(type_name: str, *, integer: bool = False, scale: int | None = None) -> dict[str, Any]:
    """Infer a column's ``type``, ``fmt`` and ``align`` from its data type."""
    if type_name != "number":
        return {"type": type_name, "fmt": None, "align": "left"}
    if integer:
        # Counts and ids read better as whole numbers than the magnitude-based
        # auto format, which would render 12 as "12.0".
        fmt: str | None = "num0"
    elif scale is not None:
        fmt = f"num{min(max(scale, 0), 4)}"
    else:
        fmt = None  # leave it to the auto-scaling num/usd/... format
    return {"type": "number", "fmt": fmt, "align": "right"}


def _arrow_column_spec(field_type: Any) -> dict[str, Any]:
    type_name = _arrow_type_name(field_type)
    if type_name != "number":
        return _column_spec(type_name)
    head = _arrow_head(field_type)
    if head.startswith(("int", "uint")):
        return _column_spec("number", integer=True)
    if head.startswith("decimal"):
        scale = getattr(field_type, "scale", None)
        return _column_spec("number", scale=scale if isinstance(scale, int) else None)
    return _column_spec("number")


#: Arrow field metadata keys treated as a column description (case-insensitive).
_FIELD_INFO_KEYS = ("comment", "description", "info")


def _arrow_field_info(field: Any) -> str | None:
    """A column description from Arrow field metadata, if any.

    This is how a description survives Parquet and Feather: PyArrow writes the
    full Arrow schema (including field metadata) into the file's ``ARROW:schema``
    key-value entry, and reads it back. DuckDB does not surface it from
    ``read_parquet``. Recognised keys are ``comment``, ``description`` and
    ``info`` (case-insensitive).
    """
    metadata = getattr(field, "metadata", None)
    if not metadata:
        return None
    normalized: dict[str, Any] = {}
    for key, value in metadata.items():
        name = key.decode("utf-8", "replace") if isinstance(key, bytes) else str(key)
        normalized[name.lower()] = value
    for key in _FIELD_INFO_KEYS:
        value = normalized.get(key)
        if not value:
            continue
        text = value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)
        if text.strip():
            return text.strip()
    return None


def _python_column_spec(values: Iterable[Any]) -> dict[str, Any]:
    numeric = False
    integer = True
    for value in values:
        if value is None:
            continue
        if isinstance(value, bool):
            return _column_spec("boolean")
        if isinstance(value, int):
            numeric = True
            continue
        if isinstance(value, (float, Decimal)):
            numeric = True
            integer = False
            continue
        if isinstance(value, (dt.datetime, dt.date, dt.time)):
            return _column_spec("date")
        if isinstance(value, (list, tuple)):
            return _column_spec("array")
        if isinstance(value, Mapping):
            return _column_spec("object")
        return _column_spec("string")
    if numeric:
        return _column_spec("number", integer=integer)
    return _column_spec("string")


def infer_columns(data: Any, rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Infer widget column definitions from a data object or sampled rows.

    Arrow-backed sources (including DuckDB relations) use the result schema, so
    integer columns default to ``num0``, decimals keep their scale, and nested
    types are recognised; other sources are inferred from the first values.
    """
    schema = getattr(data, "schema", None)
    if schema is not None and hasattr(schema, "names"):  # pyarrow-style schema
        columns = []
        for field in schema:
            column = make_column(field.name, **_arrow_column_spec(field.type))
            info = _arrow_field_info(field)
            if info:
                column["info"] = info
            columns.append(column)
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
        columns.append(make_column(name, **_python_column_spec(values)))
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


def apply_blank_predicates(
    rows: Iterable[Mapping[str, Any]],
    column_config: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Replace values with ``None`` where a column's ``blank`` callable says so.

    Custom callables cannot be serialised to the browser, so they are applied to
    the rows here; the rendered result is a null (see the column's
    ``null_text``).
    """
    if not column_config:
        return [dict(row) for row in rows]
    predicates: dict[str, Any] = {}
    for name, config in column_config.items():
        if not isinstance(config, Mapping):
            continue
        predicate = config.get("blank") or config.get("blank_if")
        if callable(predicate):
            predicates[name] = predicate
    if not predicates:
        return [dict(row) for row in rows]
    result = []
    for row in rows:
        row = dict(row)
        for name, predicate in predicates.items():
            value = row.get(name)
            if value is not None and predicate(value):
                row[name] = None
        result.append(row)
    return result


def _relation_column_comments(relation: Any) -> dict[str, str]:
    """DuckDB column comments for a table/view relation, if it knows its name.

    DuckDB stores ``COMMENT ON COLUMN`` metadata but exposes it only through
    ``duckdb_columns()`` (it does not travel with the result or the Arrow
    schema). Relations built from a table or view — including ``.limit()``,
    ``.filter()`` and ``.select()`` — keep that name in ``alias``; raw
    ``con.sql(...)`` relations do not, and fall back to
    :func:`evidential.duck.column_comments`.
    """
    alias = getattr(relation, "alias", None)
    run_query = getattr(relation, "query", None)
    if not alias or str(alias).startswith("unnamed_relation") or not callable(run_query):
        return {}
    escaped = str(alias).replace("'", "''")
    try:
        rows = run_query(
            "__evidential_relation",
            f"SELECT column_name, comment FROM duckdb_columns() WHERE table_name = '{escaped}' AND comment IS NOT NULL",
        ).fetchall()
    except Exception:  # pragma: no cover - depends on the DuckDB build
        return {}
    return {str(name): str(comment) for name, comment in rows if comment}


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
                columns = infer_columns(arrow, [])
                # Surface DuckDB column comments as header descriptions.
                comments = _relation_column_comments(data)
                for column in columns:
                    comment = comments.get(column["name"])
                    if comment:
                        column["info"] = comment
                return arrow_table_to_rows(arrow), columns
    if hasattr(data, "to_pylist"):
        raw_rows = [dict(row) for row in data.to_pylist()]
        return [jsonify(row) for row in raw_rows], infer_columns(data, raw_rows)
    raw_rows = [dict(row) for row in data]
    return [jsonify(row) for row in raw_rows], infer_columns(None, raw_rows)
