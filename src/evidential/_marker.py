"""One shape, rotation and outline contract across geometric markers."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from .configuration import MarkerOptions, validate_options


def normalize_marker_options(options: Mapping[str, Any]) -> dict[str, Any]:
    spec = dict(options)
    marker = {key: spec[key] for key in ("shape", "angle", "outline") if spec.get(key) is not None}
    outline = marker.get("outline")
    if outline is not None and not isinstance(outline, bool) and not (isinstance(outline, str) and outline.strip()):
        raise ValueError("marker outline must be True, False, or a color string")
    validate_options(marker, MarkerOptions, "marker")
    if "angle" in marker:
        if not math.isfinite(marker["angle"]):
            raise ValueError("marker angle must be finite")
        spec["angle"] = marker["angle"] % 360
    return spec
