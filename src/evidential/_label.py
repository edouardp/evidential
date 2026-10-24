"""Immutable mark labels and their shared mapping normalizer."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any, Self

from ._aliases import alias, format_code
from ._text_style import TextStyle
from .configuration import EncodingLabel, validate_options

#: Where a mark-owned label may sit.
LABEL_POSITIONS = (
    "inside_start",
    "inside_end",
    "outside_start",
    "outside_end",
    "center",
    "above",
    "below",
)


def _source(value: Any) -> Any:
    return value[1:] if isinstance(value, str) and value.startswith("@") else value


def _position(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("label position must be a string")
    canonical = value.replace("-", "_").replace(" ", "_")
    if canonical not in LABEL_POSITIONS:
        raise ValueError(f"Unknown label position {value!r}; use one of {', '.join(LABEL_POSITIONS)}")
    return canonical


def _label_spec(
    value: Any = None,
    *,
    source: str | Callable[[Mapping[str, Any]], Any] | None = None,
    text: str | None = None,
    literal: str | None = None,
    position: str | None = None,
    auto: bool | None = None,
    format: str | None = None,
    fmt: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    align: str | None = None,
    share: bool | None = None,
    overflow: str | None = None,
    min_width: float | None = None,
    color: str | None = None,
    font: str | None = None,
    font_weight: str | None = None,
    font_style: str | None = None,
    figure_style: str | None = None,
) -> dict[str, Any] | None:
    """Canonicalise a mark-owned label declaration.

    ``label=True`` labels the mark's own value; ``label="@field"`` labels
    another field; ``label="text"`` (through the constructor) is a literal. A
    mapping (``label={"source": "@x", "prefix": "$"}``) is the same as the
    fluent form. ``.label(...)`` is unambiguous: ``source=`` vs ``text=``.
    """
    spec: dict[str, Any] = {}
    if isinstance(value, Mapping):
        spec.update({key: item for key, item in value.items() if item is not None})
        value = None
    if source is not None:
        spec["source"] = _source(source)
    if text is not None:
        spec["text"] = text
    if literal is not None:
        spec["text"] = literal
    if value is True:
        spec["value"] = True
    elif value is False:
        return None
    elif isinstance(value, str):
        if value.startswith("@"):
            spec["source"] = value[1:]
        else:
            spec["text"] = value
    elif value is not None:
        raise TypeError(f"label expects True, False, '@field', a string or a mapping, got {value!r}")
    if position is not None:
        position = _position(position)
        spec["position"] = position
    if align is not None:
        if align not in ("begin", "center", "end"):
            raise ValueError("label align is 'begin', 'center' or 'end'")
        spec["align"] = align
    for key, item in (("format", format_code(format, fmt)), ("prefix", prefix), ("suffix", suffix)):
        if item is not None:
            spec[key] = item
    if share:
        spec["share"] = True
    if overflow is not None:
        if overflow not in ("hide", "show"):
            raise ValueError("label overflow is 'hide' or 'show'")
        spec["overflow"] = overflow
    if min_width is not None:
        if not math.isfinite(min_width) or min_width < 0:
            raise ValueError("label min_width must be finite and nonnegative")
        spec["min_width"] = min_width
    if color is not None:
        spec["color"] = color
    for key, item in (
        ("font", font),
        ("font_weight", font_weight),
        ("font_style", font_style),
        ("figure_style", figure_style),
    ):
        if item is not None:
            spec[key] = item
    if auto is not None:
        spec["auto"] = auto
    alias(spec, "format", "fmt")
    if spec.get("source") is not None:
        spec["source"] = _source(spec["source"])
    if spec.get("position") is not None:
        spec["position"] = _position(spec["position"])
    if spec.get("min_width") is not None and (not math.isfinite(spec["min_width"]) or spec["min_width"] < 0):
        raise ValueError("label min_width must be finite and nonnegative")
    if sum(key in spec for key in ("source", "text", "value")) > 1:
        raise ValueError("label needs only one of source, text or value")
    validate_options(spec, EncodingLabel, "label")
    if spec.get("auto"):
        if spec.get("position", "outside_end") not in LABEL_POSITIONS[:4]:
            raise ValueError("auto label position must specify inside/outside and start/end")
        if spec.get("overflow") == "show":
            raise ValueError("auto label placement cannot use overflow='show'")
    return spec or None


class Label(TextStyle, Mapping[str, Any]):
    """A reusable mark annotation. Every refinement returns a new label.

    With no explicit source or text, labels show the mark's own value.
    Use the :mod:`evidential.label` namespace to start a chain.
    """

    __slots__ = ("_spec",)
    _format_key = "format"
    _text_color_key = "color"

    def __init__(self, spec: Mapping[str, Any] | None = None) -> None:
        self._spec = _label_spec(spec or {}) or {}
        if not any(key in self._spec for key in ("source", "text", "value")):
            self._spec["value"] = True

    def __getitem__(self, key: str) -> Any:
        return self._spec[key]

    def __iter__(self):
        return iter(self._spec)

    def __len__(self) -> int:
        return len(self._spec)

    def __repr__(self) -> str:
        return f"Label({self._spec!r})"

    def _with(self, **changes: Any) -> Self:
        spec = {**self._spec, **changes}
        return type(self)({key: value for key, value in spec.items() if value is not None})

    def source(self, field: str | Callable[[Mapping[str, Any]], Any]) -> Self:
        """Label another field (or a callable evaluated against each prepared row)."""
        return self._with(source=field, text=None, value=None)

    def text(self, value: str) -> Self:
        """Use literal text instead of a field's value."""
        return self._with(text=value, source=None, value=None)

    def value(self) -> Self:
        """Show the mark's own value, clearing a previous source or literal."""
        return self._with(value=True, source=None, text=None)

    def position(self, value: str) -> Self:
        """Fix placement, e.g. ``"inside end"``; disables automatic placement."""
        return self._with(position=_position(value), auto=False)

    def auto_position(self, preferred: str) -> Self:
        """Try this position, then swap inside/outside at the same edge; omit if neither fits."""
        return self._with(position=_position(preferred), auto=True)

    def align(self, value: str) -> Self:
        """Align text within the mark: begin/left, center, or end/right."""
        return self._with(align={"left": "begin", "right": "end"}.get(value, value))

    def prefix(self, value: str) -> Self:
        """Prepend text to the formatted value."""
        return self._with(prefix=value)

    def suffix(self, value: str) -> Self:
        """Append text to the formatted value."""
        return self._with(suffix=value)

    def share(self, value: bool = True) -> Self:
        """Label a stacked segment with its share of the row total."""
        return self._with(share=value)

    def overflow(self, value: str) -> Self:
        """Hide fixed labels that do not fit, or explicitly show overflowing text."""
        return self._with(overflow=value)

    def min_width(self, pixels: float) -> Self:
        """Omit labels whose available box is narrower than this many pixels."""
        return self._with(min_width=pixels)

    color = TextStyle.font_color
    colour = TextStyle.font_color
