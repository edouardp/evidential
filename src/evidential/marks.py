"""Declarative, multi-encoding columns (the v1.1 API redesign).

The classic builder (``_column.py``) binds a column to one field and gives it at
most one visualisation. This module adds a *presentation slot* that can hold an
ordered list of **encodings** — a bar, a point, a range — each bound to its own
source and sharing one coordinate system::

    col.bar('current', color='navy', size=0.8).bar('previous', color='#d1d5db', size=0.2)
    col.bar('votes', label='@candidate', color='@party_colour')
    col.bar('current').point('target')
    col.range('low', 'high', cap='line').point('estimate').scale(domain=(0, 100), unit='%')

A ``MarkColumn`` is still an immutable :class:`~evidential.Column` (a
``Mapping``), so it drops straight into ``columns=[...]`` and ``column_config``.

Every mark column serializes to the same encoding shape, independent of which
annotations, scales or overlays are configured. Classic ``viz="bar"`` mappings
remain supported as compatibility declarations. Scalar columns do not expose
a bar decoration; use ``col.bar(..., label=True)`` for a bar with a value label.
Callable bindings are evaluated against prepared rows before crossing JSON.

"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal

from ._aliases import alias, format_code
from ._column import Column, _clean, _field
from ._distribution import band_spec, validate_curve
from ._label import LABEL_POSITIONS, _label_spec
from .configuration import EncodingSpec, validate_options

__all__ = [
    "MarkColumn",
    "bar",
    "boxplot",
    "distribution",
    "point",
    "points",
    "range",
    "stacked_bar",
    "strip",
    "LABEL_POSITIONS",
]

#: Supported classic bar style options, honored by the marks renderer too.
_BAR_STYLE_KEYS = {
    "color",
    "color_negative",
    "background",
    "hide_labels",
    "fit_to_data",
    "center",
    "pad",
    "direction",
    "reference",
    "reference_color",
    "reference_label",
}

#: Encoding keys that are style, not source/composition.
_ENCODING_KEYS = (
    "kind",
    "source",
    "high",
    "color",
    "color_negative",
    "color_negative_column",
    "color_column",
    "colors",
    "segmented",
    "strip_labels",
    "parts",
    "outliers",
    "whisker",
    "diverge_at",
    "neutral",
    "x",
    "y",
    "style",
    "distribution",
    "size",
    "outline",
    "side",
    "valign",
    "cap",
    "direction_marker",
    "overflow",
    "fill",
    "fit_to_data",
    "background",
    "hide_labels",
    "center",
    "pad",
    "direction",
    "reference",
    "reference_color",
    "reference_label",
    "label",
)

#: Names for callable-sourced columns whose field cannot be named in Python.
_ANONYMOUS = itertools.count()


def _canonical_encoding(
    kind: str,
    source: Any,
    *,
    high: Any = None,
    label: Any = None,
    label_options: Mapping[str, Any] | None = None,
    label_position: str | None = None,
    **style: Any,
) -> dict[str, Any]:
    """Build one encoding dict, applying the ``@column`` colour convention."""
    field = _field(source)
    if not isinstance(field, str) and not callable(field):
        raise TypeError(f"{kind} expects a field name or a callable, got {source!r}")
    encoding: dict[str, Any] = {"kind": kind, "source": field}
    alias(style, "color_negative", "negative_color")
    if kind in ("bar", "stacked_bar"):
        alias(style, "size", "height")
    if high is not None:
        encoding["high"] = _field(high)
    color = style.pop("color", None)
    if isinstance(color, str) and color.startswith("@"):
        encoding["color_column"] = color[1:]
    elif color is not None:
        encoding["color"] = color
    for key in (
        "color_column",
        "color_negative",
        "color_negative_column",
        "size",
        "outline",
        "side",
        "valign",
        "cap",
        "direction_marker",
        "overflow",
        "fill",
        "fit_to_data",
        "background",
        "hide_labels",
        "center",
        "pad",
        "direction",
        "reference",
        "reference_color",
        "reference_label",
        "colors",
        "segmented",
        "strip_labels",
        "parts",
        "outliers",
        "whisker",
        "diverge_at",
        "neutral",
        "x",
        "y",
        "style",
        "distribution",
    ):
        if style.get(key) is not None:
            encoding[key] = style.pop(key)
    leftover = {key: value for key, value in style.items() if value is not None}
    if leftover:
        raise TypeError(f"Unknown {kind} option(s): {', '.join(sorted(leftover))}")
    negative_color = encoding.get("color_negative")
    if isinstance(negative_color, str) and negative_color.startswith("@"):
        encoding["color_negative_column"] = negative_color[1:]
        encoding.pop("color_negative")
    common = {"kind", "source", "label", "color", "color_column"}
    allowed = {
        "bar": {*_BAR_STYLE_KEYS, "color_negative_column", "side", "size", "valign"},
        "point": {"outline", "size", "valign"},
        "points": {"outline", "size", "valign"},
        "range": {
            "high",
            "cap",
            "direction_marker",
            "color_negative",
            "color_negative_column",
            "size",
            "overflow",
            "fill",
            "valign",
        },
        "strip": {"colors", "strip_labels", "segmented"},
        "stacked_bar": {"size", "diverge_at", "neutral"},
        "boxplot": {"parts", "outliers", "whisker"},
        "distribution": {"distribution"},
    }
    if kind not in allowed:
        raise ValueError(f"Unknown mark kind {kind!r}")
    irrelevant = set(encoding) - common - allowed[kind]
    if "outline" in irrelevant:
        raise ValueError("outline is only supported for point and points marks")
    if irrelevant:
        raise ValueError(f"{', '.join(sorted(irrelevant))} is not supported for {kind} marks")
    if kind == "range" and high is None:
        raise TypeError("range expects two endpoints: col.range(low, high)")
    size = encoding.get("size")
    if size is not None:
        if not isinstance(size, (int, float)) or isinstance(size, bool) or not math.isfinite(size) or size <= 0:
            raise ValueError(f"{kind} size must be finite and positive")
        if kind in ("bar", "stacked_bar") and size > 1:
            raise ValueError(f"{kind} height (size) is a fraction in (0, 1]")
    outline = encoding.get("outline")
    if outline is not None:
        if kind not in ("point", "points"):
            raise ValueError("outline is only supported for point and points marks")
        if not isinstance(outline, bool) and not (isinstance(outline, str) and outline.strip()):
            raise ValueError("point outline must be True, False, or a color string")
    if encoding.get("side") is not None and encoding["side"] not in ("left", "right"):
        raise ValueError(f"side must be 'left' or 'right', got {encoding['side']!r}")
    if encoding.get("overflow") not in (None, "clip", "arrow"):
        raise ValueError("range overflow is 'clip' or 'arrow'")
    label_spec = _label_spec(label, position=label_position, **(label_options or {}))
    if label_spec:
        if label_spec.get("auto") and kind != "bar":
            raise ValueError("auto label placement is only supported for bar marks")
        if kind == "stacked_bar" and label_spec.get("position", "inside_end") not in (
            "inside_start",
            "inside_end",
            "center",
        ):
            raise ValueError("stacked_bar label position is inside_start, inside_end or center")
        encoding["label"] = label_spec
    if kind == "bar" and label is False:
        encoding["hide_labels"] = True
    validate_options(encoding, EncodingSpec, "encoding")
    return {key: encoding[key] for key in _ENCODING_KEYS if key in encoding}


def normalize_encoding(encoding: Mapping[str, Any]) -> dict[str, Any]:
    """Use the same validation for dictionaries, builders and table updates."""
    options = dict(encoding)
    kind = options.pop("kind", None)
    source = options.pop("source", None)
    if kind is None:
        raise ValueError("encoding.kind is required")
    return _canonical_encoding(kind, source, **options)


def _merge_label(previous: Mapping[str, Any] | None, update: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Refine label style, replacing its binding only when a new one is given."""
    if update is None:
        return None
    merged = dict(previous or {})
    if any(key in update for key in ("source", "text", "value")):
        for key in ("source", "text", "value"):
            merged.pop(key, None)
    merged.update(update)
    return merged


