"""Shared numeric gradient validation for sparklines and interval marks."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from .configuration import COLOR_SCALES, ColorOptions, validate_options


def normalize_value_colors(colors: Mapping[str, Any], subject: str) -> dict[str, Any]:
    """Copy and validate palettes, numeric bounds and explicit value stops."""
    if not isinstance(colors, Mapping):
        raise TypeError(f"{subject} expects a color-options mapping")
    spec = {key: value for key, value in colors.items() if value is not None}
    validate_options(spec, ColorOptions, subject)
    if any(spec.get(key) is not None for key in ("conditional_colors", "scale_column")):
        raise ValueError(f"{subject} uses numeric values, not row color bindings")
    for name in ("min", "max", "midpoint"):
        if name in spec and not math.isfinite(spec[name]):
            raise ValueError(f"{subject} {name} must be finite")
    if "min" in spec and "max" in spec and spec["min"] >= spec["max"]:
        raise ValueError(f"{subject} min must be less than max")
    palette = spec.get("color_scale")
    if isinstance(palette, str):
        if palette.lower() not in COLOR_SCALES:
            raise ValueError(f"Unknown colour scale {palette!r}")
    elif palette is not None:
        if len(palette) < 2 or any(not color.strip() for color in palette):
            raise ValueError(f"{subject} scale needs at least two nonempty colors")
        spec["color_scale"] = list(palette)
    if "color_stops" in spec:
        stops = [dict(stop) for stop in spec["color_stops"]]
        if len(stops) < 2 or any(not math.isfinite(stop["value"]) or not stop["color"].strip() for stop in stops):
            raise ValueError(f"{subject} stops need at least two finite values and nonempty colors")
        if len({stop["value"] for stop in stops}) != len(stops):
            raise ValueError(f"{subject} stops must have distinct values")
        spec["color_stops"] = stops
    return spec
