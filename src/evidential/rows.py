"""Display-only group headings and summaries, separate from detail data.

Use ``EvidentialTable(data, row_layout=rows.group_by("region").section()
.summary(values={"sales": "sum"}).grand_summary())``. The bound ``of(data)``
form remains a convenience: its ``build()`` returns a RowView whose sequence
contains only detail records, alongside the layout declaration (ADR-064).
"""

from __future__ import annotations

import builtins
import copy
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ._aliases import format_code
from .aggregations import BUILTIN_AGGREGATIONS, resolve_aggregation
from .data import jsonify, normalize_data

__all__ = ["Aggregate", "Rows", "RowView", "aggregate", "count", "group_by", "of"]


@dataclass(frozen=True)
class Aggregate:
    """A portable summary expression, recalculated over matching detail rows."""

    operation: str
    source: str | None = None
    prefix: str = ""
    suffix: str = ""
    format: str | None = None

    def __post_init__(self) -> None:
        operation = self.operation.strip().lower()
        if operation not in BUILTIN_AGGREGATIONS:
            raise ValueError(f"Unknown summary aggregation {operation!r}")
        object.__setattr__(self, "operation", operation)


def aggregate(
    operation: str,
    source: str | None = None,
    *,
    prefix: str = "",
    suffix: str = "",
    format: str | None = None,
    fmt: str | None = None,
) -> Aggregate:
    """Summarize a field; prefix/suffix produce formatted display text."""
    return Aggregate(operation, source, prefix, suffix, format_code(format, fmt))


def count(*, prefix: str = "", suffix: str = "") -> Aggregate:
    """Count matching detail records, e.g. ``rows.count(suffix=' products')``."""
    return Aggregate("count", None, prefix, suffix, "num0")


@dataclass(frozen=True)
class _Annotation:
    label: Any = None
    values: Mapping[str, Any] | None = None
    align: str = "left"
    position: str = "bottom"
    style: Mapping[str, str] | None = None
    rule: str = "none"
    label_column: str | None = None


@dataclass(frozen=True)
class RowView(Sequence[Mapping[str, Any]]):
    """Detail records plus a separate display declaration; never synthetic data."""

    data: tuple[Mapping[str, Any], ...]
    layout: Rows

    def __getitem__(self, index: Any) -> Any:
        return self.data[index]

    def __len__(self) -> int:
        return len(self.data)


