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

Compatibility: a single plain bar over the column's own field with no label,
size, side, scale or references serialises to the classic ``viz="bar"`` +
``bar_options`` shape, so existing notebooks are unchanged. The new
``encodings`` / ``scale`` / ``references`` keys are emitted only when the new
features are used.

This phase binds field-name sources (including the ``@field`` convention).
Per-row Python callables are resolved to hidden helper columns in a later
phase (see ADR-058).
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from ._column import Column, _clean, _field
from ._distribution import band_spec, validate_curve

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

#: Classic bar options that map one-to-one onto ``bar_options``.
_LEGACY_BAR_KEYS = {
    "color": "bar_color",
    "color_negative": "bar_color_negative",
    "background": "background_color",
    "hide_labels": "hide_labels",
    "fit_to_data": "fit_to_data",
    "center": "center",
    "pad": "pad",
    "direction": "direction",
    "reference": "reference",
    "reference_color": "reference_color",
    "reference_label": "reference_label",
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


def _has_callable(value: Any) -> bool:
    """True if a source/style value (or a nested label) is a Python callable."""
    if callable(value):
        return True
    if isinstance(value, Mapping):
        return any(_has_callable(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_callable(item) for item in value)
    return False


def _label_spec(
    value: Any = None,
    *,
    source: str | None = None,
    text: str | None = None,
    literal: str | None = None,
    position: str | None = None,
    format: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    align: str | None = None,
    share: bool | None = None,
    overflow: str | None = None,
    min_width: float | None = None,
    color: str | None = None,
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
        spec["source"] = _field(source)
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
        if position not in LABEL_POSITIONS:
            raise ValueError(f"Unknown label position {position!r}; use one of {', '.join(LABEL_POSITIONS)}")
        spec["position"] = position
    if align is not None:
        if align not in ("begin", "center", "end"):
            raise ValueError("label align is 'begin', 'center' or 'end'")
        spec["align"] = align
    for key, item in (("format", format), ("prefix", prefix), ("suffix", suffix)):
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
    return spec or None


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
        "size",
        "outline",
        "side",
        "valign",
        "cap",
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
        encoding["label"] = label_spec
    return {key: encoding[key] for key in _ENCODING_KEYS if key in encoding}


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


def _legacy_bar_options(encoding: Mapping[str, Any]) -> dict[str, Any]:
    """The classic ``bar_options`` for a single bar encoding."""
    options: dict[str, Any] = {}
    for source, target in _LEGACY_BAR_KEYS.items():
        if encoding.get(source) is not None:
            options[target] = encoding[source]
    if encoding.get("color_column") is not None:
        options["bar_color_column"] = encoding["color_column"]
    return options


class MarkColumn(Column):
    """A column that holds an ordered list of encodings (see module docstring)."""

    __slots__ = ()

    def _with(self, **changes: Any) -> MarkColumn:
        spec = dict(self._spec)
        for key, value in changes.items():
            if value is None:
                spec.pop(key, None)
            else:
                spec[key] = value
        return MarkColumn(self._name, spec)

    def _merge(self, key: str, **values: Any) -> MarkColumn:
        merged = {**dict(self._spec.get(key) or {}), **_clean(**values)}
        return self._with(**{key: merged or None})

    # ------------------------------------------------------ serialisation ---
    def _encodings(self) -> list[dict[str, Any]]:
        return list(self._spec.get("encodings") or [])

    def _is_legacy(self) -> bool:
        encodings = self._encodings()
        if len(encodings) != 1:
            return False
        if self._spec.get("scale") or self._spec.get("references"):
            return False
        if self._spec.get("viz") == "sparkline":
            return False
        encoding = encodings[0]
        if encoding.get("kind") != "bar" or encoding.get("source") != self._name:
            return False
        # Any callable must be resolved to a hidden column first.
        if _has_callable(encoding):
            return False
        # Any new-only key makes this a marks column.
        return not any(key in encoding for key in ("size", "side", "cap", "label", "valign"))

    def _serialized(self) -> dict[str, Any]:
        spec = dict(self._spec)
        encodings = spec.pop("encodings", None)
        if encodings and self._is_legacy():
            spec["viz"] = "bar"
            options = _legacy_bar_options(encodings[0])
            spec["bar_options"] = options or None
        else:
            if encodings:
                spec["encodings"] = encodings
        return {key: value for key, value in spec.items() if value is not None or key == "type"}

    def __getitem__(self, key: str) -> Any:
        if key == "name":
            return self._name
        return self._serialized()[key]

    def __iter__(self):
        yield "name"
        yield from (key for key in self._serialized() if key != "name")

    def __len__(self) -> int:
        return 1 + len([key for key in self._serialized() if key != "name"])

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
        return self._with(encodings=encodings)

    def bar(
        self,
        source: Any = None,
        *,
        color: str | None = None,
        negative_color: str | None = None,
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
        side: Literal["left", "right"] | None = None,
        valign: Literal["top", "center", "bottom"] | None = None,
        label: Any = None,
        label_position: str | None = None,
    ) -> MarkColumn:
        """Add a bar bound to ``source``; ``label=`` annotates this bar.

        Called without a source it refines the most recently declared encoding
        (kept for signature-compatibility with the classic ``Column.bar``).
        """
        options: dict[str, Any] = {
            "color": color,
            "color_negative": negative_color,
            "fit_to_data": fit_to_data,
            "hide_labels": hide_labels,
            "background": background,
            "center": center,
            "pad": pad,
            "direction": direction,
            "reference": reference,
            "reference_color": reference_color,
            "reference_label": reference_label,
            "size": size,
            "side": side,
            "valign": valign,
        }
        if label is not None:
            options["label"] = label
        if label_position is not None:
            options["label_position"] = label_position
        if source is None:
            encodings = self._encodings()
            if not encodings:
                return self._with(**{key: value for key, value in options.items() if value is not None})
            enc = dict(encodings[-1])
            if color is not None:
                enc.pop("color_column", None)
            for key, value in options.items():
                if value is not None and key not in ("label", "label_position"):
                    enc[key] = value
            if label is not None or label_position is not None:
                enc["label"] = _merge_label(enc.get("label"), _label_spec(label, position=label_position))
            kind = enc.pop("kind")
            bound_source = enc.pop("source")
            encodings[-1] = _canonical_encoding(kind, bound_source, **enc)
            return self._with(encodings=encodings)
        return self._add("bar", source, **_bar_kwargs(options))

    def point(self, source: Any, *, outline: bool | str | None = None, **options: Any) -> MarkColumn:
        """Add a point; ``outline=False`` removes its ring, or use a color string."""
        return self._add("point", source, outline=outline, **options)

    def points(self, source: Any, *, outline: bool | str | None = None, **options: Any) -> MarkColumn:
        """Add array points, with the same ``outline`` control as scalar points."""
        return self._add("points", source, outline=outline, **options)

    def range(self, low: Any, high: Any | None = None, **options: Any) -> MarkColumn:
        """Connect two endpoints (a dumbbell / interval); not a confidence claim."""
        if high is None and isinstance(low, (tuple, list)) and len(low) == 2:
            low, high = low
        if high is None:
            raise TypeError("range expects two endpoints: col.range(low, high)")
        return self._add("range", low, high=high, **options)

    def label(
        self,
        value: Any = None,
        *,
        source: str | None = None,
        text: str | None = None,
        position: str | None = None,
        format: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        align: str | None = None,
        overflow: str | None = None,
        min_width: float | None = None,
        color: str | None = None,
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
            format=format,
            prefix=prefix,
            suffix=suffix,
            align=align,
            overflow=overflow,
            min_width=min_width,
            color=color,
        )
        encodings[-1] = {**encodings[-1], "label": _merge_label(encodings[-1].get("label"), spec)}
        return self._with(encodings=encodings)

    # ------------------------------------------------- column-wide options ---
    def scale(
        self,
        domain: Sequence[float | None] | None = None,
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

    def to_config(self) -> dict[str, Any]:
        """The serialised column definition (same as ``dict(column)``)."""
        return self._serialized()


def _bar_kwargs(options: Mapping[str, Any]) -> dict[str, Any]:
    """Pass bar options through; ``label`` may be a bool, ``"@field"`` or a mapping."""
    return dict(options)


def _mark_column(name: Any, **base: Any) -> MarkColumn:
    spec = {"type": "number"}
    if callable(name):
        # An expression column has no field name; give it a stable hidden id.
        name = f"__mark_expr_{next(_ANONYMOUS)}"
    for key in ("title", "fmt", "align"):
        if base.get(key) is not None:
            spec[key] = base.pop(key)
    return MarkColumn(_field(name), {**spec, **{k: v for k, v in base.items() if v is not None}})


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
    scale = column.get("scale") or {}
    for encoding in encodings:
        if encoding["kind"] == "distribution":
            config = encoding.get("distribution")
            if not isinstance(config, Mapping):
                raise ValueError("distribution needs a band specification; use col.distribution(...)")
            band_spec(**config)
    domain = scale.get("domain")
    if domain and any(encoding.get("side") or encoding.get("diverge_at") for encoding in encodings):
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
    source: Any, *, title: str | None = None, fmt: str | None = None, align: str | None = None, **options: Any
) -> MarkColumn:
    """A number shown as an inline bar; ``label=``/``size=``/``side=`` are mark-owned.

    Example::

        col.bar("votes", label="@candidate", color="@party_colour")
        col.bar("current", color="navy", size=0.8).bar("previous", color="#d1d5db", size=0.2)
    """
    column = _mark_column(source, title=title, fmt=fmt, align=align)
    return column._add("bar", source, **_bar_kwargs(options))


def point(
    source: Any,
    *,
    title: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    outline: bool | str | None = None,
    **options: Any,
) -> MarkColumn:
    """A point marker; ``outline=False`` hides its ring, or use a color string.

    Omitted/``True`` retains the default outline, independently of the fill.
    """
    column = _mark_column(source, title=title, fmt=fmt, align=align)
    return column._add("point", source, outline=outline, **options)


def points(
    source: Any,
    *,
    title: str | None = None,
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
    column = _mark_column(source, title=title)
    return column._add("points", source, size=size, color=color, outline=outline, **options)._with(type="array")


def range(  # noqa: A001 - the public constructor name
    low: Any,
    high: Any | None = None,
    *,
    title: str | None = None,
    fmt: str | None = None,
    align: str | None = None,
    **options: Any,
) -> MarkColumn:
    """Connect two endpoints: ``col.range("low", "high").point("estimate")``."""
    if high is None and isinstance(low, (tuple, list)) and len(low) == 2:
        low, high = low
    column = _mark_column(low, title=title, fmt=fmt, align=align)
    return column._add("range", low, high=high, **options)


def strip(
    source: str,
    *,
    title: str | None = None,
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
    column = _mark_column(source, title=title)
    encoding = _canonical_encoding(
        "strip", source, colors=dict(colors) if colors else None, segmented=segmented, strip_labels=labels, **options
    )
    return column._with(type="array", encodings=[encoding])


def stacked_bar(
    *sources: Any,
    title: str | None = None,
    colors: Sequence[Any] | None = None,
    labels: bool | str | None = None,
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
    share of the row instead. ``size`` is the stack's height fraction.
    """
    if not sources:
        raise TypeError("stacked_bar needs at least one segment column")
    if labels not in (None, False, True, "percent", "share"):
        raise ValueError("stacked_bar labels is True, False or 'percent'")
    if size is not None and not 0 < float(size) <= 1:
        raise ValueError("stacked_bar size is a fraction in (0, 1]")
    column = _mark_column(sources[0], title=title)
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
                True,
                position=options.get("label_position", "inside_end"),
                align=options.get("label_align"),
                share=labels in ("percent", "share"),
            )
        encodings.append(encoding)
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
    encoding: dict[str, Any] = {"kind": "boxplot", "source": _field(median), "parts": parts}
    if outliers is not None:
        encoding["outliers"] = _field(outliers)
    if whisker is not None:
        encoding["whisker"] = whisker
    if color is not None:
        encoding["color"] = color
    if options:
        raise TypeError(f"Unknown boxplot option(s): {', '.join(sorted(options))}")
    column = _mark_column(median, title=title)
    return column._with(encodings=[encoding])


def distribution(
    source: Any,
    *,
    x: str = "position",
    y: str = "density",
    style: str = "band",
    title: str | None = None,
    color: str | None = None,
    height: float = 0.5,
    density_max: float | None = None,
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
    encoding = _canonical_encoding("distribution", source, distribution=config, color=color)
    column = _mark_column(source, title=title)
    return column._with(type="array", encodings=[encoding])
