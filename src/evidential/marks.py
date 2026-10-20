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
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from ._column import Column, _clean, _field

__all__ = ["MarkColumn", "bar", "point", "range", "stacked_bar", "strip", "LABEL_POSITIONS"]

#: Where a mark-owned label may sit.
LABEL_POSITIONS = (
    "inside_start",
    "inside_end",
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
    "size",
    "side",
    "cap",
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
) -> dict[str, Any] | None:
    """Canonicalise a mark-owned label declaration.

    ``label=True`` labels the mark's own value; ``label="@field"`` labels
    another field; ``label="text"`` (through the constructor) is a literal. The
    fluent ``.label(...)`` form is unambiguous: ``source=`` vs ``text=``.
    """
    spec: dict[str, Any] = {}
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
        raise TypeError(f"label expects True, False, '@field' or a string, got {value!r}")
    if position is not None:
        if position not in LABEL_POSITIONS:
            raise ValueError(f"Unknown label position {position!r}; use one of {', '.join(LABEL_POSITIONS)}")
        spec["position"] = position
    if format is not None:
        spec["format"] = format
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
        "side",
        "cap",
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
    ):
        if style.get(key) is not None:
            encoding[key] = style.pop(key)
    leftover = {key: value for key, value in style.items() if value is not None}
    if leftover:
        raise TypeError(f"Unknown {kind} option(s): {', '.join(sorted(leftover))}")
    if encoding.get("side") is not None and encoding["side"] not in ("left", "right"):
        raise ValueError(f"side must be 'left' or 'right', got {encoding['side']!r}")
    label_spec = _label_spec(label, position=label_position, **(label_options or {}))
    if label_spec:
        encoding["label"] = label_spec
    return {key: encoding[key] for key in _ENCODING_KEYS if key in encoding}


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
        encoding = encodings[0]
        if encoding.get("kind") != "bar" or encoding.get("source") != self._name:
            return False
        # Any callable must be resolved to a hidden column first.
        if _has_callable(encoding):
            return False
        # Any new-only key makes this a marks column.
        return not any(key in encoding for key in ("size", "side", "cap", "label"))

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
            for key, value in options.items():
                if value is not None and key != "label_position":
                    enc[key] = value
            if label_position is not None:
                enc["label"] = _label_spec(label, position=label_position)
            encodings[-1] = enc
            return self._with(encodings=encodings)
        return self._add("bar", source, **_bar_kwargs(options))

    def point(self, source: Any, **options: Any) -> MarkColumn:
        """Add a point marker at ``source``."""
        return self._add("point", source, **options)

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
    ) -> MarkColumn:
        """Annotate the most recently declared encoding."""
        encodings = self._encodings()
        if not encodings:
            raise ValueError("label() needs a mark first: declare a bar/point/range, then label it")
        spec = _label_spec(value, source=source, text=text, position=position, format=format)
        encodings[-1] = {**encodings[-1], "label": spec}
        return self._with(encodings=encodings)

    # ------------------------------------------------- column-wide options ---
    def scale(
        self,
        domain: Sequence[float | None] | None = None,
        *,
        include_zero: bool | None = None,
        unit: str | None = None,
    ) -> MarkColumn:
        """The quantitative axis shared by the column's encodings."""
        spec: dict[str, Any] = {}
        if domain is not None:
            if isinstance(domain, str):
                if domain != "auto":
                    raise ValueError("scale domain is 'auto' or a (lo, hi) pair")
            else:
                domain = tuple(domain)
                if len(domain) != 2:
                    raise ValueError("scale domain expects a (lo, hi) pair")
                spec["domain"] = domain
        if include_zero is not None:
            spec["include_zero"] = include_zero
        if unit is not None:
            spec["unit"] = unit
        return self._with(scale=spec or None)

    def reference_line(self, value: float, *, label: str | None = None, color: str | None = None) -> MarkColumn:
        """Draw a column-wide reference rule at ``value`` (on the shared scale)."""
        references = list(self._spec.get("references") or [])
        references.append(_clean(value=value, label=label, color=color))
        return self._with(references=references)

    def to_config(self) -> dict[str, Any]:
        """The serialised column definition (same as ``dict(column)``)."""
        return self._serialized()


def _bar_kwargs(options: Mapping[str, Any]) -> dict[str, Any]:
    """Accept both ``label='@x'`` and ``label={'source': 'x'}`` in a bar call."""
    options = dict(options)
    label = options.pop("label", None)
    if isinstance(label, Mapping):
        options["label_options"] = dict(label)
        label = label.get("value")
        if label is None and "source" not in options["label_options"]:
            label = True
    return {**options, "label": label}


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
    column: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], hidden: dict[str, list[Any]]
) -> dict[str, Any]:
    """Replace callable sources/styles in one column with hidden-column names."""
    spec = dict(column)
    encodings = spec.get("encodings")
    if not encodings:
        return spec
    resolved: list[dict[str, Any]] = []
    for index, encoding in enumerate(encodings):
        encoding = dict(encoding)
        for role in ("source", "high", "color", "color_negative"):
            value = encoding.get(role)
            if not callable(value):
                continue
            name = f"__mark_{spec['name']}_{index}_{role}"
            hidden[name] = [value(row) for row in rows]
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
            name = f"__mark_{spec['name']}_{index}_label"
            hidden[name] = [label["source"](row) for row in rows]
            encoding["label"] = {**label, "source": name}
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
    resolved = [_resolve_column(column, rows, hidden) for column in columns]
    return resolved, hidden


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
    **options: Any,
) -> MarkColumn:
    """A point marker at ``source`` (e.g. a target on a bar's scale)."""
    column = _mark_column(source, title=title, fmt=fmt, align=align)
    return column._add("point", source, **options)


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
    labels: bool | None = None,
    normalize: str | None = None,
    **options: Any,
) -> MarkColumn:
    """A cumulative stack of segment magnitudes (a distinct encoding).

    Each ``source`` is a segment magnitude; ``colors`` is positional. Stacking
    uses the raw additive values and does not normalise automatically; pass
    ``normalize="percent"`` to divide each row by its total.
    """
    if not sources:
        raise TypeError("stacked_bar needs at least one segment column")
    column = _mark_column(sources[0], title=title)
    encodings: list[dict[str, Any]] = []
    colour_list = list(colors or [])
    for index, source in enumerate(sources):
        style: dict[str, Any] = {}
        if index < len(colour_list) and colour_list[index] is not None:
            style["color"] = colour_list[index]
        encoding = _canonical_encoding("stacked_bar", source, **style)
        if labels:
            encoding["label"] = {"value": True, "position": options.get("label_position", "inside_end")}
        encodings.append(encoding)
    column = column._with(encodings=encodings)
    if normalize is not None:
        if normalize != "percent":
            raise ValueError("stacked_bar normalize is 'percent' or None")
        column = column._with(scale={"normalize": "percent"})
    return column