class MarkColumn(Column):
    """A column that holds an ordered list of encodings (see module docstring)."""

    __slots__ = ()

    def _with(self, **changes: Any) -> MarkColumn:
        if changes.get("viz") in ("color", "chip", "delta", "symbols"):
            changes["encodings"] = None
        return super()._with(**changes)

    def _encodings(self) -> list[dict[str, Any]]:
        return list(self._spec.get("encodings") or [])

    # --------------------------------------------------------- mark chain ---
    def _add(
        self,
        kind: str,
        source: Any,
        *,
        high: Any = None,
        label: Any = None,
        label_options: Mapping[str, Any] | None = None,
        label_position: str | None = None,
        **style: Any,
    ) -> MarkColumn:
        metadata = _factory_column(self._name, style)._spec
        encodings = self._encodings()
        encodings.append(
            _canonical_encoding(
                kind,
                source,
                high=high,
                label=label,
                label_options=label_options,
                label_position=label_position,
                **style,
            )
        )
        return self._with(
            encodings=encodings, **{key: metadata[key] for key in ("title", "fmt", "align") if key in metadata}
        )

    def bar(
        self,
        source: Any = None,
        *,
        title: str | None = None,
        format: str | None = None,
        fmt: str | None = None,
        align: str | None = None,
        color: str | None = None,
        negative_color: str | None = None,
        color_negative: str | None = None,
        fit_to_data: bool | None = None,
        hide_labels: bool | None = None,
        background: str | None = None,
        center: bool | None = None,
        pad: float | str | None = None,
        direction: Literal["left", "right"] | None = None,
        reference: float | None = None,
        reference_color: str | None = None,
        reference_label: str | None = None,
        size: float | None = None,
        height: float | None = None,
        side: Literal["left", "right"] | None = None,
        valign: Literal["top", "center", "bottom"] | None = None,
        label: Any = None,
        label_options: Mapping[str, Any] | None = None,
        label_position: str | None = None,
    ) -> MarkColumn:
        """Add a bar bound to ``source``; ``label=`` annotates this bar.

        Called without a source it refines the last bar; pass a source to
        append a new bar. Scalar column builders do not have this method.
        """
        column = self._with(**_clean(title=title, fmt=format_code(format, fmt), align=align))
        aliases = {"color_negative": color_negative, "negative_color": negative_color, "size": size, "height": height}
        alias(aliases, "color_negative", "negative_color")
        alias(aliases, "size", "height")
        options: dict[str, Any] = {
            "color": color,
            "color_negative": aliases.get("color_negative"),
            "fit_to_data": fit_to_data,
            "hide_labels": hide_labels,
            "background": background,
            "center": center,
            "pad": pad,
            "direction": direction,
            "reference": reference,
            "reference_color": reference_color,
            "reference_label": reference_label,
            "size": aliases.get("size"),
            "side": side,
            "valign": valign,
        }
        if label is not None:
            options["label"] = label
        if label_position is not None:
            options["label_position"] = label_position
        if label_options is not None:
            options["label_options"] = label_options
        if source is None:
            encodings = column._encodings()
            if not encodings:
                raise ValueError("bar() without a source needs a last bar to refine; pass a source to add one")
            enc = dict(encodings[-1])
            if enc["kind"] != "bar":
                raise ValueError("bar() without a source can only refine the last bar; pass a source to add one")
            if color is not None:
                enc.pop("color_column", None)
            if negative_color is not None or color_negative is not None:
                enc.pop("color_negative_column", None)
            for key, value in options.items():
                if value is not None and key not in ("label", "label_position", "label_options"):
                    enc[key] = value
            if label is not None or label_position is not None or label_options is not None:
                enc["label"] = _merge_label(
                    enc.get("label"), _label_spec(label, position=label_position, **(label_options or {}))
                )
            kind = enc.pop("kind")
            bound_source = enc.pop("source")
            encodings[-1] = _canonical_encoding(kind, bound_source, **enc)
            return column._with(encodings=encodings)
        return column._add("bar", source, **options)

    def point(self, source: Any, *, outline: bool | str | None = None, **options: Any) -> MarkColumn:
        """Add a point; ``outline=False`` removes its ring, or use a color string."""
        return self._add("point", source, outline=outline, **options)

    def points(self, source: Any, *, outline: bool | str | None = None, **options: Any) -> MarkColumn:
        """Add array points, with the same ``outline`` control as scalar points."""
        return self._add("points", source, outline=outline, **options)

    def range(
        self,
        low: Any,
        high: Any | None = None,
        *,
        color_negative: str | Callable[[Mapping[str, Any]], Any] | None = None,
        direction_marker: bool | None = None,
        **options: Any,
    ) -> MarkColumn:
        """Connect two endpoints (a dumbbell / interval); not a confidence claim."""
        if high is None and isinstance(low, (tuple, list)) and len(low) == 2:
            low, high = low
        if high is None:
            raise TypeError("range expects two endpoints: col.range(low, high)")
        return self._add(
            "range", low, high=high, color_negative=color_negative, direction_marker=direction_marker, **options
        )

    def _append_column(self, column: MarkColumn) -> MarkColumn:
        """Compose a factory's validated marks without replacing slot metadata."""
        if any(enc["kind"] == "stacked_bar" for enc in self._encodings()) and any(
            enc["kind"] == "stacked_bar" for enc in column._encodings()
        ):
            raise ValueError("a column can contain one stacked_bar; use separate columns for independent stacks")
        result = self._with(
            encodings=[*self._encodings(), *column._encodings()],
            **{key: column._spec[key] for key in ("title", "fmt", "align") if key in column._spec},
        )
        if column._spec.get("scale"):
            result = result._merge("scale", **column._spec["scale"])
        return result

    def strip(self, source: Any, **options: Any) -> MarkColumn:
        """Append an ordered category sequence (shares coordinates with other strips)."""
        return self._append_column(strip(source, **options))

    def stacked_bar(self, *sources: Any, **options: Any) -> MarkColumn:
        """Append one cumulative stack on the column's shared scale."""
        return self._append_column(stacked_bar(*sources, **options))

    def boxplot(self, minimum: Any, q1: Any, median: Any, q3: Any, maximum: Any, **options: Any) -> MarkColumn:
        """Append a precomputed five-number summary."""
        return self._append_column(boxplot(minimum, q1, median, q3, maximum, **options))

    def distribution(self, source: Any, **options: Any) -> MarkColumn:
        """Append a precomputed density band."""
        return self._append_column(distribution(source, **options))

    def label(
        self,
        value: Any = None,
        *,
        source: str | None = None,
        text: str | None = None,
        position: str | None = None,
        auto: bool | None = None,
        format: str | None = None,
        fmt: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        align: str | None = None,
        overflow: str | None = None,
        min_width: float | None = None,
        color: str | None = None,
        font: str | None = None,
        font_weight: str | None = None,
        font_style: str | None = None,
        figure_style: str | None = None,
    ) -> MarkColumn:
        """Annotate the most recently declared encoding."""
        encodings = self._encodings()
        if not encodings:
            raise ValueError("label() needs a mark first: declare a bar/point/range, then label it")
        spec = _label_spec(
            value,
            source=source,
            text=text,
            position=position,
            auto=auto,
            format=format,
            fmt=fmt,
            prefix=prefix,
            suffix=suffix,
            align=align,
            overflow=overflow,
            min_width=min_width,
            color=color,
            font=font,
            font_weight=font_weight,
            font_style=font_style,
            figure_style=figure_style,
        )
        if spec is None and value is not False:
            return self
        encodings[-1] = {**encodings[-1], "label": _merge_label(encodings[-1].get("label"), spec)}
        if encodings[-1]["kind"] == "bar" and (value is False or (value is True and "hide_labels" in encodings[-1])):
            encodings[-1]["hide_labels"] = value is False
        encodings[-1] = normalize_encoding(encodings[-1])
        return self._with(encodings=encodings)

    # ------------------------------------------------- column-wide options ---
    def scale(
        self,
        domain: Sequence[float | None] | Literal["auto"] | None = None,
        *,
        include_zero: bool | None = None,
        unit: str | None = None,
        transform: str | None = None,
        axis: bool | None = None,
        axis_position: str | None = None,
        gridlines: bool | None = None,
    ) -> MarkColumn:
        """The quantitative axis shared by the column's encodings."""
        spec: dict[str, Any] = dict(self._spec.get("scale") or {})
        if domain is not None:
            if isinstance(domain, str):
                if domain != "auto":
                    raise ValueError("scale domain is 'auto' or a (lo, hi) pair")
                spec.pop("domain", None)
            else:
                domain = tuple(domain)
                if len(domain) != 2:
                    raise ValueError("scale domain expects a (lo, hi) pair")
                if any(bound is not None and not math.isfinite(bound) for bound in domain):
                    raise ValueError("scale domain bounds must be finite")
                if domain[0] is not None and domain[1] is not None and domain[0] >= domain[1]:
                    raise ValueError("scale domain bounds must be increasing")
                spec["domain"] = domain
        if include_zero is not None:
            spec["include_zero"] = include_zero
        if unit is not None:
            spec["unit"] = unit
        if transform is not None:
            if transform not in ("linear", "log"):
                raise ValueError("scale transform is 'linear' or 'log'")
            spec["transform"] = transform
        if spec.get("transform") == "log":
            bounds = [bound for bound in spec.get("domain", ()) if bound is not None]
            if any(bound <= 0 for bound in bounds):
                raise ValueError("a log scale needs a positive domain")
        if axis is not None:
            spec["axis"] = axis
        if axis_position is not None:
            if axis_position not in ("top", "bottom"):
                raise ValueError("axis_position is 'top' or 'bottom'")
            spec["axis_position"] = axis_position
        if gridlines is not None:
            spec["gridlines"] = gridlines
        return self._with(scale=spec or None)

    def reference_line(self, value: float, *, label: str | None = None, color: str | None = None) -> MarkColumn:
        """Draw a column-wide reference rule at ``value`` (on the shared scale)."""
        references = list(self._spec.get("references") or [])
        references.append(_clean(value=value, label=label, color=color))
        return self._with(references=references)

    def reference_band(
        self, low: float, high: float, *, label: str | None = None, color: str | None = None
    ) -> MarkColumn:
        """Shade a column-wide band from ``low`` to ``high`` (a target zone)."""
        if high <= low:
            raise ValueError("reference_band needs high > low")
        references = list(self._spec.get("references") or [])
        references.append(_clean(value=low, high=high, label=label, color=color))
        return self._with(references=references)


