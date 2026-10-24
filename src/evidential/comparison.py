"""Prior-period comparison helper.

:func:`comparison_table` computes each measure for the current period and the
matching prior period (anchored on the latest date in the data) and adds
absolute and percentage change columns.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .data import make_column
from .grouped import _parse_measure
from .marks import rebind_measure
from .table import EvidentialTable

__all__ = ["comparison_table"]

_COMPARE_TO_PERIOD = {
    "prior year": "year",
    "prior quarter": "quarter",
    "prior month": "month",
    "prior week": "week",
    "prior day": "day",
    "year over year": "year",
    "quarter over quarter": "quarter",
    "month over month": "month",
    "week over week": "week",
}
_PERIODS = {"year", "quarter", "month", "week", "day"}


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def comparison_table(
    connection: Any,
    sql: str,
    dimensions: Sequence[str],
    measures: Sequence[Any],
    *,
    date_column: str,
    compare_vs: str = "prior year",
    periods: int = 1,
    dimension_config: Mapping[str, Mapping[str, Any]] | None = None,
    measure_config: Mapping[str, Mapping[str, Any]] | None = None,
    **table_options: Any,
) -> EvidentialTable:
    """Compare each measure against the previous ``periods`` periods.

    The window is anchored on the latest ``date_column`` value in ``sql``:
    the current period is the most recent ``periods`` units and the prior
    period is the ``periods`` units before that. Adds ``<measure>_prior``,
    ``<measure>_delta`` and ``<measure>_pct`` columns.
    """
    period = _COMPARE_TO_PERIOD.get(str(compare_vs).lower(), str(compare_vs).lower())
    if period not in _PERIODS:
        raise ValueError(f"compare_vs must be one of {sorted(_PERIODS)} or a prior-* alias")
    if periods < 1:
        raise ValueError("periods must be >= 1")
    if not dimensions:
        raise ValueError("comparison_table requires at least one dimension")
    if not measures:
        raise ValueError("comparison_table requires at least one measure")

    dims = list(dimensions)
    parsed = [_parse_measure(measure) for measure in measures]
    measure_exprs = ", ".join(f"{expression} AS {_quote(alias)}" for alias, expression in parsed)

    current_offset = periods - 1
    prior_offset = 2 * periods - 1

    select_parts = [f"c.{_quote(dim)}" for dim in dims]
    for alias, _ in parsed:
        quoted = _quote(alias)
        select_parts.extend(
            [
                f"c.{quoted} AS {quoted}",
                f"p.{quoted} AS {_quote(alias + '_prior')}",
                f"coalesce(c.{quoted}, 0) - coalesce(p.{quoted}, 0) AS {_quote(alias + '_delta')}",
                f"(c.{quoted} - p.{quoted}) / nullif(p.{quoted}, 0) AS {_quote(alias + '_pct')}",
            ]
        )

    join = " AND ".join(f"c.{_quote(dim)} IS NOT DISTINCT FROM p.{_quote(dim)}" for dim in dims)
    order_alias = _quote(parsed[0][0])

    query = f"""
        WITH __base AS (
            {sql}
        ),
        __bounds AS (
            SELECT date_trunc('{period}', max({date_column})) AS anchor FROM __base
        ),
        __current AS (
            SELECT {", ".join(dims)}, {measure_exprs}
            FROM __base, __bounds
            WHERE {date_column} >= anchor - INTERVAL '{current_offset} {period}'
              AND {date_column} < anchor + INTERVAL '1 {period}'
            GROUP BY {", ".join(dims)}
        ),
        __prior AS (
            SELECT {", ".join(dims)}, {measure_exprs}
            FROM __base, __bounds
            WHERE {date_column} >= anchor - INTERVAL '{prior_offset} {period}'
              AND {date_column} < anchor - INTERVAL '{current_offset} {period}'
            GROUP BY {", ".join(dims)}
        )
        SELECT {", ".join(select_parts)}
        FROM __current AS c
        LEFT JOIN __prior AS p ON {join}
        ORDER BY c.{order_alias} DESC NULLS LAST
    """
    rows = connection.sql(query).to_arrow_table().to_pylist()

    columns: list[dict[str, Any]] = []
    for dim in dims:
        overrides = dict((dimension_config or {}).get(dim, {}))
        overrides.pop("name", None)  # a col.* builder carries its name; the key is the name
        overrides.setdefault("type", "string")
        overrides.setdefault("align", "left")
        columns.append(make_column(dim, **overrides))

    for alias, _ in parsed:
        base = dict((measure_config or {}).get(alias, {}))
        base.pop("name", None)
        # Delta options on a measure (e.g. `col.currency("sales").delta(...)`)
        # describe the derived change columns, not the measure itself.
        delta_options = dict(base.pop("delta_options", None) or {})
        for key in (
            "down_is_good",
            "neutral_range",
            "neutral_min",
            "neutral_max",
            "show_symbol",
            "show_value",
            "symbol_position",
            "chip",
        ):
            if key in base:
                delta_options.setdefault(key, base.pop(key))
        if base.get("viz") == "delta":
            base.pop("viz", None)
        base.setdefault("type", "number")
        base.setdefault("align", "right")
        columns.append(make_column(alias, **base))

        prior = rebind_measure(base, alias, alias + "_prior")
        columns.append(make_column(alias + "_prior", **{**prior, "title": "Prior"}))

        delta = {**base, "title": "Change"}
        delta.pop("viz", None)
        delta.pop("bar_options", None)
        delta.pop("color_options", None)
        for key in ("encodings", "scale", "references"):
            delta.pop(key, None)
        if delta_options:
            delta["delta_options"] = dict(delta_options)
        columns.append(make_column(alias + "_delta", **delta))

        pct = {**base, "title": "% change", "fmt": "pct1", "viz": "delta"}
        pct.pop("bar_options", None)
        pct.pop("color_options", None)
        for key in ("encodings", "scale", "references"):
            pct.pop(key, None)
        if delta_options:
            pct["delta_options"] = dict(delta_options)
        columns.append(make_column(alias + "_pct", **pct))

    return EvidentialTable(rows=rows, columns=columns, **table_options)
