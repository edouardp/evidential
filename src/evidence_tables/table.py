"""The :class:`EvidenceTable` anywidget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import anywidget
import traitlets

from .data import _merge_column_config, apply_blank_predicates, infer_columns, jsonify, make_column, normalize_data
from .rules import resolve_rules

__all__ = ["EvidenceTable"]

_ASSET_DIR = Path(__file__).parent / "static"

#: Table-level options forwarded to the browser. Mirrors Evidence's prop names.
_OPTION_KEYS = {
    "title",
    "subtitle",
    "caption",
    "null_text",
    "stub",
    "stub_head",
    "footnote_marks",
    "all_caps",
    "stretch",
    "align_decimals",
    "group_gap",
    "rotate_titles",
    "figure_style",
    "footnote_column",
    "footnotes",
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
    "groups_open",
    "group_type",
    "link",
    "width",
    "max_height",
    "order_columns_by_group",
    "row_numbers",
    "column_stats",
    "compact",
    "empty_message",
    "default_sort",
    "row_conditional_colors",
    "show_link_column",
    "header_color",
    "header_font_color",
    "total_row_color",
    "total_font_color",
    "background_color",
    "theme",
    "color_scale",
}

_OPTION_DEFAULTS: dict[str, Any] = {
    "title": None,
    "subtitle": None,
    "caption": None,
    "null_text": None,
    "stub": None,
    "stub_head": None,
    "footnote_marks": None,
    "all_caps": False,
    "stretch": True,
    "align_decimals": False,
    "group_gap": False,
    "rotate_titles": None,
    "figure_style": None,
    "footnote_column": None,
    "footnotes": None,
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
    "groups_open": None,
    "group_type": None,
    "link": None,
    "width": None,
    "max_height": None,
    "order_columns_by_group": True,
    "row_numbers": False,
    "column_stats": False,
    "compact": False,
    "empty_message": "No records",
    "default_sort": None,
    "row_conditional_colors": None,
    "show_link_column": False,
    "header_color": None,
    "header_font_color": None,
    "total_row_color": None,
    "total_font_color": None,
    "background_color": None,
    "theme": None,
    "color_scale": None,
}


# Evidence `contentType` → (viz, sparkline type)
_CONTENT_TYPES: dict[str, tuple[str | None, str | None]] = {
    "sparkline": ("sparkline", "line"),
    "sparkarea": ("sparkline", "area"),
    "sparkbar": ("sparkline", "bar"),
    "bar": ("bar", None),
    "color": ("color", None),
    "colorscale": ("color", None),
    "chip": ("chip", None),
    "delta": ("delta", None),
}

# Evidence camelCase column attributes → our snake_case keys.
_COLUMN_ALIASES = {
    "contentType": "content_type",
    "colGroup": "column_group",
    "col_group": "column_group",
    "fmtColumn": "fmt_column",
    "redNegatives": "red_negatives",
    "linkLabel": "link_label",
    "openInNewTab": "link_new_tab",
    "wrapTitle": "wrap_title",
    "description": "info",
    "sortBy": "sort_by",
    "sortColumn": "sort_by",
    "highlightColor": "highlight",
    "highlight_color": "highlight",
}


def _normalize_column_options(data: dict[str, Any]) -> dict[str, Any]:
    """Merge Evidence-style top-level column options into nested option dicts.

    Allows ergonomic, Evidence-compatible configs such as
    ``{"color_scale": "green", "sparkY": "sales"}`` to populate
    ``color_options`` / ``sparkline_options`` / ``bar_options`` / etc.
    """
    color = dict(data.get("color_options") or {})
    for key in (
        "color_scale",
        "color_stops",
        "scale_column",
        "scale_mode",
        "conditional_colors",
    ):
        if key in data:
            color.setdefault(key, data.pop(key))
    for camel, snake in (("colorMin", "min"), ("colorMax", "max"), ("colorMid", "midpoint")):
        if camel in data:
            color.setdefault(snake, data.pop(camel))
    for key, target in (("color_min", "min"), ("color_max", "max"), ("color_mid", "midpoint")):
        if key in data:
            color.setdefault(target, data.pop(key))
    if color:
        data["color_options"] = color

    spark = dict(data.get("sparkline_options") or {})
    for camel, snake in (
        ("sparkX", "x"),
        ("sparkY", "y"),
        ("sparkColor", "color"),
        ("sparkHeight", "height"),
        ("sparkWidth", "width"),
        ("sparkType", "type"),
        ("sparkYScale", "fit_to_data"),
        ("sparkYFmt", "y_fmt"),
    ):
        if camel in data:
            spark.setdefault(snake, data.pop(camel))
    for key in ("spark_x", "spark_y", "spark_color", "spark_height", "spark_width", "spark_type"):
        if key in data:
            spark.setdefault(key[len("spark_") :], data.pop(key))
    if "spark_y_scale" in data:
        spark.setdefault("fit_to_data", data.pop("spark_y_scale"))
    if spark:
        data["sparkline_options"] = spark

    bar = dict(data.get("bar_options") or {})
    for camel, snake in (
        ("barColor", "bar_color"),
        ("negativeBarColor", "bar_color_negative"),
        ("hideLabels", "hide_labels"),
        ("fitToData", "fit_to_data"),
    ):
        if camel in data:
            bar.setdefault(snake, data.pop(camel))
    if bar:
        data["bar_options"] = bar

    delta = dict(data.get("delta_options") or {})
    for camel, snake in (
        ("deltaSymbol", "show_symbol"),
        ("downIsGood", "down_is_good"),
        ("showValue", "show_value"),
        ("neutralMin", "neutral_min"),
        ("neutralMax", "neutral_max"),
        ("chip", "chip"),
    ):
        if camel in data:
            delta.setdefault(snake, data.pop(camel))
    # Allow the delta options (incl. a neutral range) at the top level too.
    for key in (
        "down_is_good",
        "show_symbol",
        "show_value",
        "symbol_position",
        "neutral_range",
        "neutral_min",
        "neutral_max",
        "chip",
    ):
        if key in data:
            delta.setdefault(key, data.pop(key))
    if delta:
        data["delta_options"] = delta

    image = dict(data.get("image_options") or {})
    for key in ("height", "width", "alt"):
        if key in data:
            image.setdefault(key, data.pop(key))
    if image:
        data["image_options"] = image

    # Accept `comment` / `description` as aliases for the header description.
    # These win over an inferred `info` (e.g. a DuckDB comment) because an
    # explicit `column_config` should override the source.
    for key in ("comment", "description"):
        if key in data:
            data["info"] = data.pop(key)
    # `sort_by` (camelCase too) — sort this column by another column's values.
    for key in ("sortBy", "sortColumn", "sort_column"):
        if key in data and "sort_by" not in data:
            data["sort_by"] = data.pop(key)
    # `highlight` (camelCase too) — a background band for the whole column.
    for key in ("highlightColor", "highlight_color"):
        if key in data and "highlight" not in data:
            data["highlight"] = data.pop(key)
    return data


def section_row(label: str) -> dict[str, Any]:
    """Return a full-width section divider row for :class:`EvidenceTable`."""
    return {"render_type": "row_section", "__label": label}


def _coerce_column(column: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(column, str):
        return make_column(column)
    data = dict(column)
    for camel, snake in _COLUMN_ALIASES.items():
        if camel in data and snake not in data:
            data[snake] = data.pop(camel)
    data = _normalize_column_options(data)
    name = data.pop("name", None)
    if not name:
        raise ValueError(f"column definition is missing a name: {column!r}")
    content_type = data.pop("content_type", None)
    if content_type:
        viz, spark_type = _CONTENT_TYPES.get(str(content_type).lower(), (None, None))
        if viz:
            data.setdefault("viz", viz)
        if spark_type:
            spark = dict(data.get("sparkline_options") or {})
            spark.setdefault("type", spark_type)
            data["sparkline_options"] = spark
        if content_type == "html":
            data.setdefault("html", True)
        if content_type == "link":
            data.setdefault("link", str(name))
        if content_type == "image":
            data.setdefault("image", str(name))
        if content_type == "logo":
            data.setdefault("logo", str(name))
    type_ = data.pop("type", "string")
    return make_column(str(name), type=type_, **data)


def _coerce_columns(
    columns: Iterable[str | Mapping[str, Any]] | None,
    column_config: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    columns = list(columns) if columns is not None else []
    result = [_coerce_column(column) for column in columns]
    merged = _merge_column_config(result, column_config)
    # Template columns (cols_merge*) may not exist in the data; synthesise them.
    if column_config:
        existing = {column["name"] for column in merged}
        for name, config in column_config.items():
            if name in existing or not isinstance(config, Mapping):
                continue
            if config.get("template"):
                merged.append(_coerce_column({"name": name, **config}))
    # column_config overrides bypass _coerce_column, so normalise them too, and
    # drop Python callables (e.g. `blank`) that can't cross the JSON boundary.
    return [_normalize_column_options({k: v for k, v in dict(column).items() if not callable(v)}) for column in merged]


def _center_chips(
    columns: list[dict[str, Any]],
    column_config: Mapping[str, Mapping[str, Any]] | None,
    explicit_columns: list[Any] | None,
) -> list[dict[str, Any]]:
    """A chip is centred unless the column asks for another alignment.

    The type-derived default (numbers right, text left) must not win, so only an
    explicit ``align`` — in ``column_config`` or an explicit column definition —
    keeps a chip off-centre.
    """
    explicit = {
        str(column.get("name"))
        for column in explicit_columns or []
        if isinstance(column, Mapping) and column.get("align") is not None
    }
    if column_config:
        explicit.update(
            str(name)
            for name, config in column_config.items()
            if isinstance(config, Mapping) and config.get("align") is not None
        )
    for column in columns:
        if column.get("viz") == "chip" and column["name"] not in explicit:
            column["align"] = "center"
    return columns


def _resolve_column_groups(
    columns: list[dict[str, Any]],
    groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Assign each column's ``column_group``.

    ``groups`` maps ``{group: [column, ...]}`` and always wins; a group may also
    be ``{"columns": [...], "highlight": "#..."}`` to highlight every column in
    it. Otherwise a column whose name contains a dot takes the part before the
    **last** dot as its group — the ``"group.column"`` convention — and extra
    dots nest: ``"Root.Sub.Leaf"`` groups under ``["Root", "Sub"]``. The name
    itself is left untouched: the frontend's ``formatTitle`` already shows only
    the trailing segment as the leaf label.

    Column order is left to the frontend, which clusters each group at its
    first occurrence so a leading dimension column (e.g. a date) keeps its
    place.
    """
    result = [dict(column) for column in columns]
    if groups:
        by_name = {column["name"]: column for column in result}
        for group, spec in groups.items():
            # A group is a list of columns, or a mapping with those columns and
            # a highlight colour for the whole group.
            if isinstance(spec, Mapping):
                names = spec.get("columns") or []
                highlight = spec.get("highlight") or spec.get("highlight_color")
            else:
                names = spec
                highlight = None
            for name in names:
                column = by_name.get(name)
                if column is None:
                    continue
                column["column_group"] = group
                if highlight and not column.get("highlight"):
                    column["highlight"] = highlight
    for column in result:
        if not column.get("column_group"):
            head, _, leaf = str(column.get("name", "")).rpartition(".")
            if head and leaf:
                segments = [segment for segment in head.split(".") if segment]
                if len(segments) == 1:
                    column["column_group"] = segments[0]
                elif segments:
                    column["column_group"] = segments
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
    #: When true the renderer dims the current table and shows a spinner without
    #: changing its size (used while a live query is in flight).
    loading = traitlets.Bool(False).tag(sync=True)

    def __init__(
        self,
        data: Any = None,
        *,
        rows: Sequence[Mapping[str, Any]] | None = None,
        columns: Iterable[str | Mapping[str, Any]] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None = None,
        rules: Iterable[Mapping[str, Any]] | None = None,
        **options: Any,
    ) -> None:
        table_options = {key: options.pop(key) for key in list(options) if key in _OPTION_KEYS}
        self._rules = list(rules) if rules else None

        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        explicit_columns = list(columns) if columns is not None else None
        had_explicit_columns = explicit_columns is not None
        if columns is None and inferred:
            columns = inferred
        normalized_rows = apply_blank_predicates(normalized_rows, column_config)
        normalized_rows, client_rules = resolve_rules(normalized_rows, rules)
        coerced = _resolve_column_groups(_coerce_columns(columns, column_config), column_groups)
        coerced = _center_chips(coerced, column_config, explicit_columns)

        merged_options = dict(_OPTION_DEFAULTS)
        merged_options.update(table_options)
        if client_rules:
            merged_options["rules"] = client_rules
        if merged_options.get("groups_open") is not None and "collapsed" not in table_options:
            merged_options["collapsed"] = not merged_options["groups_open"]

        link = merged_options.get("link")
        if link and not had_explicit_columns and not merged_options.get("show_link_column"):
            link_column = next((column for column in coerced if column["name"] == link), None)
            if link_column is not None:
                link_column["hide"] = True

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
        column_groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None = None,
    ) -> EvidenceTable:
        """Replace the table data, keeping the current options."""
        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        explicit_columns = list(columns) if columns is not None else None
        if columns is None:
            columns = inferred
        if columns is not None:
            new_columns = _resolve_column_groups(_coerce_columns(columns, column_config), column_groups)
            new_columns = _center_chips(new_columns, column_config, explicit_columns)
            # Setting columns triggers a browser re-render; only do it when the
            # column structure actually changed so data-only updates render once.
            if new_columns != list(self.columns):
                self.columns = new_columns
        normalized_rows = apply_blank_predicates(normalized_rows, column_config)
        normalized_rows, client_rules = resolve_rules(normalized_rows, self._rules)
        self.rows = normalized_rows
        if client_rules:
            current = dict(self.options)
            current["rules"] = client_rules
            self.options = current
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
    def from_records(cls, records: Sequence[Mapping[str, Any]], **kwargs: Any) -> EvidenceTable:
        """Build a table from a list of dicts."""
        return cls(list(records), **kwargs)

    @classmethod
    def from_duckdb(cls, connection: Any, sql: str, **kwargs: Any) -> EvidenceTable:
        """Run ``sql`` on a DuckDB connection and wrap the result."""
        return cls(connection.sql(sql), **kwargs)
