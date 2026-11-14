"""Normalize sparkline settings for both fluent and mapping declarations."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from ._color import normalize_value_colors
from .configuration import COLOR_SCALES, SparklineOptions, validate_options


def normalize_sparkline_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """Validate change thresholds and palettes without changing caller-owned data."""
    spec = {key: value for key, value in options.items() if value is not None}
    validate_options(spec, SparklineOptions, "column.sparkline_options")
    if "reference_color" in spec and "reference" not in spec:
        raise ValueError("sparkline reference_color requires reference")
    change = spec.get("type", "line") == "change"
    if "fill_opacity" in spec:
        if spec.get("type", "line") != "area":
            raise ValueError("sparkline fill_opacity requires type='area'")
        opacity = spec["fill_opacity"]
        values = (opacity,) if isinstance(opacity, (int, float)) else opacity
        if any(isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError("sparkline fill_opacity must contain finite opacities between 0 and 1")
        spec["fill_opacity"] = opacity if isinstance(opacity, (int, float)) else tuple(opacity)
    if not change and {"delta", "steady"}.intersection(spec):
        raise ValueError("delta and steady require sparkline type='change'")
    if change and "reference" in spec:
        raise ValueError("sparkline reference does not apply to type='change'")
    for name in ("steady", "color_domain"):
        if name not in spec:
            continue
        lo, hi = spec[name]
        if not all(math.isfinite(value) for value in (lo, hi)) or lo > hi or (name == "color_domain" and lo == hi):
            raise ValueError(
                f"sparkline {name} must be a finite, ordered pair"
                + (" with distinct endpoints" if name == "color_domain" else "")
            )
        spec[name] = (lo, hi)
    steady = spec.get("steady", (0, 0))
    domain = spec.get("color_domain")
    if change and domain is not None and (domain[0] > steady[0] or domain[1] < steady[1]):
        raise ValueError("sparkline color_domain must contain the steady range")
    palette = spec.get("color_scale")
    if palette is not None:
        if "color" in spec:
            raise ValueError("sparkline color and color_scale are mutually exclusive")
        if isinstance(palette, str):
            if palette.lower() not in COLOR_SCALES:
                raise ValueError(f"Unknown colour scale {palette!r}")
        elif len(palette) < 2 or any(not color.strip() for color in palette):
            raise ValueError("sparkline color_scale needs at least two nonempty colors")
        else:
            spec["color_scale"] = list(palette)
    elif domain is not None:
        raise ValueError("sparkline color_domain requires color_scale")
    for name in ("width", "height"):
        if name in spec and (not math.isfinite(spec[name]) or spec[name] <= 0):
            raise ValueError(f"sparkline {name} must be finite and positive")
    if change and any(spec.get(name) for name in ("markers", "marker_color", "signed", "fit_to_data")):
        raise ValueError("change sparklines use fixed rectangles; markers, signed and fit_to_data do not apply")
    return spec


def normalize_sparkline_colors(options: Mapping[str, Any], colors: Mapping[str, Any]) -> dict[str, Any]:
    """Reuse the cell gradient declaration for observation y values, without row bindings."""
    spec = normalize_value_colors(colors, "sparkline color")
    palette = spec.get("color_scale")
    legacy = options.get("color_scale")
    if legacy is not None and palette is not None:
        if (legacy.lower() if isinstance(legacy, str) else list(legacy)) != (
            palette.lower() if isinstance(palette, str) else list(palette)
        ):
            raise ValueError("Conflicting sparkline color scales; configure the gradient with .color()")
    domain = options.get("color_domain")
    if domain is not None and any(
        key in spec and spec[key] != bound for key, bound in zip(("min", "max"), domain, strict=True)
    ):
        raise ValueError("Conflicting sparkline color bounds; configure the gradient with .color()")
    if spec and options.get("color") is not None:
        raise ValueError("sparkline color and gradient options are mutually exclusive")
    if options.get("type") == "change":
        lo, hi = options.get("steady", (0, 0))
        if spec.get("min", lo) > lo or spec.get("max", hi) < hi:
            raise ValueError("sparkline color bounds must contain the steady range")
        if "midpoint" in spec and spec["midpoint"] != (lo + hi) / 2:
            raise ValueError("change sparkline color midpoint must match the steady interval's center")
    return spec