def _mark_column(name: Any, **base: Any) -> MarkColumn:
    spec = {"type": "number"}
    if callable(name):
        # An expression column has no field name; give it a stable hidden id.
        name = f"__mark_expr_{next(_ANONYMOUS)}"
    for key in ("title", "fmt", "align"):
        if base.get(key) is not None:
            spec[key] = base.pop(key)
    return MarkColumn(_field(name), {**spec, **{k: v for k, v in base.items() if v is not None}})


def _factory_column(source: Any, options: dict[str, Any], **base: Any) -> MarkColumn:
    """Split common column metadata from mark options for every factory."""
    metadata = {key: options.pop(key) for key in ("title", "align", "fmt", "format") if key in options}
    metadata = {**metadata, **{key: value for key, value in base.items() if value is not None}}
    alias(metadata, "fmt", "format")
    return _mark_column(source, **metadata)


def rebind_measure(column: Mapping[str, Any], source: str, target: str) -> dict[str, Any]:
    """Copy a measure declaration onto a projected field, retaining other bindings.

    Pivot/prior-period outputs rename a measure. Only references to that measure
    change; literal labels/colors and independent dimension bindings stay intact.
    """
    spec = dict(column)
    if not spec.get("encodings"):
        return spec
    encodings = []
    for original in spec["encodings"]:
        encoding = dict(original)
        for role in ("source", "high", "color_column", "color_negative_column", "outliers"):
            if encoding.get(role) == source:
                encoding[role] = target
        if encoding.get("parts"):
            encoding["parts"] = {key: target if value == source else value for key, value in encoding["parts"].items()}
        if (encoding.get("label") or {}).get("source") == source:
            encoding["label"] = {**encoding["label"], "source": target}
        encodings.append(encoding)
    spec["encodings"] = encodings
    return spec


