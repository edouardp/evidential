"""gt-style location-based styling, formatting and transforms.

gt's defining idea is that style/format/transform functions all take a
``locations`` argument and target a set of cells. This module brings that to
:class:`~evidence_tables.EvidenceTable`::

    rules=[
        tab_style(cells_body(columns=["Intel"], rows=lambda r: r["Processors"] == 1),
                  background="#fee2e2", font_weight="600"),
        tab_format(cells_body(columns=["Revenues, 2009, $bn"]), "usd1"),
        text_transform(cells_body(columns="Software**"), lambda value: f"{value}*"),
    ]

Rows may be a list of 0-based indices, a predicate on the row dict, or omitted
for "all rows". Style/format rules are sent to the browser; transforms run here
before serialisation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

__all__ = [
    "cells_body",
    "tab_style",
    "tab_format",
    "text_transform",
    "sub_missing",
    "sub_zero",
    "sub_small_vals",
    "sub_large_vals",
    "sub_values",
    "cols_merge",
    "cols_merge_range",
    "cols_merge_uncert",
    "cols_merge_n_pct",
    "resolve_rules",
]


def _columns(value: Any) -> list[str] | str:
    if value is None or value == "*":
        return "*"
    if isinstance(value, str):
        return [value]
    return [str(column) for column in value]


def cells_body(
    columns: str | Sequence[str] = "*",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Target body cells by column name(s) and optional row reference."""
    return {"columns": _columns(columns), "rows": rows}


def tab_style(locations: Mapping[str, Any], **style: Any) -> dict[str, Any]:
    """Apply CSS ``style`` (underscores become hyphens) to ``locations``."""
    css = {key.replace("_", "-"): value for key, value in style.items()}
    return {
        "type": "style",
        "columns": locations["columns"],
        "rows": locations.get("rows"),
        "style": css,
    }


def tab_format(locations: Mapping[str, Any], fmt: str) -> dict[str, Any]:
    """Override the format code for ``locations``."""
    return {
        "type": "format",
        "columns": locations["columns"],
        "rows": locations.get("rows"),
        "fmt": fmt,
    }


def text_transform(locations: Mapping[str, Any], fn: Callable[[Any], Any]) -> dict[str, Any]:
    """Transform the displayed value at ``locations`` with a Python callable."""
    return {
        "type": "transform",
        "columns": locations["columns"],
        "rows": locations.get("rows"),
        "fn": fn,
    }


def sub_missing(
    columns: str | Sequence[str] = "*",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
    missing_text: str = "—",
) -> dict[str, Any]:
    """Replace missing values with ``missing_text``."""
    return _sub(columns, rows, "missing", missing_text)


def sub_zero(
    columns: str | Sequence[str] = "*",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
    zero_text: str = "—",
) -> dict[str, Any]:
    """Replace zero values with ``zero_text``."""
    return _sub(columns, rows, "zero", zero_text)


