"""Canonicalize Evidence aliases before validating column settings."""

from __future__ import annotations

from collections.abc import Mapping
from difflib import get_close_matches
from typing import Any

from ._aliases import alias
from ._domain import domain_spec
from ._sparkline import normalize_sparkline_options
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


def _normalize_column_options(data: dict[str, Any]) -> dict[str, Any]:
    """Merge Evidence-style top-level column options into nested option dicts.

    Allows ergonomic, Evidence-compatible configs such as
    ``{"color_scale": "green", "sparkY": "sales"}`` to populate
    ``color_options`` / ``sparkline_options`` / ``bar_options`` / etc.
    """
    for canonical, compatibility in (
        ("fmt", "format"),
        ("fmt_column", "format_column"),
        ("total_fmt", "total_format"),
        ("subtotal_fmt", "subtotal_format"),
    ):
        alias(data, canonical, compatibility)
    for alias_name, canonical in _COLUMN_ALIASES.items():
        if alias_name in data:
            data.setdefault(canonical, data.pop(alias_name))
    for key in (
        "color_options",
        "bar_options",
        "delta_options",
        "sparkline_options",
        "chip_options",
        "boolean_options",
        "cell_style",
        "image_options",
        "logo_options",
    ):
        if data.get(key) is not None and not isinstance(data[key], Mapping):
            raise TypeError(f"column.{key} expects a mapping")
    content_type = str(data.pop("content_type", "") or "").lower()
    if content_type:
        viz, spark_type = _CONTENT_TYPES.get(content_type, (None, None))
        if content_type not in {*_CONTENT_TYPES, "html", "link", "image", "logo"}:
            raise ValueError(f"Unknown column content type: {content_type!r}")
        if viz:
            data.setdefault("viz", viz)
        if spark_type:
            spark_options = dict(data.get("sparkline_options") or {})
            spark_options.setdefault("type", spark_type)
            data["sparkline_options"] = spark_options
        if content_type == "html":
            data.setdefault("html", True)
        if content_type in {"link", "image", "logo"}:
            data.setdefault(content_type, str(data["name"]))

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
        data["sparkline_options"] = normalize_sparkline_options(spark)

    bar = dict(data.get("bar_options") or {})
    for camel, snake in (
        ("barColor", "bar_color"),
        ("negativeBarColor", "bar_color_negative"),
        ("hideLabels", "hide_labels"),
        ("fitToData", "fit_to_data"),
        ("barDirection", "direction"),
        ("referenceLine", "reference"),
    ):
        if camel in data:
            bar.setdefault(snake, data.pop(camel))
    # Allow the bar options at the top level too (snake_case), like the colour
    # and delta options, so `bar_color="#..."` is not silently ignored.
    for key in (
        "bar_color",
        "bar_color_negative",
        "hide_labels",
        "fit_to_data",
        "direction",
        "reference",
        "reference_color",
        "reference_label",
    ):
        if key in data:
            bar.setdefault(key, data.pop(key))
    # The `@column` reference convention: `bar_color="@name"` colours each bar
    # from that column, so remember the column rather than a literal colour.
    bar_color = bar.get("bar_color")
    if isinstance(bar_color, str) and bar_color.startswith("@"):
        bar["bar_color_column"] = bar_color[1:]
        del bar["bar_color"]
    negative_color = bar.get("bar_color_negative")
    if isinstance(negative_color, str) and negative_color.startswith("@"):
        bar["bar_color_negative_column"] = negative_color[1:]
        bar.pop("bar_color_negative")
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

    chip = dict(data.get("chip_options") or {})
    for camel, snake in (
        ("chipMinWidth", "min_width"),
        ("chipWidth", "min_width"),
    ):
        if camel in data:
            chip.setdefault(snake, data.pop(camel))
    # Allow the chip option at the top level too.
    if "chip_min_width" in data:
        chip.setdefault("min_width", data.pop("chip_min_width"))
    if chip:
        data["chip_options"] = chip

    boolean = dict(data.get("boolean_options") or {})
    for key in ("true_text", "false_text", "true_symbol", "false_symbol"):
        if key in data:
            boolean.setdefault(key, data.pop(key))
    if boolean:
        data["boolean_options"] = boolean

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
    # The `@column` reference convention: `"@name"` names the column `name`.
    for key in ("sort_by", "fmt_column", "footnote", "link", "image", "logo"):
        value = data.get(key)
        if isinstance(value, str) and value.startswith("@"):
            data[key] = value[1:]
    for key in ("color_options", "chip_options"):
        options = data.get(key)
        if isinstance(options, Mapping):
            options = dict(options)
            for field in ("conditional_colors", "scale_column"):
                value = options.get(field)
                if isinstance(value, str) and value.startswith("@"):
                    options[field] = value[1:]
            # Validate a named colour scale (a list of colours is left to chroma).
            scale = options.get("color_scale")
            if isinstance(scale, str) and not scale.startswith("@") and scale.lower() not in COLOR_SCALES:
                suggestion = get_close_matches(scale.lower(), list(COLOR_SCALES), n=1)
                hint = f"; did you mean {suggestion[0]!r}?" if suggestion else ""
                raise ValueError(f"Unknown colour scale {scale!r}{hint}")
            data[key] = options

    cell_style = dict(data.get("cell_style") or {})
    background = cell_style.get("background")
    if isinstance(background, str) and background.startswith("@"):
        cell_style["background_column"] = background[1:]
        cell_style.pop("background", None)
    if cell_style:
        data["cell_style"] = cell_style
    if data.get("encodings"):
        from .marks import normalize_encoding

        data["encodings"] = [normalize_encoding(encoding) for encoding in data["encodings"]]
    if data.get("domain") is not None:
        data["domain"] = domain_spec(data["domain"])
    validate_options(data, ColumnOptions, "column")
    return data
