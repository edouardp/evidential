"""The :class:`EvidentialTable` anywidget."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Unpack

import anywidget
import traitlets

from ._column_options import _normalize_column_options
from ._domain import resolve_domains
from ._row_layout import display_records, split_legacy, unwrap_view
from .configuration import TABLE_DEFAULTS, TableOptions, unknown_option, validate_options
from .data import _merge_column_config, apply_blank_predicates, infer_columns, jsonify, make_column, normalize_data
from .marks import apply_hidden_columns, resolve_encodings
from .rows import Rows, RowView
from .rules import resolve_rules

__all__ = ["EvidentialTable"]

_ASSET_DIR = Path(__file__).parent / "static"

#: Table-level options forwarded to the browser. Mirrors Evidence's prop names.
_OPTION_KEYS = set(TableOptions.__annotations__)
_OPTION_DEFAULTS = TABLE_DEFAULTS
_UNSET = object()


def section_row(label: str, *, align: str = "left") -> dict[str, Any]:
    """Return a full-width section divider row for :class:`EvidentialTable`.

    ``align`` places the label: ``"left"`` (default) or ``"center"``. A
    centered section carries its meaning in the label alone, so it has no
    summary cells.
    """
    if align not in ("left", "center"):
        raise ValueError("section_row align is 'left' or 'center'")
    return {"render_type": "row_section", "__label": label, "__align": align}


def spacer_row(height: int | float | None = None) -> dict[str, Any]:
    """Return a blank spacer row, e.g. to separate blocks without a label.

    ``height`` is a pixel number or a CSS length; without one the row uses the
    table's default row height.
    """
    row: dict[str, Any] = {"render_type": "row_spacer"}
    if height is not None:
        row["__height"] = height
    return row


def _flatten_columns(columns: Iterable[Any]) -> Iterator[Any]:
    """Yield columns, flattening the groups built by ``col.subcolumns`` / ``col.group``.

    A ``Column`` is a ``Mapping`` and a column name is a ``str``, so neither is
    treated as a group; any other sequence is expanded (and may nest).
    """
    for item in columns:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, Mapping)):
            yield from _flatten_columns(item)
        else:
            yield item


def _coerce_column(column: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(column, str):
        return make_column(column)
    data = dict(column)
    data = _normalize_column_options(data)
    name = data.pop("name", None)
    if not name:
        raise ValueError(f"column definition is missing a name: {column!r}")
    type_ = data.pop("type", "string")
    return make_column(str(name), type=type_, **data)


def _with_inferred(column: Any, inferred_by_name: Mapping[str, dict[str, Any]]) -> Any:
    """Resolve a spec that does not say what a column is to its inferred definition.

    `col.auto("x")` (and a bare name) carries no ``type``, so it takes the type,
    format, alignment and ``info`` inferred from the data, then applies its own
    options over them.
    """
    if isinstance(column, str):
        return inferred_by_name.get(column, column)
    if isinstance(column, Mapping) and not column.get("type"):
        base = inferred_by_name.get(str(column.get("name")))
        if base is not None:
            merged = dict(base)
            # Normalize first: aliases (`redNegatives` → `red_negatives`) must win
            # over the inferred base's explicit ``False`` defaults.
            merged.update(_normalize_column_options(dict(column)))
            return merged
    return column


def _coerce_columns(
    columns: Iterable[Any] | None,
    column_config: Mapping[str, Mapping[str, Any]] | None,
    inferred: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    inferred_by_name = {str(column["name"]): dict(column) for column in (inferred or [])}
    columns = list(_flatten_columns(columns)) if columns is not None else []
    result = [_coerce_column(_with_inferred(column, inferred_by_name)) for column in columns]
    normalized_config = {
        name: _normalize_column_options({"name": name, **config}) for name, config in (column_config or {}).items()
    }
    merged = _merge_column_config(result, normalized_config)
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
        for column in _flatten_columns(explicit_columns or [])
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


def _prepare_columns_and_rows(
    source_rows: Sequence[Mapping[str, Any]],
    inferred: Sequence[Mapping[str, Any]] | None,
    explicit_columns: list[Any] | None,
    column_config: Mapping[str, Mapping[str, Any]] | None,
    column_groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None,
    rules: Iterable[Mapping[str, Any]] | None,
    options: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Prepare Python display values before resolving any callable mark bindings.

    All public construction/update paths start from the retained source snapshot,
    never from rows that already contain transforms or generated helper fields.
    """
    columns = explicit_columns if explicit_columns is not None else inferred or []
    blanks = {str(column["name"]): dict(column) for column in _flatten_columns(columns) if isinstance(column, Mapping)}
    for name, config in (column_config or {}).items():
        blanks[name] = {**blanks.get(name, {}), **config}
    prepared = apply_blank_predicates(copy.deepcopy(source_rows), blanks)
    prepared, client_rules = resolve_rules(prepared, rules)
    coerced = _resolve_column_groups(_coerce_columns(columns, column_config, inferred), column_groups)
    coerced = _center_chips(coerced, column_config, explicit_columns)
    coerced = resolve_domains(coerced)
    coerced, hidden = resolve_encodings(coerced, prepared)
    apply_hidden_columns(prepared, hidden)
    link = options.get("link")
    if link and explicit_columns is None and not options.get("show_link_column"):
        for column in coerced:
            if column["name"] == link:
                column["hide"] = True
    return prepared, coerced, client_rules