def sub_small_vals(
    columns: str | Sequence[str] = "*",
    threshold: float = 0.01,
    small_text: str = "small",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Replace values below ``threshold`` with ``small_text``."""
    return _sub(columns, rows, "small", small_text, threshold=threshold)


def sub_large_vals(
    columns: str | Sequence[str] = "*",
    threshold: float = 1_000_000,
    large_text: str = "large",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Replace values above ``threshold`` with ``large_text``."""
    return _sub(columns, rows, "large", large_text, threshold=threshold)


def sub_values(
    columns: str | Sequence[str] = "*",
    values: Sequence[Any] = (),
    replacement: str = "—",
    rows: Sequence[int] | Callable[[Mapping[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Replace any of ``values`` with ``replacement``."""
    return _sub(columns, rows, "values", replacement, values=list(values))


def _sub(
    columns: Any,
    rows: Any,
    kind: str,
    text: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "type": "substitute",
        "columns": _columns(columns),
        "rows": rows,
        "kind": kind,
        "text": text,
        **extra,
    }


def cols_merge(
    template: str,
    *,
    template_fmt: Mapping[str, str] | None = None,
    **options: Any,
) -> dict[str, Any]:
    """Column config that renders ``template`` filled from other columns.

    Example: ``cols_merge("{low}–{high}", template_fmt={"low": "num0", "high": "num0"})``.
    """
    config: dict[str, Any] = {"template": template, **options}
    if template_fmt:
        config["template_fmt"] = dict(template_fmt)
    return config


def cols_merge_range(
    col_begin: str,
    col_end: str,
    *,
    sep: str = "–",
    fmt: str | None = None,
    **options: Any,
) -> dict[str, Any]:
    """Merge a begin/end pair into ``"begin–end"``."""
    template_fmt = {col_begin: fmt, col_end: fmt} if fmt else None
    return cols_merge(f"{{{col_begin}}}{sep}{{{col_end}}}", template_fmt=template_fmt, **options)


def cols_merge_uncert(
    col_val: str,
    col_uncert: str,
    *,
    sep: str = " ± ",
    fmt: str | None = None,
    **options: Any,
) -> dict[str, Any]:
    """Merge a value and its uncertainty into ``"value ± uncert"``."""
    template_fmt = {col_val: fmt, col_uncert: fmt} if fmt else None
    return cols_merge(f"{{{col_val}}}{sep}{{{col_uncert}}}", template_fmt=template_fmt, **options)


def cols_merge_n_pct(
    col_n: str,
    col_pct: str,
    *,
    fmt: str | None = None,
    pct_fmt: str | None = "pct1",
    **options: Any,
) -> dict[str, Any]:
    """Merge a count and percentage into ``"n (pct)"``."""
    template_fmt: dict[str, str] = {}
    if fmt:
        template_fmt[col_n] = fmt
    if pct_fmt:
        template_fmt[col_pct] = pct_fmt
    return cols_merge(f"{{{col_n}}} ({{{col_pct}}})", template_fmt=template_fmt or None, **options)


def _matches_column(rule_columns: Any, name: str) -> bool:
    return rule_columns == "*" or name in rule_columns


def _resolve_rows(rows: Sequence[Mapping[str, Any]], reference: Any) -> list[int] | None:
    if reference is None:
        return None
    if callable(reference):
        return [index for index, row in enumerate(rows) if reference(row)]
    return [int(index) for index in reference]


def resolve_rules(
    rows: Sequence[Mapping[str, Any]],
    rules: Iterable[Mapping[str, Any]] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return ``(transformed_rows, client_rules)`` for the renderer.

    Rows get a stable ``__row_id`` so rules survive sorting/paging. Transform
    rules are applied here; style/format rules are returned for the browser.
    """
    if not rules:
        return [dict(row) for row in rows], []
    working = [dict(row) for row in rows]
    for index, row in enumerate(working):
        row["__row_id"] = index

    client_rules: list[dict[str, Any]] = []
    for rule in rules:
        rule_type = rule.get("type")
        columns = rule.get("columns", "*")
        row_ids = _resolve_rows(working, rule.get("rows"))
        matching = row_ids if row_ids is not None else range(len(working))
        if rule_type == "transform":
            fn = rule["fn"]
            for index in matching:
                row = working[index]
                for name in list(row.keys()):
                    if name.startswith("__"):
                        continue
                    if _matches_column(columns, name):
                        row[name] = fn(row[name])
        elif rule_type == "format":
            client_rules.append({"columns": columns, "rows": row_ids, "fmt": rule["fmt"]})
        elif rule_type == "style":
            client_rules.append({"columns": columns, "rows": row_ids, "style": rule["style"]})
        elif rule_type == "substitute":
            client = {"type": "substitute", "columns": columns, "rows": row_ids}
            for key in ("kind", "text", "threshold", "values"):
                if key in rule:
                    client[key] = rule[key]
            client_rules.append(client)
    return working, client_rules
