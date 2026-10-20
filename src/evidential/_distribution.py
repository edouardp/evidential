"""Contract and validation for precomputed uncertainty bands (ADR-065)."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


def band_spec(*, x: str, y: str, height: float, density_max: float | None) -> dict[str, Any]:
    """Keep density bindings, physical height and intensity scale independent."""
    if not isinstance(x, str) or not x or not isinstance(y, str) or not y:
        raise ValueError("distribution x and y must be nonempty field names")
    if not _number(height) or not 0 < height <= 1:
        raise ValueError("distribution height must be a finite fraction in (0, 1]")
    if density_max is not None and (not _number(density_max) or density_max <= 0):
        raise ValueError("distribution density_max must be finite and positive, or None for the row peak")
    return {"x": x, "y": y, "height": height, "density_max": density_max}


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_curve(value: Any, spec: Mapping[str, Any], *, source: str, log: bool) -> None:
    """Validate ordered density records, with nulls representing unknown support."""
    if value is None:
        return
    if not isinstance(value, list):
        raise ValueError(f"distribution {source!r} requires a precomputed list of position/density records")
    previous = -math.inf
    for sample in value:
        if sample is None:
            continue
        if not isinstance(sample, Mapping):
            raise ValueError(f"distribution {source!r} requires precomputed density records, not raw samples")
        x, y = spec["x"], spec["y"]
        if x not in sample or y not in sample:
            raise ValueError(f"distribution {source!r} records need fields {x!r} and {y!r}")
        position, density = sample[x], sample[y]
        for field, observed in ((x, position), (y, density)):
            if observed is not None and not _number(observed):
                raise ValueError(f"distribution {source!r} field {field!r} must be numeric and finite, or null")
        if density is not None and density < 0:
            raise ValueError(f"distribution {source!r} density must be nonnegative")
        if position is not None:
            if position <= previous:
                raise ValueError(f"distribution {source!r} positions must be strictly increasing")
            if log and position <= 0:
                raise ValueError(f"a log scale requires positive distribution positions in {source!r}")
            previous = position
