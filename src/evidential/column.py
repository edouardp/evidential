"""The ``col`` column-spec builder.

Factories return an immutable :class:`Column`; every method returns a *new*
column, so a spec can be built, reused and composed::

    from evidential import col

    columns=[
        col.text("city"),
        col.number("sales").fmt("usd0").bar(color="#93c5fd", fit_to_data=True),
        col.sparkline("trend", type="area"),
        col.chip("status", min_width=72, conditional_colors="status_color"),
        col.delta("change", down_is_good=True, neutral_range="0.05"),
    ]

A :class:`Column` is a :class:`~collections.abc.Mapping`, so it is accepted
anywhere a column definition is — including
``column_config={"sales": col.number("sales").bar(...)}``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from .configuration import ColumnOptions, validate_options

Align = Literal["left", "right", "center"]
Rotation = Literal["vertical"] | float

__all__ = [
    "Column",
    "array",
    "boolean",
    "chip",
    "date",
    "delta",
    "html",
    "image",
    "link",
    "logo",
    "markdown",
    "number",
    "sparkline",
    "text",
]


def _clean(**values: Any) -> dict[str, Any]:
    """Drop unset (``None``) values, keeping ``False`` and ``0``."""
    return {key: value for key, value in values.items() if value is not None}


class Column(Mapping[str, Any]):
    """An immutable column definition; every method returns a new ``Column``."""

    __slots__ = ("_name", "_spec")

    def __init__(self, name: str, spec: Mapping[str, Any] | None = None) -> None:
        self._name = name
        self._spec = dict(spec or {})

    # --------------------------------------------------------- mapping ---
    def __getitem__(self, key: str) -> Any:
        if key == "name":
            return self._name
        return self._spec[key]

    def __iter__(self):
        yield "name"
        yield from self._spec

    def __len__(self) -> int:
        return 1 + len(self._spec)

    def __repr__(self) -> str:
        args = ", ".join(f"{key}={value!r}" for key, value in self._spec.items())
        return f"col({self._name!r}, {args})" if args else f"col({self._name!r})"

    # ---------------------------------------------------------- builder ---
    def _with(self, **changes: Any) -> Column:
        spec = dict(self._spec)
        for key, value in changes.items():
            if value is None:
                spec.pop(key, None)
            else:
                spec[key] = value
        return Column(self._name, spec)

    def _merge(self, key: str, **values: Any) -> Column:
        merged = {**dict(self._spec.get(key) or {}), **_clean(**values)}
        return self._with(**{key: merged or None})

    # -- labels and formatting -------------------------------------------
    def title(self, value: str) -> Column:
        return self._with(title=value)

    def fmt(self, code: str) -> Column:
        return self._with(fmt=code)

    #: ``format`` reads better in a chain; ``fmt`` matches the option name.
    format = fmt

    def total_fmt(self, code: str) -> Column:
        return self._with(total_fmt=code)

    def subtotal_fmt(self, code: str) -> Column:
        return self._with(subtotal_fmt=code)

    def align(self, value: Align) -> Column:
        return self._with(align=value)

    def align_decimals(self, value: bool = True) -> Column:
        return self._with(align_decimals=value)

    def figure_style(self, value: str) -> Column:
        return self._with(figure_style=value)

    def font(self, family: str) -> Column:
        return self._with(font=family)

    def font_color(self, color: str) -> Column:
        return self._with(font_color=color)

    def wrap(self, value: bool = True) -> Column:
        return self._with(wrap=value)

    def null_text(self, text: str) -> Column:
        return self._with(null_text=text)

    def blank_below(self, value: float) -> Column:
        return self._with(blank_below=value)

    def blank_above(self, value: float) -> Column:
        return self._with(blank_above=value)

    def blank(self, predicate: Any) -> Column:
        return self._with(blank=predicate)

    def red_negatives(self, value: bool = True) -> Column:
        return self._with(red_negatives=value)

    def rotate_title(self, value: Rotation) -> Column:
        return self._with(rotate_title=value)

    # -- placement and metadata ------------------------------------------
    def group(self, value: str | Sequence[str]) -> Column:
        return self._with(column_group=value)

    def subcolumn(self, value: str) -> Column:
        return self._with(subcolumn_group=value)

    def repeat_values(self, value: bool = True) -> Column:
        return self._with(repeat_values=value)

    def hide(self, value: bool = True) -> Column:
        return self._with(hide=value)

    def info(self, text: str) -> Column:
        return self._with(info=text)

    def footnote(self, column: str) -> Column:
        return self._with(footnote=column)

    def sort_by(self, column: str) -> Column:
        return self._with(sort_by=column)

    def highlight(self, color: str) -> Column:
        return self._with(highlight=color)

    # -- cell content ----------------------------------------------------
    def markdown(self) -> Column:
        return self._with(markdown=True)

    def html(self) -> Column:
        return self._with(html=True)

    def link(self, column: str | None = None, *, label: str | None = None, new_tab: bool = False) -> Column:
        return self._with(
            **_clean(link=column or self._name, link_label=label, link_new_tab=new_tab or None),
        )

    def image(
        self,
        column: str | None = None,
        *,
        height: float | None = None,
        width: float | None = None,
        alt: str | None = None,
    ) -> Column:
        return self._with(
            image=column or self._name, **_merge_options("image_options", height=height, width=width, alt=alt)
        )

    def logo(self, column: str | None = None, *, height: float | None = None) -> Column:
        return self._with(logo=column or self._name, **_merge_options("logo_options", height=height))

    def template(self, value: str, **formats: str) -> Column:
        return self._with(template=value, template_fmt=_clean(**formats) or None)

    # -- visualizations --------------------------------------------------
    def viz(self, kind: str, **options: Any) -> Column:
        return self._with(viz=kind, **{f"{kind}_options": _clean(**options)})

    def bar(
        self,
        *,
        color: str | None = None,
        negative_color: str | None = None,
        fit_to_data: bool | None = None,
        hide_labels: bool | None = None,
        background: str | None = None,
    ) -> Column:
        return self._with(
            viz="bar",
            **_merge_options(
                "bar_options",
                bar_color=color,
                bar_color_negative=negative_color,
                fit_to_data=fit_to_data,
                hide_labels=hide_labels,
                background_color=background,
            ),
        )

    def color(
        self,
        *,
        scale: Any = None,
        stops: Any = None,
        conditional_colors: str | None = None,
        scale_column: str | None = None,
        min: float | None = None,
        max: float | None = None,
        midpoint: float | None = None,
    ) -> Column:
        return self._with(
            viz="color",
            **_merge_options(
                "color_options",
                color_scale=scale,
                color_stops=stops,
                conditional_colors=conditional_colors,
                scale_column=scale_column,
                min=min,
                max=max,
                midpoint=midpoint,
            ),
        )

    def delta(
        self,
        *,
        down_is_good: bool | None = None,
        neutral_range: Any = None,
        chip: bool | None = None,
        show_value: bool | None = None,
        show_symbol: bool | None = None,
        symbol_position: Literal["left", "right"] | None = None,
    ) -> Column:
        return self._with(
            viz="delta",
            **_merge_options(
                "delta_options",
                down_is_good=down_is_good,
                neutral_range=neutral_range,
                chip=chip,
                show_value=show_value,
                show_symbol=show_symbol,
                symbol_position=symbol_position,
            ),
        )

    def sparkline(
        self,
        *,
        type: Literal["line", "area", "bar"] | None = None,
        x: str | None = None,
        y: str | None = None,
        color: str | None = None,
        fit_to_data: bool | None = None,
        y_fmt: str | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> Column:
        return self._with(
            viz="sparkline",
            **_merge_options(
                "sparkline_options",
                type=type,
                x=x,
                y=y,
                color=color,
                fit_to_data=fit_to_data,
                y_fmt=y_fmt,
                width=width,
                height=height,
            ),
        )

    def chip(
        self,
        *,
        min_width: Any = None,
        conditional_colors: str | None = None,
        scale: Any = None,
    ) -> Column:
        changes: dict[str, Any] = {"viz": "chip"}
        chip = _clean(min_width=min_width)
        if chip:
            changes["chip_options"] = {**dict(self._spec.get("chip_options") or {}), **chip}
        color = _clean(conditional_colors=conditional_colors, color_scale=scale)
        if color:
            changes["color_options"] = {**dict(self._spec.get("color_options") or {}), **color}
        return self._with(**changes)

    # ----------------------------------------------------------- output ---
    def to_config(self) -> dict[str, Any]:
        """Validate and return the plain column definition (the wire format)."""
        config = {"name": self._name, **self._spec}
        validate_options(config, ColumnOptions, "column")
        return config


def _merge_options(key: str, **values: Any) -> dict[str, Any]:
    options = _clean(**values)
    return {key: options} if options else {}


# ------------------------------------------------------------------ factories ---
def _column(name: str, type_name: str, **spec: Any) -> Column:
    return Column(name, {"type": type_name, **_clean(**spec)})


def text(name: str, *, title: str | None = None, **extra: Any) -> Column:
    return _column(name, "string", title=title, **extra)


def number(
    name: str, *, fmt: str | None = None, align: Align | None = None, title: str | None = None, **extra: Any
) -> Column:
    return _column(name, "number", fmt=fmt, align=align, title=title, **extra)


def date(
    name: str, *, fmt: str | None = None, align: Align | None = None, title: str | None = None, **extra: Any
) -> Column:
    return _column(name, "date", fmt=fmt, align=align, title=title, **extra)


def boolean(name: str, *, title: str | None = None, **extra: Any) -> Column:
    return _column(name, "boolean", title=title, **extra)


def array(name: str, *, title: str | None = None, **extra: Any) -> Column:
    return _column(name, "array", title=title, **extra)


def markdown(name: str, *, title: str | None = None, **extra: Any) -> Column:
    return _column(name, "string", title=title, markdown=True, **extra)


def html(name: str, *, title: str | None = None, **extra: Any) -> Column:
    return _column(name, "string", title=title, html=True, **extra)


def link(
    name: str, *, label: str | None = None, new_tab: bool = False, title: str | None = None, **extra: Any
) -> Column:
    return _column(name, "string", title=title, link=name, link_label=label, link_new_tab=new_tab or None, **extra)


def image(
    name: str, *, height: float | None = None, width: float | None = None, alt: str | None = None, **extra: Any
) -> Column:
    return _column(
        name, "string", image=name, image_options=_clean(height=height, width=width, alt=alt) or None, **extra
    )


def logo(name: str, *, height: float | None = None, **extra: Any) -> Column:
    return _column(name, "string", logo=name, logo_options=_clean(height=height) or None, **extra)


def sparkline(name: str, *, type: Literal["line", "area", "bar"] = "line", **extra: Any) -> Column:
    return Column(name, {"type": "array", "viz": "sparkline", "sparkline_options": {"type": type}, **_clean(**extra)})


def chip(
    name: str, *, min_width: Any = None, conditional_colors: str | None = None, scale: Any = None, **extra: Any
) -> Column:
    # A text chip; use ``col.number("aqi").chip(...)`` for a numeric one.
    return Column(name, {"type": "string", **_clean(**extra)}).chip(
        min_width=min_width,
        conditional_colors=conditional_colors,
        scale=scale,
    )


def delta(
    name: str, *, down_is_good: bool | None = None, neutral_range: Any = None, chip: bool | None = None, **extra: Any
) -> Column:
    return Column(name, {"type": "number", **_clean(**extra)}).delta(
        down_is_good=down_is_good,
        neutral_range=neutral_range,
        chip=chip,
    )
