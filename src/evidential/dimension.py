"""Linked, searchable dimension facets without exposing source rows to the browser."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any, Literal, TypedDict

import anywidget
import traitlets

from .data import infer_columns, normalize_data

Aggregate = Literal["sum", "count", "mean", "min", "max"]
Scalar = str | int | float | bool | None


class _FacetItem(TypedDict):
    value: Scalar
    metric: float | None


def _key(value: Scalar) -> tuple[type, Scalar]:
    # JSON numbers have one identity, while booleans remain distinct.
    kind = float if isinstance(value, (int, float)) and not isinstance(value, bool) else type(value)
    return kind, value


@dataclass
class _Category:
    value: Scalar
    count: int = 0
    total: float = 0
    minimum: float | None = None
    maximum: float | None = None

    def add(self, metric: Any, aggregate: Aggregate) -> None:
        if metric is None:
            return
        self.count += 1
        if aggregate == "count":
            return
        self.total += metric
        self.minimum = metric if self.minimum is None else min(self.minimum, metric)
        self.maximum = metric if self.maximum is None else max(self.maximum, metric)

    def result(self, aggregate: Aggregate) -> float | None:
        if aggregate == "count":
            return self.count
        if aggregate == "mean":
            return self.total / self.count if self.count else None
        if aggregate == "min":
            return self.minimum
        if aggregate == "max":
            return self.maximum
        return self.total


class DimensionGrid(anywidget.AnyWidget):
    """Horizontal category slicers with cross-filtered aggregate bars.

    Search and scrolling are local to each dimension. Selection is OR within
    a dimension and AND across dimensions. Each facet excludes its own filter
    so alternative categories remain available. Only aggregate categories and
    selections cross the widget boundary; source records stay in Python.
    """

    _esm = Path(__file__).parent / "static" / "dimension-grid.js"
    _css = Path(__file__).parent / "static" / "dimension-grid.css"

    selected = traitlets.Dict(default_value={}).tag(sync=True)
    facets = traitlets.List(default_value=[]).tag(sync=True)
    options = traitlets.Dict(default_value={}).tag(sync=True)

    def __init__(
        self,
        data: Any = None,
        *,
        dimensions: Sequence[str] | Mapping[str, str] | None = None,
        metric: str | None = None,
        aggregate: Aggregate | None = None,
        format: str = "compact",
        multiple: bool = True,
        height: int = 280,
        dimension_width: int = 220,
        color: str = "#93b4ef",
        title: str | None = None,
        subtitle: str | None = None,
        selected: Mapping[str, Sequence[Scalar]] | None = None,
    ) -> None:
        records, inferred = normalize_data(data)
        schema = inferred or infer_columns(data, records)
        names = {column["name"] for column in schema}
        if dimensions is None:
            dimensions = [column["name"] for column in schema if column.get("type") == "string"]
        if isinstance(dimensions, str):
            raise TypeError("dimensions must be a sequence of field names or a field-to-label mapping")
        self._dimensions = dict(dimensions) if isinstance(dimensions, Mapping) else dict.fromkeys(dimensions)
        if not self._dimensions:
            raise ValueError("Provide at least one dimension (string columns are inferred by default)")
        if names and (unknown := set(self._dimensions) - names):
            raise ValueError(f"Unknown dimensions: {sorted(unknown)}")
        self._metric = metric
        self._aggregate: Aggregate = aggregate if aggregate is not None else ("sum" if metric is not None else "count")
        if self._aggregate not in ("sum", "count", "mean", "min", "max"):
            raise ValueError("aggregate must be sum, count, mean, min or max")
        if self._aggregate != "count" and metric is None:
            raise ValueError("A metric field is required for this aggregate")
        if metric is not None and names and metric not in names:
            raise ValueError(f"Unknown metric: {metric}")
        if not isinstance(multiple, bool):
            raise TypeError("multiple must be a boolean")
        for name, value in (("height", height), ("dimension_width", dimension_width)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 100:
                raise ValueError(f"{name} must be an integer of at least 100 pixels")
        self._multiple = multiple
        self._records = self._validate_records(records)
        self._domains = self._get_domains(self._records)
        super().__init__(
            options={
                "format": format,
                "multiple": multiple,
                "height": height,
                "dimension_width": dimension_width,
                "color": color,
                "title": title,
                "subtitle": subtitle,
                "metric": metric,
                "aggregate": self._aggregate,
            },
            selected=dict(selected or {}),
        )
        self._refresh()

    def _validate_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for row in records:
            for name in self._dimensions:
                value = row.get(name)
                if value is not None and not isinstance(value, (str, int, float, bool)):
                    raise TypeError(f"Dimension {name!r} must contain scalar values")
            if self._metric is not None and self._aggregate != "count":
                value = row.get(self._metric)
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                    raise TypeError(f"Metric {self._metric!r} must contain numeric values or nulls")
        return deepcopy(records)

    def _get_domains(self, records: list[dict[str, Any]]) -> dict[str, set[tuple[type, Scalar]]]:
        return {name: {_key(row.get(name)) for row in records} for name in self._dimensions}

    @traitlets.validate("selected")
    def _validate_selected(self, proposal: dict[str, Any]) -> dict[str, list[Scalar]]:
        result = {}
        for name, values in proposal["value"].items():
            if name not in self._dimensions:
                raise traitlets.TraitError(f"Unknown dimension: {name}")
            if not isinstance(values, (list, tuple)):
                raise traitlets.TraitError("Each selection must be a list of category values")
            unique: dict[tuple[type, Scalar], Scalar] = {}
            for value in values:
                if not isinstance(value, (str, int, float, bool, type(None))) or _key(value) not in self._domains[name]:
                    raise traitlets.TraitError(f"Unknown category for {name!r}: {value!r}")
                unique[_key(value)] = value
            if not self._multiple and len(unique) > 1:
                raise traitlets.TraitError("Enable multiple=True to select multiple values within a dimension")
            if unique:
                result[name] = list(unique.values())
        return result

    @traitlets.observe("selected")
    def _selection_changed(self, change: dict[str, Any]) -> None:
        self._refresh()

    def _refresh(self) -> None:
        selections = {name: {_key(value) for value in values} for name, values in self.selected.items()}
        groups: dict[str, dict[tuple[type, Scalar], _Category]] = {name: {} for name in self._dimensions}
        for row in self._records:
            failures = [name for name, values in selections.items() if _key(row.get(name)) not in values]
            if len(failures) > 1:
                continue
            for name in self._dimensions:
                if failures and failures[0] != name:
                    continue
                value = row.get(name)
                key = _key(value)
                entry = groups[name].get(key)
                if entry is None:
                    entry = groups[name][key] = _Category(value)
                metric = row.get(self._metric) if self._metric is not None else 1
                entry.add(metric, self._aggregate)
        facets = []
        for name, label in self._dimensions.items():
            items: list[_FacetItem] = []
            for category in groups[name].values():
                aggregate = category.result(self._aggregate)
                items.append(
                    {"value": category.value, "metric": aggregate if aggregate is None or isfinite(aggregate) else None}
                )
            items.sort(key=lambda item: (item["metric"] is None, -(item["metric"] or 0), str(item["value"])))
            # Retain incompatible selections so they can always be removed.
            available = {_key(item["value"]) for item in items}
            items.extend(
                {"value": value, "metric": None}
                for value in self.selected.get(name, [])
                if _key(value) not in available
            )
            facets.append({"name": name, "title": label, "items": items})
        self.facets = facets

    @property
    def raw(self) -> list[dict[str, Any]]:
        """A detached snapshot of all unformatted source records."""
        return deepcopy(self._records)

    @property
    def filtered(self) -> list[dict[str, Any]]:
        """A detached snapshot matching the current selections."""
        selections = {name: {_key(value) for value in values} for name, values in self.selected.items()}
        return deepcopy(
            [row for row in self._records if all(_key(row.get(name)) in values for name, values in selections.items())]
        )

    def where(self) -> tuple[str, list[Scalar]]:
        """Return a SQL predicate and bound parameters for the current selections.

        Field identifiers are quoted; values are never interpolated. Apply the
        predicate to a relation with the same dimension field names.
        """
        clauses = []
        parameters: list[Scalar] = []
        for name, values in self.selected.items():
            field = '"' + name.replace('"', '""') + '"'
            nonnull = [value for value in values if value is not None]
            parts = []
            if nonnull:
                parts.append(f"{field} IN ({', '.join('?' for _ in nonnull)})")
                parameters.extend(nonnull)
            if None in values:
                parts.append(f"{field} IS NULL")
            clauses.append("(" + " OR ".join(parts) + ")")
        return " AND ".join(clauses) or "TRUE", parameters

    def set_data(self, data: Any) -> None:
        """Replace source records, retaining selections still in the new domains."""
        records, _ = normalize_data(data)
        records = self._validate_records(records)
        domains = self._get_domains(records)
        selected = {
            name: [value for value in values if _key(value) in domains[name]] for name, values in self.selected.items()
        }
        self._records, self._domains = records, domains
        self.selected = selected
        self._refresh()

    def clear(self) -> None:
        """Clear all selections; local search text is independent of selection."""
        self.selected = {}
