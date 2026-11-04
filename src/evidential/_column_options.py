"""Canonicalize Evidence aliases before validating column settings."""

from __future__ import annotations

from collections.abc import Mapping
from difflib import get_close_matches
from typing import Any

from ._aliases import alias
from ._domain import domain_spec
from ._sparkline import normalize_sparkline_colors, normalize_sparkline_options
from .configuration import COLOR_SCALES, ColumnOptions, validate_options

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
    "footnote_column": "footnote",
    "sortBy": "sort_by",
    "sortColumn": "sort_by",
    "highlightColor": "highlight",
    "highlight_color": "highlight",
    "color": "font_color",
}


# Ordered aliases preserve compatibility precedence; canonical nested options win.
_GROUP_ALIASES = {
    "color_options": (
        *((key, key) for key in ("color_scale", "color_stops", "scale_column", "scale_mode", "conditional_colors")),
        ("colorMin", "min"),
        ("colorMax", "max"),
        ("colorMid", "midpoint"),
        ("color_min", "min"),
        ("color_max", "max"),
        ("color_mid", "midpoint"),
    ),
    "sparkline_options": (
        ("sparkX", "x"),
        ("sparkY", "y"),
        ("sparkColor", "color"),
        ("sparkHeight", "height"),
        ("sparkWidth", "width"),
        ("sparkType", "type"),
        ("sparkYScale", "fit_to_data"),
        ("sparkYFmt", "y_fmt"),
        *((f"spark_{key}", key) for key in ("x", "y", "color", "height", "width", "type")),
        ("spark_y_scale", "fit_to_data"),
    ),
    "bar_options": (
        ("barColor", "bar_color"),
        ("negativeBarColor", "bar_color_negative"),
        ("hideLabels", "hide_labels"),
        ("fitToData", "fit_to_data"),
        ("barDirection", "direction"),
        ("referenceLine", "reference"),
        *(
            (key, key)
            for key in (
                "bar_color",
                "bar_color_negative",
                "hide_labels",
                "fit_to_data",
                "direction",
                "reference",
                "reference_color",
                "reference_label",
            )
        ),
    ),
    "delta_options": (
        ("deltaSymbol", "show_symbol"),
        ("downIsGood", "down_is_good"),
        ("showValue", "show_value"),
        ("neutralMin", "neutral_min"),
        ("neutralMax", "neutral_max"),
        ("chip", "chip"),
        *(
            (key, key)
            for key in (
                "down_is_good",
                "show_symbol",
                "show_value",
                "symbol_position",
                "neutral_range",
                "neutral_min",
                "neutral_max",
                "chip",
            )
        ),
    ),
    "chip_options": (("chipMinWidth", "min_width"), ("chipWidth", "min_width"), ("chip_min_width", "min_width")),
    "boolean_options": tuple((key, key) for key in ("true_text", "false_text", "true_symbol", "false_symbol")),
    "image_options": tuple((key, key) for key in ("height", "width", "alt")),
}
_MAPPING_OPTIONS = (*_GROUP_ALIASES, "cell_style", "logo_options", "tooltip_options")


def _content_type(data: dict[str, Any]) -> None:
    kind = str(data.pop("content_type", "") or "").lower()
    if not kind:
        return
    if kind not in {*_CONTENT_TYPES, "html", "link", "image", "logo"}:
        raise ValueError(f"Unknown column content type: {kind!r}")
    viz, spark_type = _CONTENT_TYPES.get(kind, (None, None))
    if viz:
        data.setdefault("viz", viz)
    if spark_type:
        data["sparkline_options"] = {"type": spark_type, **dict(data.get("sparkline_options") or {})}
    if kind == "html":
        data.setdefault("html", True)
    if kind in {"link", "image", "logo"}:
        data.setdefault(kind, str(data["name"]))


def _bind_field(options: dict[str, Any], key: str, target: str | None = None) -> None:
    value = options.get(key)
    if isinstance(value, str) and value.startswith("@"):
        options[target or key] = value[1:]
        if target and target != key:
            del options[key]


def canonicalize_column_options(data: dict[str, Any]) -> dict[str, Any]:
    """Adapt aliases and field bindings once, before inference/configuration merging."""
    for canonical, compatibility in (
        ("fmt", "format"),
        ("fmt_column", "format_column"),
        ("total_fmt", "total_format"),
        ("subtotal_fmt", "subtotal_format"),
    ):
        alias(data, canonical, compatibility)
    for source, target in _COLUMN_ALIASES.items():
        if source in data:
            data.setdefault(target, data.pop(source))
    for key in _MAPPING_OPTIONS:
        if data.get(key) is not None and not isinstance(data[key], Mapping):
            raise TypeError(f"column.{key} expects a mapping")
    _content_type(data)
    for key, aliases in _GROUP_ALIASES.items():
        options = dict(data.get(key) or {})
        for source, target in aliases:
            if source in data:
                options.setdefault(target, data.pop(source))
        if options:
            data[key] = options
    for source, target in (("comment", "info"), ("sort_column", "sort_by")):
        if source in data:
            value = data.pop(source)
            if source == "comment":
                data[target] = value
            else:
                data.setdefault(target, value)
    for key in ("sort_by", "fmt_column", "footnote", "link", "image", "logo"):
        _bind_field(data, key)
    for key in ("color_options", "chip_options"):
        if isinstance(data.get(key), Mapping):
            options = dict(data[key])
            for field in ("conditional_colors", "scale_column"):
                _bind_field(options, field)
            data[key] = options
    if data.get("bar_options"):
        options = data["bar_options"]
        _bind_field(options, "bar_color", "bar_color_column")
        _bind_field(options, "bar_color_negative", "bar_color_negative_column")
    if data.get("cell_style"):
        data["cell_style"] = dict(data["cell_style"])
        _bind_field(data["cell_style"], "background", "background_column")
    return data


def _validate_palette(options: Mapping[str, Any]) -> None:
    scale = options.get("color_scale")
    if isinstance(scale, str) and not scale.startswith("@") and scale.lower() not in COLOR_SCALES:
        suggestion = get_close_matches(scale.lower(), list(COLOR_SCALES), n=1)
        hint = f"; did you mean {suggestion[0]!r}?" if suggestion else ""
        raise ValueError(f"Unknown colour scale {scale!r}{hint}")


def validate_canonical_column(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the complete declaration after all configuration layers are merged."""
    if data.get("tooltip") == "@":
        raise ValueError("tooltip row binding needs a field name")
    if data.get("sparkline_options"):
        data["sparkline_options"] = normalize_sparkline_options(data["sparkline_options"])
    if data.get("viz") == "sparkline" and data.get("color_options"):
        data["color_options"] = normalize_sparkline_colors(data.get("sparkline_options") or {}, data["color_options"])
    for key in ("color_options", "chip_options"):
        if isinstance(data.get(key), Mapping):
            _validate_palette(data[key])
    if data.get("encodings"):
        from .marks import normalize_encoding

        data["encodings"] = [normalize_encoding(encoding) for encoding in data["encodings"]]
    if data.get("legend") is not None:
        from .marks import normalize_legend

        data["legend"] = normalize_legend(data["legend"], data.get("encodings") or [])
    if data.get("domain") is not None:
        data["domain"] = domain_spec(data["domain"])
    validate_options(data, ColumnOptions, "column")
    return data


def _normalize_column_options(data: dict[str, Any]) -> dict[str, Any]:
    """Compatibility entry point for standalone declarations and public mutations."""
    return validate_canonical_column(canonicalize_column_options(data))