def _resolve_column(
    column: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], hidden: dict[str, list[Any]], used: set[str]
) -> dict[str, Any]:
    """Replace callable sources/styles in one column with hidden-column names."""
    spec = dict(column)
    encodings = spec.get("encodings")
    if not encodings:
        return spec
    resolved: list[dict[str, Any]] = []

    def bind(base: str, function: Any) -> str:
        name = base
        suffix = 1
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1
        used.add(name)
        hidden[name] = [function(row) for row in rows]
        return name

    for index, encoding in enumerate(encodings):
        encoding = dict(encoding)
        for role in ("source", "high", "color", "color_negative"):
            value = encoding.get(role)
            if not callable(value):
                continue
            name = bind(f"__mark_{spec['name']}_{index}_{role}", value)
            if role == "color":
                encoding.pop("color", None)
                encoding["color_column"] = name
            elif role == "color_negative":
                encoding.pop("color_negative", None)
                encoding["color_negative_column"] = name
            else:
                encoding[role] = name
        label = encoding.get("label")
        if isinstance(label, Mapping) and callable(label.get("source")):
            name = bind(f"__mark_{spec['name']}_{index}_label", label["source"])
            encoding["label"] = {**label, "source": name}
        parts = encoding.get("parts")
        if isinstance(parts, Mapping):
            resolved_parts: dict[str, Any] = {}
            for part, value in parts.items():
                if callable(value):
                    name = bind(f"__mark_{spec['name']}_{index}_part_{part}", value)
                    resolved_parts[part] = name
                else:
                    resolved_parts[part] = value
            encoding["parts"] = resolved_parts
        outliers = encoding.get("outliers")
        if callable(outliers):
            name = bind(f"__mark_{spec['name']}_{index}_outliers", outliers)
            encoding["outliers"] = name
        resolved.append(encoding)
    spec["encodings"] = resolved
    return spec