class Rows:
    """An immutable row-layout declaration, optionally bound with ``of(data)``."""

    def __init__(
        self,
        detail: Sequence[Mapping[str, Any]] | None = None,
        *,
        dims: Sequence[str] = (),
        section: _Annotation | None = None,
        summary: _Annotation | None = None,
        grand: _Annotation | None = None,
    ) -> None:
        self._detail = None if detail is None else [dict(row) for row in detail]
        self._dims = tuple(dims)
        self._section = section
        self._summary = summary
        self._grand = grand

    @classmethod
    def of(cls, data: Any = None, *, rows: Sequence[Mapping[str, Any]] | None = None) -> Rows:
        detail = [jsonify(dict(row)) for row in rows] if rows is not None else normalize_data(data)[0]
        if any(row.get("render_type") not in (None, "cell_data") for row in detail):
            raise ValueError("rows.of expects detail data; declare synthetic rows through the layout")
        return cls(detail)

    def _replace(self, **changes: Any) -> Rows:
        values = {
            "detail": self._detail,
            "dims": self._dims,
            "section": self._section,
            "summary": self._summary,
            "grand": self._grand,
        }
        values.update(changes)
        return Rows(**values)

    def group_by(self, *dims: str) -> Rows:
        """Group presentation by one or more fields, in first-appearance order."""
        if not dims or any(not isinstance(dim, str) or not dim for dim in dims):
            raise ValueError("group_by needs at least one nonempty column name")
        return self._replace(dims=dims)

    def section(
        self,
        label: Any = None,
        *,
        values: Mapping[str, Any] | None = None,
        align: str = "left",
        style: Mapping[str, str] | None = None,
        rule: str = "none",
        label_column: str | None = None,
    ) -> Rows:
        """Show a group heading, optionally with totals or text in named columns."""
        if align not in ("left", "center"):
            raise ValueError("section align is 'left' or 'center'")
        if align == "center" and values:
            raise ValueError("a centered section cannot have summary values")
        _validate_rule(rule)
        return self._replace(
            section=_Annotation(
                label,
                copy.deepcopy(values),
                align,
                position="section",
                style=copy.deepcopy(style),
                rule=rule,
                label_column=label_column,
            )
        )

    def summary(
        self,
        label: Any = "Subtotal",
        *,
        values: Mapping[str, Any] | None = None,
        position: str = "bottom",
        style: Mapping[str, str] | None = None,
        rule: str = "above",
        label_column: str | None = None,
    ) -> Rows:
        """Show an optional summary once per group; no summary is implicit."""
        if position not in ("top", "bottom"):
            raise ValueError("summary position is 'top' or 'bottom'")
        _validate_rule(rule)
        return self._replace(
            summary=_Annotation(
                label,
                copy.deepcopy(values),
                position=position,
                style=copy.deepcopy(style),
                rule=rule,
                label_column=label_column,
            )
        )

    def grand_summary(
        self,
        label: Any = "Total",
        *,
        values: Mapping[str, Any] | None = None,
        style: Mapping[str, str] | None = None,
        rule: str = "above",
        label_column: str | None = None,
    ) -> Rows:
        """Show one final summary, computed from detail records only."""
        _validate_rule(rule)
        return self._replace(
            grand=_Annotation(
                label, copy.deepcopy(values), style=copy.deepcopy(style), rule=rule, label_column=label_column
            )
        )

    def total(self, label: Any = "Total", **options: Any) -> Rows:
        """Compatibility spelling of ``grand_summary``."""
        return self.grand_summary(label, **options)

    def build(self) -> RowView:
        """Bind detail data and the layout without inserting display records."""
        if self._detail is None:
            raise ValueError("build needs data: use rows.of(data), or pass this layout as row_layout=")
        return RowView(tuple(dict(row) for row in self._detail), self._replace(detail=None))

    def __iter__(self):
        return iter(self.build())

    def compile(self, detail: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """Resolve annotations separately; member indices refer only to detail data."""
        if (self._section or self._summary) and not self._dims:
            raise ValueError("section/summary needs group_by; use grand_summary for an ungrouped table")

        def groups(indices: list[int], level: int, path: tuple[Any, ...]) -> list[dict[str, Any]]:
            if level == len(self._dims):
                return []
            buckets: dict[str, tuple[Any, list[int]]] = {}
            for index in indices:
                value = detail[index].get(self._dims[level])
                key = json.dumps(value, sort_keys=True, default=str)
                buckets.setdefault(key, (value, []))[1].append(index)
            result = []
            for value, members in buckets.values():
                group_path = (*path, value)
                group: dict[str, Any] = {
                    "id": json.dumps(group_path, sort_keys=True, default=str),
                    "members": members,
                    "depth": level,
                    "children": groups(members, level + 1, group_path),
                }
                records = [detail[index] for index in members]
                if self._section:
                    group["section"] = _compile_annotation(
                        self._section, records, str(value) if value is not None else ""
                    )
                if self._summary:
                    group["summary"] = _compile_annotation(self._summary, records, "")
                result.append(group)
            return result

        plan: dict[str, Any] = {"version": 1, "groups": groups(list(builtins.range(len(detail))), 0, ())}
        if self._grand:
            plan["grand_summary"] = _compile_annotation(self._grand, detail, "")
        return plan


def _validate_rule(rule: str) -> None:
    if rule not in ("none", "above", "below", "both"):
        raise ValueError("row rule is 'none', 'above', 'below', or 'both'")


def _compile_annotation(
    annotation: _Annotation, members: Sequence[Mapping[str, Any]], default_label: str
) -> dict[str, Any]:
    label = annotation.label(members) if callable(annotation.label) else annotation.label
    values = annotation.values
    if values is None and annotation.position in ("top", "bottom"):
        values = {
            name: "sum"
            for row in members
            for name, value in row.items()
            if not name.startswith("__") and isinstance(value, (int, float)) and not isinstance(value, bool)
        }
    cells = {}
    for name, spec in (values or {}).items():
        expression = (
            aggregate(spec, name) if isinstance(spec, str) and spec.strip().lower() in BUILTIN_AGGREGATIONS else spec
        )
        if isinstance(expression, Aggregate):
            source = expression.source if expression.source is not None or expression.operation == "count" else name
            observed = [row[source] for row in members if source is not None and row.get(source) is not None]
            value = (
                len(members)
                if source is None and expression.operation == "count"
                else (
                    0
                    if not observed
                    and expression.operation in ("count", "count_distinct", "countdistinct", "distinct_count")
                    else resolve_aggregation(expression.operation)(observed, None)
                    if observed
                    else None
                )
            )
            cells[name] = {
                "value": jsonify(value),
                "operation": expression.operation,
                "source": source,
                "prefix": expression.prefix,
                "suffix": expression.suffix,
                "format": expression.format,
            }
        else:
            cells[name] = {
                "value": jsonify(expression(members) if callable(expression) else expression),
                "scope": "source",
            }
    return {
        "label": str(default_label if label is None else label),
        "cells": cells,
        "align": annotation.align,
        "position": annotation.position,
        "style": dict(annotation.style or {}),
        "rule": annotation.rule,
        "label_column": annotation.label_column,
    }


def group_by(*dims: str) -> Rows:
    """Declare a display layout independently of its data source."""
    return Rows().group_by(*dims)


def of(data: Any = None, *, rows: Sequence[Mapping[str, Any]] | None = None) -> Rows:
    return Rows.of(data, rows=rows)
