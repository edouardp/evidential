"""Reusable numeric domains and validation shared by all table update paths."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any, Self

from .configuration import COLOR_SCALES, DomainSpec, validate_options


def domain_spec(value: str | Mapping[str, Any]) -> dict[str, Any]:
    """Copy and normalize a domain declaration without changing caller-owned data."""
    spec: dict[str, Any] = {"name": value} if isinstance(value, str) else dict(value)
    validate_options(spec, DomainSpec, "domain")
    if not isinstance(spec.get("name"), str) or not spec["name"].strip():
        raise ValueError("domain needs a nonempty name")
    for key in ("bounds", "neutral_range"):
        if key in spec:
            lo, hi = spec[key]
            if not all(math.isfinite(v) for v in (lo, hi)) or lo > hi or (key == "bounds" and lo == hi):
                raise ValueError(f"domain {key} must be finite and ordered")
            spec[key] = (lo, hi)
    if "midpoint" in spec and not math.isfinite(spec["midpoint"]):
        raise ValueError("domain midpoint must be finite")
    palette = spec.get("palette")
    if isinstance(palette, str):
        if palette.lower() not in COLOR_SCALES:
            raise ValueError(f"Unknown colour scale {palette!r}")
        spec["palette"] = palette.lower()
    elif palette is not None:
        if len(palette) < 2 or any(not color.strip() for color in palette):
            raise ValueError("domain palette needs at least two nonempty colors")
        spec["palette"] = list(palette)
    return spec


class Domain(Mapping[str, Any]):
    """An immutable named domain; reuse it across columns and tables."""

    __slots__ = ("_spec",)

    def __init__(self, name: str, spec: Mapping[str, Any] | None = None) -> None:
        self._spec = domain_spec({**dict(spec or {}), "name": name})

    def __getitem__(self, key: str) -> Any:
        value = self._spec[key]
        return list(value) if isinstance(value, list) else value

    def __iter__(self):
        return iter(self._spec)

    def __len__(self) -> int:
        return len(self._spec)

    def __repr__(self) -> str:
        return f"Domain({self._spec!r})"

    def _with(self, **options: Any) -> Self:
        return type(self)(self._spec["name"], {**self._spec, **options})

    def include_zero(self, value: bool = True) -> Self:
        """Include zero when inferring bounds; explicit bounds remain fixed."""
        return self._with(include_zero=value)

    def bounds(self, low: float, high: float) -> Self:
        """Set fixed, shared endpoints instead of inferring them from the data."""
        return self._with(bounds=(low, high))

    def palette(self, colors: str | Sequence[str]) -> Self:
        """Share a named color palette or list of colors across color encodings."""
        return self._with(palette=colors)

    def midpoint(self, value: float) -> Self:
        """Anchor a diverging color palette at this value."""
        return self._with(midpoint=value)


def _merge_setting(group: dict[str, Any], key: str, value: Any) -> None:
    if key in group and group[key] != value:
        raise ValueError(f"Conflicting {key} for shared domain {group['name']!r}")
    group[key] = value


def resolve_domains(columns: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Merge named declarations once; reject contradictory per-column settings."""
    groups: dict[str, dict[str, Any]] = {}
    members: dict[str, list[Mapping[str, Any]]] = {}
    for column in columns:
        value = column.get("domain")
        if value is None:
            continue
        spec = domain_spec(value)
        name = spec["name"]
        group = groups.setdefault(name, {"name": name})

        for key, value in spec.items():
            _merge_setting(group, key, value)
        scale = column.get("scale") or {}
        colors = column.get("color_options") or {}
        spark = column.get("sparkline_options") or {}
        if (
            scale.get("domain") is not None
            or any(colors.get(key) is not None for key in ("min", "max", "color_stops"))
            or spark.get("color_domain") is not None
        ):
            raise ValueError(f"Configure shared bounds on domain {name!r}, not on an individual column")
        if scale.get("transform", "linear") != "linear":
            raise ValueError("Shared numeric domains currently require linear scales")
        if scale.get("include_zero") is not None:
            _merge_setting(group, "include_zero", scale["include_zero"])
        if column.get("viz") == "sparkline" and spark.get("type") == "change":
            _merge_setting(group, "neutral_range", tuple(spark.get("steady") or (0, 0)))
        members.setdefault(name, []).append(column)
    for name, group in groups.items():
        columns_in_group = members[name]
        if "include_zero" not in group:
            group["include_zero"] = any(
                (col.get("viz") == "bar")
                or any(
                    enc["kind"] in ("bar", "stacked_bar") and not enc.get("fit_to_data")
                    for enc in col.get("encodings") or []
                )
                or (
                    (col.get("sparkline_options") or {}).get("type") in ("bar", "area")
                    and not col["sparkline_options"].get("fit_to_data")
                )
                for col in columns_in_group
            )
        if "palette" in group:
            for member in columns_in_group:
                midpoint = (member.get("color_options") or {}).get("midpoint")
                if midpoint is not None:
                    _merge_setting(group, "midpoint", midpoint)
        neutral = group.get("neutral_range")
        if neutral is not None:
            bounds = group.get("bounds")
            if bounds and (bounds[0] > neutral[0] or bounds[1] < neutral[1]):
                raise ValueError("Shared domain bounds must contain the steady range")
            if "midpoint" in group and group["midpoint"] != sum(neutral) / 2:
                raise ValueError("Shared domain midpoint must match the steady interval's center")
        for col in columns_in_group:
            color = col.get("color_options") or {}
            spark = col.get("sparkline_options") or {}
            for shared, local in (
                ("palette", color.get("color_scale")),
                ("midpoint", color.get("midpoint")),
                ("palette", spark.get("color_scale")),
            ):
                if local is None or shared not in group:
                    continue
                local = (
                    local.lower()
                    if isinstance(local, str)
                    else list(local)
                    if isinstance(local, (tuple, list))
                    else local
                )
                if local != group[shared]:
                    raise ValueError(f"Conflicting {shared} for shared domain {name!r}")
            if "palette" in group and spark.get("type") == "change" and spark.get("color") is not None:
                raise ValueError("A shared palette conflicts with a constant sparkline color")
            if "palette" in group and color.get("scale_mode", "lch") != "lch":
                raise ValueError("Shared palettes use lch interpolation; remove the per-column scale_mode")
            if "palette" in group and color.get("conditional_colors") is not None:
                raise ValueError("A shared palette conflicts with conditional cell colors")
            if (col.get("bar_options") or {}).get("center") or any(
                enc.get("center") or enc.get("side") or enc.get("diverge_at") for enc in col.get("encodings") or []
            ):
                bounds = group.get("bounds")
                if bounds and bounds[0] < 0 and bounds[0] != -bounds[1]:
                    raise ValueError("Centered bars need symmetric shared bounds or (0, magnitude)")
    return [
        {**col, "domain": dict(groups[domain_spec(col["domain"])["name"]])}
        if col.get("domain") is not None
        else dict(col)
        for col in columns
    ]