def _merge_options(current: Mapping[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize constructor and mutation options with identical precedence."""
    merged = {**current, **updates}
    if "groups_open" in updates and updates["groups_open"] is not None and "collapsed" not in updates:
        merged["collapsed"] = not updates["groups_open"]
    return merged


class EvidentialTable(anywidget.AnyWidget):
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
    #: Display annotations and group membership, separate from source records.
    row_layout = traitlets.Dict(default_value={}).tag(sync=True)
    #: When true the renderer dims the current table and shows a spinner without
    #: changing its size (used while a live query is in flight).
    loading = traitlets.Bool(False).tag(sync=True)
    #: The value of the ``select`` column for the clicked row (or None). Set by
    #: the browser; reading it in another cell makes the table drive the graph.
    selected = traitlets.Any(None).tag(sync=True)

    def __init__(
        self,
        data: Any = None,
        *,
        rows: Sequence[Mapping[str, Any]] | RowView | Rows | None = None,
        row_layout: Rows | None = None,
        columns: Iterable[str | Mapping[str, Any]] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None = None,
        rules: Iterable[Mapping[str, Any]] | None = None,
        settings: Mapping[str, Any] | None = None,
        **options: Any,
    ) -> None:
        if settings is not None:
            validate_options(settings, TableOptions, "table")
            options = {**settings, **options}
        allowed = _OPTION_KEYS | set(type(self).class_traits())
        for key in options:
            if key not in allowed:
                raise unknown_option(key, sorted(allowed), "table")
        table_options = {key: options.pop(key) for key in list(options) if key in _OPTION_KEYS}
        validate_options(table_options, TableOptions, "table")
        self._rules = list(rules) if rules else None
        self._explicit_columns = list(columns) if columns is not None else None
        self._column_overrides = {name: dict(config) for name, config in (column_config or {}).items()}
        self._configured_groups = column_groups
        data, rows, row_layout = unwrap_view(data, rows, row_layout)
        self._row_layout_spec = row_layout

        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        normalized_rows, layout = split_legacy(normalized_rows)
        if layout:
            if row_layout is not None:
                raise ValueError("row_layout expects detail data, not injected synthetic records")
            inferred = infer_columns(None, normalized_rows)
        elif row_layout is not None:
            layout = row_layout.compile(normalized_rows)

        self._source_rows = [dict(row) for row in normalized_rows]
        self._inferred_columns = inferred
        merged_options = _merge_options(_OPTION_DEFAULTS, table_options)
        normalized_rows, coerced, client_rules = _prepare_columns_and_rows(
            self._source_rows,
            inferred,
            self._explicit_columns,
            self._column_overrides,
            column_groups,
            self._rules,
            merged_options,
        )
        if client_rules:
            merged_options["rules"] = client_rules

        super().__init__(
            rows=normalized_rows,
            columns=coerced,
            options=merged_options,
            row_layout=layout,
            **options,
        )

    # ------------------------------------------------------------- helpers ---
    @property
    def display_rows(self) -> list[dict[str, Any]]:
        """Unfiltered display snapshot for inspection; ``rows`` is detail data."""
        return display_records(self.rows, self.row_layout)

    def set_data(
        self,
        data: Any = None,
        *,
        rows: Sequence[Mapping[str, Any]] | RowView | Rows | None = None,
        row_layout: Any = _UNSET,
        columns: Iterable[str | Mapping[str, Any]] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Sequence[str] | Mapping[str, Any]] | None = None,
    ) -> EvidentialTable:
        """Replace data, retaining column configuration unless replaced explicitly."""
        layout_spec = self._row_layout_spec if row_layout is _UNSET else row_layout
        if isinstance(rows if rows is not None else data, (Rows, RowView)):
            layout_spec = None if row_layout is _UNSET else row_layout
        data, rows, layout_spec = unwrap_view(data, rows, layout_spec)
        explicit_columns = list(columns) if columns is not None else self._explicit_columns
        column_config = (
            {name: dict(config) for name, config in column_config.items()}
            if column_config is not None
            else self._column_overrides
        )
        column_groups = column_groups if column_groups is not None else self._configured_groups
        for name, config in column_config.items():
            _normalize_column_options({"name": name, **config})
        if rows is None:
            normalized_rows, inferred = normalize_data(data)
        else:
            raw_rows = [dict(row) for row in rows]
            normalized_rows = [jsonify(row) for row in raw_rows]
            inferred = infer_columns(None, raw_rows)

        normalized_rows, layout = split_legacy(normalized_rows)
        if layout:
            if layout_spec is not None:
                raise ValueError("row_layout expects detail data, not injected synthetic records")
            inferred = infer_columns(None, normalized_rows)
        elif layout_spec is not None:
            layout = layout_spec.compile(normalized_rows)

        source_rows = [dict(row) for row in normalized_rows]
        normalized_rows, new_columns, client_rules = _prepare_columns_and_rows(
            source_rows,
            inferred,
            explicit_columns,
            column_config,
            column_groups,
            self._rules,
            self.options,
        )
        # Commit configuration and synced state only after all preparation succeeds.
        self._source_rows = source_rows
        self._inferred_columns = inferred
        self._explicit_columns = explicit_columns
        self._column_overrides = {name: dict(config) for name, config in column_config.items()}
        self._configured_groups = column_groups
        self._row_layout_spec = layout_spec
        with self.hold_sync():
            if new_columns != list(self.columns):
                self.columns = new_columns
            self.rows = normalized_rows
            self.row_layout = layout
            if client_rules:
                current = dict(self.options)
                current["rules"] = client_rules
                self.options = current
        return self

    def update_options(self, **options: Unpack[TableOptions]) -> EvidentialTable:
        """Update one or more table-level display options."""
        validate_options(options, TableOptions, "table")
        current = _merge_options(self.options, options)
        columns = [dict(column) for column in self.columns]
        if self._explicit_columns is None and {"link", "show_link_column"}.intersection(options):
            # Restore configured visibility before applying automatic link hiding.
            # Display-only option changes must not evaluate user callbacks again.
            configured = _coerce_columns(self._inferred_columns, self._column_overrides)
            visibility = {column["name"]: column.get("hide", False) for column in configured}
            for column in columns:
                column["hide"] = visibility.get(column["name"], False)
                if column["name"] == current.get("link") and not current.get("show_link_column"):
                    column["hide"] = True
        with self.hold_sync():
            self.options = current
            if columns != list(self.columns):
                self.columns = columns
        return self

    def set_column(self, name: str, **overrides: Any) -> EvidentialTable:
        """Merge column overrides and recompute display values and callable sources."""
        normalized = _normalize_column_options({"name": name, **overrides})
        config = {key: dict(value) for key, value in self._column_overrides.items()}
        config[name] = {**config.get(name, {}), **normalized}
        explicit = self._explicit_columns
        if not any(column["name"] == name for column in self.columns):
            explicit = [*(explicit if explicit is not None else self._inferred_columns or []), {"name": name}]
        prepared, columns, client_rules = _prepare_columns_and_rows(
            self._source_rows,
            self._inferred_columns,
            explicit,
            config,
            self._configured_groups,
            self._rules,
            self.options,
        )
        self._column_overrides = config
        self._explicit_columns = explicit
        with self.hold_sync():
            self.columns = columns
            self.rows = prepared
            if client_rules:
                self.options = {**self.options, "rules": client_rules}
        return self

    # ---------------------------------------------------------- constructors --
    @classmethod
    def from_arrow(cls, table: Any, **kwargs: Any) -> EvidentialTable:
        """Build a table from a pyarrow Table."""
        return cls(table, **kwargs)

    @classmethod
    def from_pandas(cls, frame: Any, **kwargs: Any) -> EvidentialTable:
        """Build a table from a pandas DataFrame."""
        return cls(frame, **kwargs)

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, Any]], **kwargs: Any) -> EvidentialTable:
        """Build a table from a list of dicts."""
        return cls(list(records), **kwargs)

    @classmethod
    def from_duckdb(cls, connection: Any, sql: str, **kwargs: Any) -> EvidentialTable:
        """Run ``sql`` on a DuckDB connection and wrap the result."""
        return cls(connection.sql(sql), **kwargs)
