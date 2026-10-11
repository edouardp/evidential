"""The :class:`EvidenceTable` anywidget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import anywidget
import traitlets

from .data import _merge_column_config, infer_columns, jsonify, make_column, normalize_data

__all__ = ["EvidenceTable"]

_ASSET_DIR = Path(__file__).parent / "static"

#: Table-level options forwarded to the browser. Mirrors Evidence's prop names.
_OPTION_KEYS = {
    "title",
    "subtitle",
    "info",
    "info_link",
    "info_link_title",
    "search",
    "page_size",
    "sortable",
    "download",
    "row_shading",
    "row_lines",
    "freeze_columns",
    "wrap",
    "wrap_titles",
    "format_titles",
    "show_total_row",
    "total_label",
    "total_position",
    "subtotal_position",
    "collapsible",
    "collapsed",
    "link",
    "width",
    "max_height",
    "order_columns_by_group",
    "theme",
    "color_scale",
}

_OPTION_DEFAULTS: dict[str, Any] = {
    "title": None,
    "subtitle": None,
    "info": None,
    "info_link": None,
    "info_link_title": None,
    "search": False,
    "page_size": 10,
    "sortable": True,
    "download": True,
    "row_shading": False,
    "row_lines": True,
    "freeze_columns": 0,
    "wrap": False,
    "wrap_titles": True,
    "format_titles": True,
    "show_total_row": False,
    "total_label": "Total",
    "total_position": "bottom",
    "subtotal_position": "bottom",
    "collapsible": False,
    "collapsed": None,
    "link": None,
    "width": None,
    "max_height": None,
    "order_columns_by_group": True,
    "theme": None,
    "color_scale": None,
}


def _coerce_column(column: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(column, str):
        return make_column(column)
    data = dict(column)
    name = data.pop("name", None)
    if not name:
        raise ValueError(f"column definition is missing a name: {column!r}")
    type_ = data.pop("type", "string")
    return make_column(str(name), type=type_, **data)


def _coerce_columns(
    columns: Iterable[str | Mapping[str, Any]] | None,
    column_config: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if columns is None:
        columns = []
    result = [_coerce_column(column) for column in columns]
    return _merge_column_config(result, column_config)


def _apply_column_groups(
    columns: list[dict[str, Any]],
    groups: Mapping[str, Sequence[str]] | None,
) -> list[dict[str, Any]]:
    """Assign ``column_group`` from a ``{group: [column, ...]}`` mapping.

    Column order is left to the frontend, which clusters each group at its
    first occurrence so a leading dimension column (e.g. a date) keeps its
    place.
    """
    if not groups:
        return columns
    result = [dict(column) for column in columns]
    by_name = {column["name"]: column for column in result}
    for group, names in groups.items():
        for name in names:
            column = by_name.get(name)
            if column is not None:
                column["column_group"] = group
    return result


class EvidenceTable(anywidget.AnyWidget):
    """An Evidence-style interactive data table.

    ``data`` accepts a list of dicts, a pandas DataFrame, a pyarrow Table, a
    DuckDB relation, or a list of those. ``columns`` describes per-column
    formatting/visualisation; when omitted it is inferred from ``data``.
    ``column_config`` is a convenience mapping of ``name -> overrides`` that is
    merged onto the inferred or explicit columns. ``column_groups`` maps a group
    title to the column names it spans and renders them under a shared header
    (hierarchical columns).

    Table-level display options (``title``, ``search``, ``page_size``,
    ``freeze_columns``, ``collapsible``, ``order_columns_by_group``, ...) are
    plain keyword arguments. Any remaining keyword arguments are forwarded to
    :class:`anywidget.AnyWidget`.
    """

    _esm = _ASSET_DIR / "table.js"
    _css = _ASSET_DIR / "table.css"

    rows = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
    columns = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
    options = traitlets.Dict(default_value={}).tag(sync=True)

    def __init__(
        self,
        data: Any = None,
        *,
        rows: Sequence[Mapping[str, Any]] | None = None,
        columns: Iterable[str | Mapping[str, Any]] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Sequence[str]] | None = None,
        **options: Any,
    ) -> None:
        table_options = {key: options.pop(key) for key in list(options) if key in _OPTION_KEYS}

        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        if columns is None and inferred:
            columns = inferred
        coerced = _apply_column_groups(_coerce_columns(columns, column_config), column_groups)

        merged_options = dict(_OPTION_DEFAULTS)
        merged_options.update(table_options)

        super().__init__(
            rows=normalized_rows,
            columns=coerced,
            options=merged_options,
            **options,
        )

    # ------------------------------------------------------------- helpers ---
    def set_data(
        self,
        data: Any = None,
        *,
        rows: Sequence[Mapping[str, Any]] | None = None,
        columns: Iterable[str | Mapping[str, Any]] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Sequence[str]] | None = None,
    ) -> EvidenceTable:
        """Replace the table data, keeping the current options."""
        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        if columns is None:
            columns = inferred
        if columns is not None:
            self.columns = _apply_column_groups(
                _coerce_columns(columns, column_config), column_groups
            )
        self.rows = normalized_rows
        return self

    def update_options(self, **options: Any) -> EvidenceTable:
        """Update one or more table-level display options."""
        current = dict(self.options)
        current.update({k: v for k, v in options.items() if k in _OPTION_KEYS})
        self.options = current
        return self

    def set_column(self, name: str, **overrides: Any) -> EvidenceTable:
        """Merge overrides into a single column definition."""
        columns = [dict(column) for column in self.columns]
        for column in columns:
            if column["name"] == name:
                column.update(overrides)
                break
        else:
            columns.append(_coerce_column({"name": name, **overrides}))
        self.columns = columns
        return self

    # ---------------------------------------------------------- constructors --
    @classmethod
    def from_arrow(cls, table: Any, **kwargs: Any) -> EvidenceTable:
        """Build a table from a pyarrow Table."""
        return cls(table, **kwargs)

    @classmethod
    def from_pandas(cls, frame: Any, **kwargs: Any) -> EvidenceTable:
        """Build a table from a pandas DataFrame."""
        return cls(frame, **kwargs)

    @classmethod
    def from_records(
        cls, records: Sequence[Mapping[str, Any]], **kwargs: Any
    ) -> EvidenceTable:
        """Build a table from a list of dicts."""
        return cls(list(records), **kwargs)

    @classmethod
    def from_duckdb(cls, connection: Any, sql: str, **kwargs: Any) -> EvidenceTable:
        """Run ``sql`` on a DuckDB connection and wrap the result."""
        return cls(connection.sql(sql), **kwargs)