def resolve_encodings(
    columns: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, list[Any]]]:
    """Resolve every callable mark source into a hidden helper column (ADR-006).

    Python callables cannot cross the JSON boundary, so each is evaluated here
    (Python-side, per row) into a generated hidden column; the encoding then
    references that column by name. Returns the rewritten columns and the
    hidden ``{name: values}`` map to merge into the rows.
    """
    hidden: dict[str, list[Any]] = {}
    used = {name for row in rows for name in row}
    resolved = [_resolve_column(column, rows, hidden, used) for column in columns]
    for column in resolved:
        _validate_encoding_data(column, rows, hidden)
    return resolved, hidden


def _validate_encoding_data(
    column: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], hidden: Mapping[str, Sequence[Any]]
) -> None:
    """Validate coordinate compatibility and magnitude constraints before JSON."""
    encodings = column.get("encodings") or []
    if not encodings:
        return
    kinds = {encoding["kind"] for encoding in encodings}
    if column.get("viz") == "sparkline":
        raise ValueError("sparkline cannot share coordinates with scalar marks")
    if "strip" in kinds and len(kinds) > 1:
        raise ValueError("strip cannot share coordinates with scalar marks")
    directions = {encoding.get("direction", "right") for encoding in encodings if encoding["kind"] == "bar"}
    if len(directions) > 1:
        raise ValueError("bars sharing a scale must have the same direction")
    scale = column.get("scale") or {}
    for encoding in encodings:
        if encoding["kind"] == "distribution":
            config = encoding.get("distribution")
            if not isinstance(config, Mapping):
                raise ValueError("distribution needs a band specification; use col.distribution(...)")
            band_spec(**config)
    domain = scale.get("domain")
    if domain and any(
        encoding.get("center") or encoding.get("side") or encoding.get("diverge_at") for encoding in encodings
    ):
        low, high = domain
        if low is not None and high is not None and low != 0 and low != -high:
            raise ValueError("a two-sided scale domain must be (0, magnitude) or (-magnitude, magnitude)")
    for index, row in enumerate(rows):
        if row.get("render_type") not in (None, "cell_data"):
            continue
        for encoding in encodings:
            source = encoding["source"]
            value = hidden[source][index] if source in hidden else row.get(source)
            kind = encoding["kind"]
            if kind == "distribution":
                validate_curve(value, encoding["distribution"], source=source, log=scale.get("transform") == "log")
                continue
            if kind == "strip" and isinstance(value, list) and value:
                last = value[-1]
                if isinstance(last, Mapping) and last.get("position") is not None and last.get("end") is None:
                    domain = scale.get("domain") or (None, None)
                    if domain[1] is None:
                        raise ValueError(
                            "a change-point strip needs an explicit terminal bound: scale(domain=(lo, hi))"
                        )
            if value is None:
                continue
            if kind == "stacked_bar" or encoding.get("side"):
                if float(value) < 0:
                    raise ValueError(f"{kind} source {source!r} requires nonnegative magnitudes")
            if scale.get("transform") != "log":
                continue
            fields = [source, encoding.get("high"), *(encoding.get("parts") or {}).values()]
            values = [hidden[field][index] if field in hidden else row.get(field) for field in fields if field]
            if kind == "points":
                values = [
                    item.get("value", item.get("x", item.get("y"))) if isinstance(item, Mapping) else item
                    for item in value
                ]
            for observed in values:
                if observed is not None and float(observed) <= 0:
                    raise ValueError(f"a log scale needs positive values in {source!r}")


