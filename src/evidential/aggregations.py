"""Built-in and custom aggregations for subtotal/total rows.

Evidence's ``totalAgg`` recomputes a measure's subtotal/total from its detail
values (e.g. the mean of daily sums), rather than re-aggregating the raw column.
Here that is expressed as a Python callable, so built-ins and user functions
share one path.

Pass specs to :func:`grouped_table`/:func:`pivot_table` via ``aggregations``::

    grouped_table(con, sql, ["country"], ["sum(revenue) AS revenue"],
                  aggregations={"revenue": "mean"})
    grouped_table(..., aggregations={"revenue": statistics.median})
    grouped_table(..., aggregations={"revenue": "weighted_mean"},
                  weight_columns={"revenue": "weight"})
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

__all__ = [
    "Aggregation",
    "BUILTIN_AGGREGATIONS",
    "resolve_aggregation",
    "apply_aggregations",
    "sum_values",
    "mean_values",
    "median_values",
    "min_values",
    "max_values",
    "count_values",
    "count_distinct_values",
    "weighted_mean_values",
]

#: A callable takes ``(values, weights)`` (weights may be ``None``) and returns
#: the aggregate. ``weights`` is only supplied for weighted_mean.
Aggregation = Callable[[Sequence[Any], Sequence[float] | None], Any]


def _summary_key(value: Any) -> Any:
    """JSON value identity: booleans differ from numbers; object order does not matter."""
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    if isinstance(value, Mapping):
        return ("object", tuple(sorted((str(key), _summary_key(item)) for key, item in value.items())))
    if isinstance(value, (list, tuple)):
        return ("array", tuple(_summary_key(item) for item in value))
    return (type(value).__name__, value)


def summary_values(operation: str, values: Sequence[Any]) -> Any:
    """Portable display aggregation; frontend/aggregates.js shares its fixture contract."""
    observed = [value for value in values if value is not None]
    if operation == "count":
        return len(observed)
    if operation in ("count_distinct", "countdistinct", "distinct_count"):
        return len({_summary_key(value) for value in observed})
    if not observed:
        return None
    if operation in ("min", "max") and all(isinstance(value, str) for value in observed):
        return min(observed) if operation == "min" else max(observed)
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in observed):
        raise TypeError(f"summary {operation} requires numeric values (min/max also accept strings and ISO dates)")
    return resolve_aggregation(operation)(observed, None)


def sum_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> Any:
    return sum(values)


def mean_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> float:
    return statistics.fmean(values)


def median_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> Any:
    return statistics.median(values)


def min_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> Any:
    return min(values)


def max_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> Any:
    return max(values)


def count_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> int:
    return len(values)


def count_distinct_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> int:
    return len(set(values))


def weighted_mean_values(values: Sequence[Any], weights: Sequence[float] | None = None) -> float:
    if weights is None:
        return statistics.fmean(values)
    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    total = sum(weights)
    if total == 0:
        return 0.0
    return sum(value * weight for value, weight in zip(values, weights, strict=True)) / total


BUILTIN_AGGREGATIONS: dict[str, Aggregation] = {
    "sum": sum_values,
    "mean": mean_values,
    "avg": mean_values,
    "average": mean_values,
    "median": median_values,
    "min": min_values,
    "max": max_values,
    "count": count_values,
    "count_distinct": count_distinct_values,
    "countdistinct": count_distinct_values,
    "distinct_count": count_distinct_values,
    "weighted_mean": weighted_mean_values,
    "weightedmean": weighted_mean_values,
}


def resolve_aggregation(spec: Any) -> Aggregation:
    """Resolve a spec (built-in name or callable) to an aggregation callable.

    Custom callables receive the list of detail values only; built-ins may also
    use the aggregated weights for ``weighted_mean``.
    """
    if callable(spec):
        return lambda values, weights=None: spec(values)
    if isinstance(spec, str):
        key = spec.strip().lower()
        if key in BUILTIN_AGGREGATIONS:
            return BUILTIN_AGGREGATIONS[key]
        raise ValueError(f"Unknown aggregation {spec!r}; built-ins: {', '.join(sorted(BUILTIN_AGGREGATIONS))}")
    raise TypeError(f"aggregation must be a built-in name or callable, got {spec!r}")


def _expand(aggregations: Any, measure_aliases: Iterable[str]) -> dict[str, Aggregation]:
    aliases = list(measure_aliases)
    if callable(aggregations):
        resolved = resolve_aggregation(aggregations)
        return dict.fromkeys(aliases, resolved)
    if isinstance(aggregations, Mapping):
        return {str(alias): resolve_aggregation(spec) for alias, spec in aggregations.items()}
    raise TypeError("aggregations must be a callable or a mapping of measure -> aggregation")


def apply_aggregations(
    rows: list[dict[str, Any]],
    aggregations: Any,
    measure_aliases: Iterable[str],
    weight_columns: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Recompute subtotal/total cells from the detail rows.

    ``rows`` must be the decorated, display-ordered rows produced by
    :func:`~evidential.grouped.decorate_grouped_rows` (detail rows have
    ``render_type == "cell_data"`` and ``__ancestors``).
    """
    resolved = _expand(aggregations, measure_aliases)
    if not resolved:
        return rows

    detail_rows = [row for row in rows if row.get("render_type") == "cell_data"]
    by_group: dict[str, list[dict[str, Any]]] = {}
    for detail in detail_rows:
        for ancestor in detail.get("__ancestors") or []:
            by_group.setdefault(ancestor, []).append(detail)
    for alias, aggregate in resolved.items():
        weight_column = (weight_columns or {}).get(alias)
        for row in rows:
            if row.get("render_type") == "cell_data":
                continue
            key = row.get("__group_key")
            if row.get("render_type") == "row_total" or key == "__total__":
                descendants = detail_rows
            else:
                descendants = by_group.get(key, []) if key is not None else []
            members = [candidate for candidate in descendants if candidate.get(alias) is not None]
            # A missing value or weight excludes the whole pair; filtering the
            # lists independently can silently assign a weight to another row.
            if weight_column and aggregate is weighted_mean_values:
                members = [candidate for candidate in members if candidate.get(weight_column) is not None]
            values = [candidate[alias] for candidate in members]
            if not values:
                row[alias] = None
                continue
            weights = None
            if weight_column and aggregate is weighted_mean_values:
                weights = [candidate[weight_column] for candidate in members]
            row[alias] = aggregate(values, weights)
    return rows
