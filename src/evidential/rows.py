"""Semantic synthetic rows for :class:`evidential.EvidentialTable` (ADR-060).

The grouped helpers (:func:`~evidential.grouped_table`,
:func:`~evidential.grouped_records`) generate subtotals and totals for every
grouping level. This module is for the cases they do not cover: a *section* row
that introduces a group, and a *summary* row with a custom label and per-column
values that are computed however the report needs — including from the group's
own rows::

    from evidential import rows

    builder = (
        rows.of(detail)
        .group_by("region")
        .section()
        .summary(
            label="Developing average",
            values={"debt": lambda group: sum(r["debt"] for r in group) / len(group)},
        )
        .total()
    )

    EvidentialTable(rows=builder.build(), columns=[...])

Data rows and synthetic rows are distinct records: a synthetic row carries a
``render_type`` (``row_section`` / ``row_subtotal`` / ``row_total``) and its own
values. Synthetic rows never change the detail records.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .aggregations import BUILTIN_AGGREGATIONS, resolve_aggregation
from .data import jsonify, normalize_data

__all__ = ["Rows", "of"]

#: A per-column summary value: a callable over the group's rows, a built-in
#: aggregation name, or a literal.
Value = Callable[[Sequence[Mapping[str, Any]]], Any] | str | float | int | None


def _numeric_columns(members: Sequence[Mapping[str, Any]]) -> list[str]:
    names: list[str] = []
    for row in members:
        for key, value in row.items():
            if (
                not key.startswith("__")
                and key not in names
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            ):
                names.append(key)
    return names


def _resolve_value(name: str, source: Value, members: Sequence[Mapping[str, Any]]) -> Any:
    if callable(source):
        return source(members)
    if isinstance(source, str) and source.strip().lower() in BUILTIN_AGGREGATIONS:
        values = [row.get(name) for row in members if row.get(name) is not None]
        return resolve_aggregation(source)(values, None) if values else None
    return source


def _resolve_values(spec: Mapping[str, Value] | None, members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if spec is None:
        # A summary/total with no explicit values sums each numeric column.
        return {name: sum(row.get(name, 0) or 0 for row in members) for name in _numeric_columns(members)}
    return {name: _resolve_value(name, source, members) for name, source in spec.items()}


def _resolve_label(
    label: str | Callable[[Sequence[Mapping[str, Any]]], str] | None,
    members: Sequence[Mapping[str, Any]],
    dims: Sequence[str],
) -> str:
    if callable(label):
        return str(label(members))
    if label is not None:
        return str(label)
    return str(members[0].get(dims[0], "")) if dims and members else ""


def _sort_key(row: Mapping[str, Any], dims: Sequence[str]) -> tuple[str, ...]:
    return tuple("" if row.get(dim) is None else str(row.get(dim)) for dim in dims)


@dataclass(frozen=True)
class _Annotation:
    """A summary or total: an optional label, per-column values and a position."""

    label: str | Callable[[Sequence[Mapping[str, Any]]], str] | None = None
    values: Mapping[str, Value] | None = None
    position: str = "bottom"


class Rows:
    """An immutable synthetic-row builder; each method returns a new builder."""

    def __init__(
        self,
        detail: Sequence[Mapping[str, Any]],
        *,
        dims: Sequence[str] = (),
        section: _Annotation | None = None,
        summary: _Annotation | None = None,
        total: _Annotation | None = None,
    ) -> None:
        self._detail = [dict(row) for row in detail]
        self._dims = tuple(dims)
        self._section = section
        self._summary = summary
        self._total = total

    # ----------------------------------------------------------- builders ---
    @classmethod
    def of(cls, data: Any = None, *, rows: Sequence[Mapping[str, Any]] | None = None) -> Rows:
        """Start from detail data (a list of dicts, Arrow table, DataFrame, …)."""
        if rows is not None:
            return cls([jsonify(dict(row)) for row in rows])
        normalized, _ = normalize_data(data)
        return cls(normalized)

    def group_by(self, *dims: str) -> Rows:
        """Set the grouping dimensions; sections and summaries group by the first."""
        if not dims:
            raise ValueError("group_by needs at least one column")
        return self._replace(dims=dims)

    def section(
        self,
        label: str | Callable[[Sequence[Mapping[str, Any]]], str] | None = None,
        *,
        values: Mapping[str, Value] | None = None,
        align: str = "left",
    ) -> Rows:
        """Insert a section row before each group; without a label it names the group."""
        if align not in ("left", "center"):
            raise ValueError("section align is 'left' or 'center'")
        if align == "center" and values:
            raise ValueError("a centered section cannot have summary values")
        return self._replace(section=_Annotation(label, values, align))

    def summary(
        self,
        label: str | Callable[[Sequence[Mapping[str, Any]]], str] | None = None,
        *,
        values: Mapping[str, Value] | None = None,
        position: str = "bottom",
    ) -> Rows:
        """Insert a summary row after (or before) each group."""
        if position not in ("top", "bottom"):
            raise ValueError("summary position is 'top' or 'bottom'")
        return self._replace(summary=_Annotation(label, values, position))

    def total(
        self,
        label: str | Callable[[Sequence[Mapping[str, Any]]], str] | None = "Total",
        *,
        values: Mapping[str, Value] | None = None,
    ) -> Rows:
        """Append a grand-total row computed from every detail row."""
        return self._replace(total=_Annotation(label, values, "bottom"))

    # -------------------------------------------------------------- build ---
    def build(self) -> list[dict[str, Any]]:
        """Return the detail and synthetic rows, ready for ``EvidentialTable``."""
        if not self._dims:
            rows = [{**row, "__row_builder": True} for row in self._detail]
            if self._total is not None:
                rows.append(self._total_row(self._total, self._detail))
            return rows

        detail = sorted(self._detail, key=lambda row: _sort_key(row, self._dims))
        rows: list[dict[str, Any]] = []
        index = 0
        while index < len(detail):
            group_value = detail[index].get(self._dims[0])
            members: list[dict[str, Any]] = []
            while index < len(detail) and detail[index].get(self._dims[0]) == group_value:
                members.append(detail[index])
                index += 1
            group_key = "rows:" + json.dumps(group_value, sort_keys=True)
            metadata = {"__group_key": group_key, "__row_builder": True}
            if self._section is not None:
                rows.append({**self._section_row(self._section, members), **metadata})
            if self._summary is not None and self._summary.position == "top":
                rows.append({**self._summary_row(self._summary, members), **metadata})
            rows.extend(
                {**member, "__parent_key": group_key, "__ancestors": [group_key], "__row_builder": True}
                for member in members
            )
            if self._summary is not None and self._summary.position == "bottom":
                rows.append({**self._summary_row(self._summary, members), **metadata})
        if self._total is not None:
            rows.append(self._total_row(self._total, detail))
        return rows

    def __iter__(self):
        return iter(self.build())

    # ------------------------------------------------------------ helpers ---
    def _replace(self, **changes: Any) -> Rows:
        values: dict[str, Any] = {
            "detail": self._detail,
            "dims": self._dims,
            "section": self._section,
            "summary": self._summary,
            "total": self._total,
        }
        values.update(changes)
        return Rows(**values)

    def _section_row(self, annotation: _Annotation, members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        # Explicit values make this a combined section and summary row.
        row = _resolve_values(annotation.values or {}, members)
        row["render_type"] = "row_section"
        row["__label"] = _resolve_label(annotation.label, members, self._dims)
        row["__align"] = annotation.position
        if annotation.values:
            row["__combined"] = True
        return row

    def _summary_row(self, annotation: _Annotation, members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        row = _resolve_values(annotation.values, members)
        row["render_type"] = "row_subtotal"
        # Level 0 keeps the row flat: no accordion indent and no chevron.
        row["__level"] = 0
        row["__row_builder"] = True
        row["__label"] = _resolve_label(annotation.label, members, self._dims)
        row[self._dims[0]] = _resolve_label(annotation.label, members, self._dims)
        return row

    def _total_row(self, annotation: _Annotation, members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        row = _resolve_values(annotation.values, members)
        row["render_type"] = "row_total"
        row["__level"] = 0
        row["__row_builder"] = True
        row["__label"] = _resolve_label(annotation.label, members, self._dims)
        if self._dims:
            row[self._dims[0]] = _resolve_label(annotation.label, members, self._dims)
        return row


def of(data: Any = None, *, rows: Sequence[Mapping[str, Any]] | None = None) -> Rows:
    """Start a synthetic-row builder from detail data."""
    return Rows.of(data, rows=rows)