def apply_hidden_columns(rows: list[dict[str, Any]], hidden: Mapping[str, Sequence[Any]]) -> None:
    """Merge resolved hidden-column values into the rows, in place."""
    for name, values in hidden.items():
        for index, row in enumerate(rows):
            if index < len(values):
                row[name] = values[index]


def bar(
    source: Any,
    *,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    **options: Any,
) -> MarkColumn:
    """A number shown as an inline bar; ``label=``/``size=``/``side=`` are mark-owned.

    Example::

        col.bar("votes", label="@candidate", color="@party_colour")
        col.bar("current", color="navy", size=0.8).bar("previous", color="#d1d5db", size=0.2)
    """
    column = _factory_column(source, options, title=title, fmt=format_code(format, fmt), align=align)
    return column._add("bar", source, **options)


def point(
    source: Any,
    *,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    outline: bool | str | None = None,
    **options: Any,
) -> MarkColumn:
    """A point marker; ``outline=False`` hides its ring, or use a color string.

    Omitted/``True`` retains the default outline, independently of the fill.
    """
    column = _factory_column(source, options, title=title, fmt=format_code(format, fmt), align=align)
    return column._add("point", source, outline=outline, **options)


def points(
    source: Any,
    *,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    size: float | None = None,
    color: str | None = None,
    outline: bool | str | None = None,
    **options: Any,
) -> MarkColumn:
    """An array column drawn as one point per observation (a strip/scatter).

    ``source`` holds a list of numbers; each is placed on the column's shared
    scale, so the row's distribution is read directly against a bar or target.
    ``outline=False`` removes rings; a color string sets their color.
    """
    column = _factory_column(source, options, title=title, fmt=format_code(format, fmt), align=align)
    return column._add("points", source, size=size, color=color, outline=outline, **options)._with(type="array")


