"""Live, parameterised tables for Marimo.

:class:`LiveEvidenceTable` is an :class:`~evidence_tables.EvidenceTable` that
keeps a parameterised SQL query and re-runs it when its controls change —
without recreating the widget, so sort/search/page state is preserved.

Inside Marimo the idiomatic pattern is a persistent widget plus a reactive cell
(referencing a control registers a Marimo dependency, so that cell re-runs on
change)::

    # cell 1
    min_fare = mo.ui.slider(0, 100, value=10, label="Minimum fare")
    min_fare

    # cell 2 — persistent widget, no control references
    live = LiveEvidenceTable(
        con,
        "SELECT * FROM trips WHERE fare_amount >= {min_fare}",
        auto_run=False,
    )
    live

    # cell 3 — re-runs whenever the slider changes
    _ = live.set_controls(min_fare=min_fare)

Outside a reactive host (plain ipywidgets), pass ``bind_controls=True`` and the
widget re-runs itself on control changes::

    live = LiveEvidenceTable(
        con,
        "SELECT * FROM trips WHERE fare_amount >= {min_fare}",
        params={"min_fare": min_fare},
        bind_controls=True,
    )

Either way, values are bound as SQL parameters (never spliced into the SQL).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

import traitlets

from .table import EvidenceTable

__all__ = ["LiveEvidenceTable", "query_values"]

# `${name}`, `$name` and `{name}` placeholders in plain string SQL.
_PARAM_RE = re.compile(r"\$\{(\w+)\}|\$(\w+)|\{(\w+)\}")


def _value_of(control: Any) -> Any:
    """Unwrap a Marimo/ipywidgets control to its current value."""
    return getattr(control, "value", control)


def query_values(connection: Any, sql: str) -> list[Any]:
    """Return the first column of ``sql`` as a list (for populating selectors)."""
    result = connection.sql(sql)
    rows = result.to_arrow_table().to_pylist() if hasattr(result, "to_arrow_table") else result.fetchall()
    return [next(iter(row.values())) if isinstance(row, dict) else row[0] for row in rows]


class LiveEvidenceTable(EvidenceTable):
    """An Evidence table backed by a query that re-runs on control changes."""

    sql = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        connection: Any,
        sql: Any = None,
        *,
        params: Mapping[str, Any] | None = None,
        column_config: Mapping[str, Mapping[str, Any]] | None = None,
        column_groups: Mapping[str, Iterable[str]] | None = None,
        auto_run: bool = True,
        bind_controls: bool = False,
        **options: Any,
    ) -> None:
        self._connection = connection
        self._sql_template = sql
        self._params: dict[str, Any] = dict(params or {})
        self._column_config = column_config
        self._column_groups = column_groups
        self._bind_controls_enabled = bind_controls
        self._bound: dict[int, Any] = {}
        super().__init__(rows=[], columns=[], **options)
        if bind_controls:
            self._bind_controls()
        if auto_run and sql is not None:
            self.run()

    @property
    def connection(self) -> Any:
        """The DuckDB connection used to run queries."""
        return self._connection

    def run(self, sql: Any = None, params: Mapping[str, Any] | None = None) -> LiveEvidenceTable:
        """(Re-)run the query, optionally replacing the SQL or parameter mapping."""
        if sql is not None:
            self._sql_template = sql
        if params is not None:
            self._params = dict(params)
        if self._bind_controls_enabled:
            self._bind_controls()
        statement, values = self._prepare(self._sql_template, self._params)
        relation = (
            self._connection.execute(statement, values)
            if values
            else self._connection.sql(statement)
        )
        self.set_data(
            relation,
            column_config=self._column_config,
            column_groups=self._column_groups,
        )
        self.sql = statement
        return self

    def set_controls(self, **params: Any) -> LiveEvidenceTable:
        """Add or replace bound parameters and re-run."""
        self._params.update(params)
        self.run()
        return self

    # --------------------------------------------------------------- helpers --
    def _prepare(self, template: Any, params: Mapping[str, Any]) -> tuple[str, list[Any]]:
        if template is None:
            raise ValueError("LiveEvidenceTable has no SQL to run")
        # PEP 750 t-string: one `?` per interpolation.
        if hasattr(template, "strings") and hasattr(template, "interpolations"):
            parts: list[str] = []
            values: list[Any] = []
            for index, text in enumerate(template.strings):
                parts.append(text)
                if index < len(template.interpolations):
                    parts.append("?")
                    values.append(_value_of(template.interpolations[index].value))
            return "".join(parts), values
        # Plain string: replace `$name` / `{name}` with `?` and bind positionally.
        resolved = {name: _value_of(control) for name, control in params.items()}
        positional: list[Any] = []

        def replace(match: re.Match[str]) -> str:
            name = match.group(1) or match.group(2) or match.group(3)
            if name not in resolved:
                raise KeyError(
                    f"Unknown SQL parameter {name!r}; known parameters: {sorted(resolved)}"
                )
            positional.append(resolved[name])
            return "?"

        return _PARAM_RE.sub(replace, str(template)), positional

    def _iter_controls(self) -> Iterable[Any]:
        yield from self._params.values()
        template = self._sql_template
        if hasattr(template, "interpolations"):
            for interpolation in template.interpolations:
                yield interpolation.value

    def _bind_controls(self) -> None:
        """Attach a re-run callback to any control we haven't seen before.

        Marimo forbids replacing a public ``on_change`` after construction, so
        we chain onto the private handler it already calls.
        """
        for control in self._iter_controls():
            if not hasattr(control, "_on_change"):
                continue
            key = id(control)
            if key in self._bound:
                continue
            self._bound[key] = control
            existing = getattr(control, "_on_change", None)

            def handler(value: Any = None, _existing: Any = existing) -> None:
                if callable(_existing):
                    _existing(value)
                self.run()

            control._on_change = handler
