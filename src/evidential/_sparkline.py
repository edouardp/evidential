"""Normalize sparkline settings for both fluent and mapping declarations."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from .configuration import COLOR_SCALES, SparklineOptions, validate_options


def normalize_sparkline_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """Validate change thresholds and palettes without changing caller-owned data."""
    spec = {key: value for key, value in options.items() if value is not None}
    validate_options(spec, SparklineOptions, "column.sparkline_options")
    if "reference_color" in spec and "reference" not in spec:
        raise ValueError("sparkline reference_color requires reference")
    change_only = {"delta", "steady", "color_scale", "color_domain"}
    if spec.get("type", "line") != "change":
        if change_only.intersection(spec):
            raise ValueError("delta, steady, color_scale and color_domain require sparkline type='change'")
        return spec
    if "reference" in spec:
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
    if domain is not None and (domain[0] > steady[0] or domain[1] < steady[1]):
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
    if any(spec.get(name) for name in ("markers", "marker_color", "signed", "fit_to_data")):
        raise ValueError("change sparklines use fixed rectangles; markers, signed and fit_to_data do not apply")
    return spec