def range(  # noqa: A001 - the public constructor name
    low: Any,
    high: Any | None = None,
    *,
    color_negative: str | Callable[[Mapping[str, Any]], Any] | None = None,
    direction_marker: bool | None = None,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    **options: Any,
) -> MarkColumn:
    """Connect two endpoints; color decreases and optionally mark their direction.

    ``color_negative`` applies when the second value is below the first.
    ``direction_marker=True`` adds a centered chevron toward the second value.
    """
    if high is None and isinstance(low, (tuple, list)) and len(low) == 2:
        low, high = low
    if high is None:
        raise TypeError("range expects two endpoints: col.range(low, high)")
    column = _factory_column(low, options, title=title, fmt=format_code(format, fmt), align=align)
    return column._add(
        "range", low, high=high, color_negative=color_negative, direction_marker=direction_marker, **options
    )


def strip(
    source: str,
    *,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    colors: Mapping[str, str] | None = None,
    labels: bool | None = None,
    segmented: bool | None = None,
    **options: Any,
) -> MarkColumn:
    """An ordered categorical sequence (form/W-D-L, timeline, states).

    ``source`` is a list of categories (or ``{category: ...}`` objects);
    ``colors`` maps each category to a colour. Unlike ``sparkline`` this encodes
    N ordered observations, not a numeric series.
    """
    column = _factory_column(source, options, title=title, fmt=format_code(format, fmt), align=align)
    encoding = _canonical_encoding(
        "strip", source, colors=dict(colors) if colors else None, segmented=segmented, strip_labels=labels, **options
    )
    return column._with(type="array", encodings=[encoding])


def stacked_bar(
    *sources: Any,
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    colors: Sequence[Any] | None = None,
    labels: bool | str | Mapping[str, Any] | None = None,
    normalize: str | None = None,
    diverge_at: str | None = None,
    neutral: str | None = None,
    size: float | None = None,
    **options: Any,
) -> MarkColumn:
    """A cumulative stack of segment magnitudes (a distinct encoding).

    Each ``source`` is a segment magnitude; ``colors`` is positional. Stacking
    uses the raw additive values and does not normalise automatically; pass
    ``normalize="percent"`` to divide each row's segments by its total. With
    ``diverge_at="neutral", neutral="split"`` the named segment is split around
    a central origin and the categories either side grow left and right.

    ``labels=True`` writes each segment's value; ``labels="percent"`` writes its
    share of the row instead. A fluent ``label`` specification or mapping applies
    to every segment. ``size`` is the stack's height fraction.
    """
    if not sources:
        raise TypeError("stacked_bar needs at least one segment column")
    if not isinstance(labels, Mapping) and labels not in (None, False, True, "percent", "share"):
        raise ValueError("stacked_bar labels is True, False, 'percent' or a label specification")
    if size is not None and not 0 < float(size) <= 1:
        raise ValueError("stacked_bar size is a fraction in (0, 1]")
    column = _factory_column(sources[0], options, title=title, fmt=format_code(format, fmt), align=align)
    height_options = {"size": size, "height": options.pop("height", None)}
    alias(height_options, "size", "height")
    size = height_options.get("size")
    label_position = options.pop(
        "label_position", labels.get("position", "inside_end") if isinstance(labels, Mapping) else "inside_end"
    )
    label_align = options.pop("label_align", None)
    if options:
        raise TypeError(f"Unknown stacked_bar option(s): {', '.join(sorted(options))}")
    encodings: list[dict[str, Any]] = []
    colour_list = list(colors or [])
    if colors is not None and len(colour_list) != len(sources):
        raise ValueError("stacked_bar colors must have one entry per segment")
    for index, source in enumerate(sources):
        style: dict[str, Any] = {}
        if index < len(colour_list) and colour_list[index] is not None:
            style["color"] = colour_list[index]
        if size is not None:
            style["size"] = float(size)
        encoding = _canonical_encoding("stacked_bar", source, **style)
        if labels:
            encoding["label"] = _label_spec(
                labels if isinstance(labels, Mapping) else True,
                position=label_position,
                align=label_align,
                share=labels in ("percent", "share"),
            )
        encodings.append(normalize_encoding(encoding))
    if diverge_at is not None:
        if diverge_at not in [str(source) for source in sources]:
            raise ValueError(f"diverge_at={diverge_at!r} is not one of the segment columns")
        if neutral not in (None, "split"):
            raise ValueError("neutral is 'split' or None")
        encodings[0]["diverge_at"] = diverge_at
        encodings[0]["neutral"] = neutral or "split"
    column = column._with(encodings=encodings)
    if normalize is not None:
        if normalize != "percent":
            raise ValueError("stacked_bar normalize is 'percent' or None")
        scale = dict(column._spec.get("scale") or {})
        scale["normalize"] = "percent"
        column = column._with(scale=scale)
    return column


def boxplot(
    minimum: Any,
    q1: Any,
    median: Any,
    q3: Any,
    maximum: Any,
    *,
    outliers: Any = None,
    whisker: str | None = "extrema",
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    color: str | None = None,
    **options: Any,
) -> MarkColumn:
    """A precomputed five-number summary, with optional outliers.

    ``whisker="extrema"`` (the default) means the whisker endpoints are the
    data minima/maxima; ``whisker="iqr"`` marks 1.5×IQR whiskers. The renderer
    never computes statistics — the five numbers arrive from SQL or Python.
    """
    if whisker not in (None, "extrema", "iqr"):
        raise ValueError("boxplot whisker is 'extrema', 'iqr' or None")
    parts = {
        "minimum": _field(minimum),
        "q1": _field(q1),
        "median": _field(median),
        "q3": _field(q3),
        "maximum": _field(maximum),
    }
    column = _factory_column(median, options, title=title, fmt=format_code(format, fmt), align=align)
    encoding: dict[str, Any] = {"kind": "boxplot", "source": _field(median), "parts": parts}
    if outliers is not None:
        encoding["outliers"] = _field(outliers)
    if whisker is not None:
        encoding["whisker"] = whisker
    if color is not None:
        encoding["color"] = color
    encoding.update(options)
    return column._with(encodings=[normalize_encoding(encoding)])


def distribution(
    source: Any,
    *,
    x: str = "position",
    y: str = "density",
    style: str = "band",
    title: str | None = None,
    format: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    color: str | None = None,
    height: float = 0.5,
    density_max: float | None = None,
    **options: Any,
) -> MarkColumn:
    """A flat uncertainty band from ordered, precomputed density records.

    Density sets opacity, not vertical height. ``height`` is a fraction of the
    row's mark track. By default each row's peak is fully opaque; supply a
    shared positive ``density_max`` for comparable intensity across rows.
    Nulls break the band. Raw samples and density estimation belong upstream.
    """
    if style != "band":
        raise ValueError("distribution style is 'band'")
    config = band_spec(x=x, y=y, height=height, density_max=density_max)
    column = _factory_column(source, options, title=title, fmt=format_code(format, fmt), align=align)
    encoding = _canonical_encoding("distribution", source, distribution=config, color=color, **options)
    return column._with(type="array", encodings=[encoding])
