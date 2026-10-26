"""Implementation of the ``col`` column builder (private).

The public, completable surface is :mod:`evidential.col`, which re-exports only
the factory entry points. ``Column``, ``ColumnGroup``, ``CURRENCY_CODES`` and
the helpers live here so that ``col.`` completion shows only the kinds you can
build a column from.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal, Self

from ._aliases import alias, format_code
from ._column_options import _normalize_column_options
from ._domain import domain_spec
from ._sparkline import normalize_sparkline_options
from ._text_style import TextStyle
from .configuration import Relative, SparklineType

Align = Literal["left", "right", "center"]
Rotation = Literal["vertical"] | float

__all__ = [
    "CURRENCY_CODES",
    "Column",
    "ColumnGroup",
    "array",
    "auto",
    "boolean",
    "chip",
    "color",
    "currency",
    "date",
    "datetime",
    "delta",
    "flag",
    "group",
    "html",
    "icons",
    "image",
    "integer",
    "link",
    "logo",
    "markdown",
    "merge",
    "number",
    "percent",
    "rating",
    "repeat",
    "sparkline",
    "subcolumns",
    "symbols",
    "text",
    "time",
    "url",
]

#: Currency codes the formatter knows (``col.currency(code=...)``).
CURRENCY_CODES = ("usd", "eur", "gbp", "aud", "cad", "cny", "jpy", "inr", "krw", "ngn", "sek")


def _clean(**values: Any) -> dict[str, Any]:
    """Drop unset (``None``) values, keeping ``False`` and ``0``."""
    return {key: value for key, value in values.items() if value is not None}


def _field(value: Any) -> Any:
    """``"@column"`` names the column ``column`` (the reference convention)."""
    return value[1:] if isinstance(value, str) and value.startswith("@") else value


class Column(TextStyle, Mapping[str, Any]):
    """An immutable column definition; every method returns a new ``Column``.

    Build one with a ``col.<kind>("name")`` factory and refine it by chaining::

        col.bar("sales", format="eur", label=True, color="#93c5fd").title("Revenue")

    Because chaining never mutates, a spec can be stored and reused::

        money = col.number("sales").fmt("usd0").align("right")
        columns=[money, money.title("Revenue")]
    """

    __slots__ = ("_name", "_spec")

    def __init__(self, name: str, spec: Mapping[str, Any] | None = None) -> None:
        self._name = name
        self._spec = dict(spec or {})

    # --------------------------------------------------------- mapping ---
    def __getitem__(self, key: str) -> Any:
        """Return the value of ``key``; ``"name"`` is the column's name."""
        if key == "name":
            return self._name
        return self._spec[key]

    def __iter__(self):
        """Iterate the keys (``"name"`` first, then the configured options)."""
        yield "name"
        yield from self._spec

    def __len__(self) -> int:
        """The number of keys (the name plus the configured options)."""
        return 1 + len(self._spec)

    def __repr__(self) -> str:
        """A readable ``col('name', option=value, …)`` form."""
        args = ", ".join(f"{key}={value!r}" for key, value in self._spec.items())
        return f"col({self._name!r}, {args})" if args else f"col({self._name!r})"

    # ---------------------------------------------------------- builder ---
    def _with(self, **changes: Any) -> Self:
        """Return a copy with ``changes`` applied; ``None`` values remove a key."""
        spec = dict(self._spec)
        for key, value in changes.items():
            if value is None:
                spec.pop(key, None)
            elif key.endswith("_options") and isinstance(value, Mapping):
                spec[key] = {**dict(spec.get(key) or {}), **value}
            else:
                spec[key] = value
        return type(self)(self._name, spec)

    def domain(self, value: str | Mapping[str, Any]) -> Self:
        """Share a named numeric domain with other columns, across header groups.

        Pass a name to infer combined bounds, or a reusable ``domain.numeric``
        specification to share fixed bounds and color settings too.
        """
        return self._with(domain=domain_spec(value))

    def _merge(self, key: str, **values: Any) -> Self:
        """Return a copy with ``values`` merged into the nested ``key`` options."""
        merged = {**dict(self._spec.get(key) or {}), **_clean(**values)}
        return self._with(**{key: merged or None})

    # -- labels and formatting -------------------------------------------
    def title(self, value: str) -> Self:
        """Override the column's header text.

        A ``"\\n"`` in the title forces a line break.

        Example::

            col.text("first_name").title("First name")
        """
        return self._with(title=value)

    def relative(self, value: Relative = True) -> Self:
        """Render the value relative to now (e.g. ``"3 days ago"``) instead of as
        an absolute date, using :js:class:`Intl.RelativeTimeFormat`.

        :param value: ``True`` for an automatically chosen unit, or one of
            ``"second"``, ``"minute"``, ``"hour"``, ``"day"``, ``"week"``,
            ``"month"``, ``"year"`` to fix the unit.

        Example::

            col.datetime("updated_at").relative()
            col.date("due_date", relative="day")
        """
        return self._with(relative=value)

    def fmt_column(self, column: str) -> Self:
        """Take the format code from another column, per row.

        The named column holds a format code; each cell is formatted with its own
        row's code (Evidence's ``fmtColumn``).

        Example::

            col.number("amount").fmt_column("row_fmt")
        """
        return self._with(fmt_column=_field(column))

    format_column = fmt_column

    def total_fmt(self, code: str) -> Self:
        """Format the total row differently from the cells.

        Example::

            col.number("sales").fmt("usd0").total_fmt("usd2")
        """
        return self._with(total_fmt=code)

    def subtotal_fmt(self, code: str) -> Self:
        """Format subtotal rows differently from the cells.

        Example::

            col.number("sales").fmt("usd0").subtotal_fmt("usd1")
        """
        return self._with(subtotal_fmt=code)

    total_format = total_fmt
    subtotal_format = subtotal_fmt

    def align(self, value: Align) -> Self:
        """Set the text alignment: ``"left"``, ``"right"`` or ``"center"``.

        Numbers default to right and text to left.

        Example::

            col.text("year").align("center")
        """
        return self._with(align=value)

    def align_decimals(self, value: bool = True) -> Self:
        """Align the whole column on the decimal point.

        Example::

            col.number("price").fmt("usd2").align_decimals()
        """
        return self._with(align_decimals=value)

    def wrap(self, value: bool = True) -> Self:
        """Allow (or forbid) the cell text to wrap onto several lines.

        Example::

            col.text("description").wrap()
        """
        return self._with(wrap=value)

    def null_text(self, text: str) -> Self:
        """Text to show for a NULL value (the default is the table's ``null_text``).

        Example::

            col.text("manager").null_text("—")
        """
        return self._with(null_text=text)

    def blank_below(self, value: float) -> Self:
        """Leave the cell blank when the value is below ``value``.

        Example::

            col.number("sales").blank_below(100)
        """
        return self._with(blank_below=value)

    def blank_above(self, value: float) -> Self:
        """Leave the cell blank when the value is above ``value``.

        Example::

            col.number("share").blank_above(1)
        """
        return self._with(blank_above=value)

    def blank(self, predicate: Any) -> Self:
        """Leave the cell blank when a rule matches.

        ``predicate`` is a rule name or expression, as understood by the rule
        engine (see ``docs`` on conditional rules).

        Example::

            col.number("delta").blank("delta == 0")
        """
        return self._with(blank=predicate)

    def red_negatives(self, value: bool = True) -> Self:
        """Colour negative values red (Evidence's ``redNegatives``).

        :meth:`neg` is the richer spelling.

        Example::

            col.number("profit").fmt("usd0").red_negatives()
        """
        return self._with(red_negatives=value)

    def neg(self, color: str | None = None, bracket: bool = False) -> Self:
        """Style negative values: colour them, and optionally bracket them.

        :param color: the colour for negative values (default the theme's
            negative colour — red).
        :param bracket: wrap negatives in parentheses, accounting-style, so
            ``-$1,234`` becomes ``($1,234)``.

        Example::

            col.currency("profit").neg()
            col.currency("profit").neg(color="#b91c1c", bracket=True)
        """
        return self._with(red_negatives=True, negative_color=color, bracket_negatives=bracket or None)

    def rotate_title(self, value: Rotation) -> Self:
        """Rotate the header: ``"vertical"`` or an angle in degrees.

        Example::

            col.number("q1").rotate_title("vertical")
        """
        return self._with(rotate_title=value)

    # -- placement and metadata ------------------------------------------
    def group(self, value: str | Sequence[str]) -> Self:
        """Place the column under a header group.

        A string is one level; a sequence nests (``["Root", "Sub"]``). Dotted
        column names are grouped automatically, so this overrides that.

        Example::

            col.number("revenue").group("Financials")
        """
        return self._with(column_group=value)

    def subcolumn(self, value: str) -> Self:
        """Give the column a shared sub-header (the ``X`` in an ``X value`` pair).

        Example::

            col.number("gdp_2020").fmt("usd0").subcolumn("GDP")
        """
        return self._with(subcolumn_group=value)

    def repeat_values(self, value: bool = True) -> Self:
        """Repeat a grouped value on every row instead of only the first.

        Example::

            col.text("category").repeat_values()
        """
        return self._with(repeat_values=value)

    def hide(self, value: bool = True) -> Self:
        """Hide the column, keeping it available for ``sort_by`` / links.

        Example::

            col.number("id").hide()
        """
        return self._with(hide=value)

    def info(self, text: str) -> Self:
        """Set the column's description (shown behind the ⓘ and as the header ``title``).

        Example::

            col.percent("share").info("Share of total sales")
        """
        return self._with(info=text)

    def footnote(self, column: str) -> Self:
        """Attach a footnote column, rendered as a marker next to the value.

        Example::

            col.text("estimate").footnote("estimate_note")
        """
        return self._with(footnote=_field(column))

    def sort_by(self, column: str) -> Self:
        """Sort this column by another column's values.

        The target may be hidden or not otherwise shown.

        Example::

            col.sparkline("trend").sort_by("growth")
        """
        return self._with(sort_by=_field(column))

    def highlight(self, color: str) -> Self:
        """Shade the column with a background colour band.

        Wins over row shading; the group header is filled only when every
        column it spans shares the highlight.

        Example::

            col.number("rating").highlight("#fef3c7")
        """
        return self._with(highlight=color)

    def cell_style(
        self,
        *,
        background: str | None = None,
        color: str | None = None,
        border: str | None = None,
        padding: str | None = None,
    ) -> Self:
        """Style the cell chrome, independently of any marks on it.

        :param background: a colour, or ``"@column"`` for a per-row colour.
        :param color: the text colour.
        :param border: a CSS ``border`` value.
        :param padding: a CSS ``padding`` value.

        Explicit matching ``rules`` still win for the same property.

        Example::

            col.bar("change").cell_style(background="@change_colour")
        """
        if isinstance(background, str) and background.startswith("@"):
            background, background_column = None, background[1:]
        else:
            background_column = None
        return self._with(
            cell_style=_clean(
                background=background,
                background_column=background_column,
                color=color,
                border=border,
                padding=padding,
            )
            or None
        )

    # -- cell content ----------------------------------------------------
    def markdown(self) -> Self:
        """Render the cell text as Markdown.

        Example::

            col.text("summary").markdown()
        """
        return self._with(markdown=True)

    def html(self) -> Self:
        """Render the cell text as raw HTML.

        Example::

            col.text("badge").html()
        """
        return self._with(html=True)

    def icons(self, map: Mapping[str, str]) -> Self:
        """Map each category to a glyph or image URL.

        :param map: category → glyph (e.g. ``"▲"``) or image URL/data-URI.

        Example::

            col.text("signal").icons({"buy": "▲", "sell": "▼", "hold": "●"})
        """
        return self._with(icon_map={str(key): value for key, value in map.items()})

    def link(self, column: str | None = None, *, label: str | None = None, new_tab: bool = False) -> Self:
        """Turn the cell into a hyperlink.

        :param column: the column holding the URL (defaults to this column).
        :param label: fixed link text (defaults to the cell value).
        :param new_tab: open the link in a new tab.

        Example::

            col.text("title").link("url", label="Open", new_tab=True)
        """
        return self._with(
            **_clean(link=_field(column) or self._name, link_label=label, link_new_tab=new_tab or None),
        )

    def image(
        self,
        column: str | None = None,
        *,
        height: float | None = None,
        width: float | None = None,
        alt: str | None = None,
    ) -> Self:
        """Render the cell as an image.

        :param column: the column holding the image URL (defaults to this column).
        :param height: image height in pixels.
        :param width: image width in pixels.
        :param alt: alt text column.

        Example::

            col.text("poster").image(height=48)
        """
        return self._with(
            image=_field(column) or self._name, **_merge_options("image_options", height=height, width=width, alt=alt)
        )

    def logo(self, column: str | None = None, *, height: float | None = None) -> Self:
        """Render the cell as a logo (an image sized to the row height).

        Example::

            col.text("team").logo(height=20)
        """
        return self._with(logo=_field(column) or self._name, **_merge_options("logo_options", height=height))

    def template(self, value: str, **formats: str) -> Self:
        """Render the cell with a template, e.g. ``"{last}, {first}"``.

        Extra keyword arguments are format codes for the referenced columns.

        Example::

            col.text("last_name").template("{last}, {first}", sales="usd0")
        """
        return self._with(template=value, template_fmt=_clean(**formats) or None)

    # -- visualizations --------------------------------------------------
    def viz(self, kind: str, **options: Any) -> Self:
        """Set a visualisation by name, passing its options.

        Prefer mark factories for bars and typed helpers (:meth:`color`, :meth:`delta`,
        :meth:`sparkline`, :meth:`chip`).

        Example::

            col.number("sales").viz("color", color_scale="green")
        """
        return self._with(viz=kind, **{f"{kind}_options": _clean(**options)})

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
    ) -> Self:
        """Shade each cell with a background colour for its value.

        :param scale: a named preset (``"green"``, ``"blue"``, ``"red"``,
            ``"orange"``, ``"purple"``, ``"grey"``/``"gray"``), a list of colours,
            or ``"@column"`` to colour each cell from that column's values.
        :param conditional_colors: a rule column name supplying per-row colours.
        :param scale_column: take the scale range from another column.
        :param min: lower bound of the scale.
        :param max: upper bound of the scale.
        :param midpoint: midpoint for a diverging scale.

        Example::

            col.number("rating").color(scale="green", min=6, max=10)
            col.chip("status").color(scale="@status_color")
        """
        if isinstance(scale, str) and scale.startswith("@"):
            # `scale="@column"` colours each cell from that column's values.
            conditional_colors, scale = scale[1:], None
        return self._with(
            viz="color",
            **_merge_options(
                "color_options",
                color_scale=scale,
                color_stops=stops,
                conditional_colors=_field(conditional_colors),
                scale_column=_field(scale_column),
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
    ) -> Self:
        """Show a change indicator (▲/▼) next to the value.

        :param down_is_good: invert the meaning (red up, green down).
        :param neutral_range: a ``"lo:hi"`` string, a pair, or ``±value`` for a
            grey-dash neutral band.
        :param chip: render as a chip instead of plain text.
        :param show_value: show or hide the number.
        :param show_symbol: show or hide the ▲/▼ symbol.
        :param symbol_position: ``"left"`` (default) or ``"right"``.

        Example::

            col.percent("change").delta(down_is_good=False, neutral_range="0.05")
        """
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
        type: SparklineType | None = None,
        x: str | None = None,
        y: str | None = None,
        color: str | None = None,
        fit_to_data: bool | None = None,
        reference: float | None = None,
        reference_color: str | None = None,
        y_fmt: str | None = None,
        width: float | None = None,
        height: float | None = None,
        markers: bool | str | None = None,
        marker_color: str | None = None,
        signed: bool | None = None,
        delta: bool | None = None,
        steady: tuple[float, float] | None = None,
        color_scale: str | Sequence[str] | None = None,
        color_domain: tuple[float, float] | None = None,
    ) -> Self:
        """Draw the cell's array as a compact chart, including up/steady/down changes.

        :param type: ``"line"`` (default), ``"area"``, ``"bar"``, ``"points"`` or ``"change"``.
        :param x: field for the x values.
        :param y: field for the y values.
        :param color: stroke/fill colour.
        :param fit_to_data: scale to the data's range rather than zero.
        :param reference: horizontal reference and area/bar origin (e.g. 1 for 100%).
        :param reference_color: reference line colour.
        :param y_fmt: format code for the tooltip y value.
        :param width: chart width (the viewBox, in pixels).
        :param height: chart height (the viewBox, in pixels).
        :param markers: draw a marker at every point, or ``"ends"`` for the endpoints.
        :param marker_color: marker colour; a per-point ``color`` key wins.
        :param signed: split an area fill at the zero baseline into up/down colours.
        :param delta: for change sparklines, compare adjacent observations. The first
            slot and comparisons beside missing observations stay blank. Default False.
        :param steady: inclusive change interval rendered at the center; defaults to (0, 0).
        :param color_scale: optional change gradient (named palette or color list).
            The whole steady interval maps to the palette midpoint.
        :param color_domain: fixed change gradient endpoints, containing the steady
            interval. Otherwise all matching rows supply shared bounds.

        Example::

            col.sparkline("trend", type="area", color="#0ea5e9")
        """
        options = {
            **dict(self._spec.get("sparkline_options") or {}),
            **_clean(
                type=type,
                x=x,
                y=y,
                color=color,
                fit_to_data=fit_to_data,
                reference=reference,
                reference_color=reference_color,
                y_fmt=y_fmt,
                width=width,
                height=height,
                markers=markers,
                marker_color=marker_color,
                signed=signed,
                delta=delta,
                steady=steady,
                color_scale=color_scale,
                color_domain=color_domain,
            ),
        }
        return self._with(viz="sparkline", sparkline_options=normalize_sparkline_options(options))

    def chip(
        self,
        *,
        min_width: Any = None,
        conditional_colors: str | None = None,
        scale: Any = None,
        stops: Any = None,
        scale_column: str | None = None,
        min: float | None = None,
        max: float | None = None,
        midpoint: float | None = None,
    ) -> Self:
        """Render the value in a rounded "chip".

        The fill follows the same rules as :meth:`color`.

        :param min_width: minimum chip width (a number of pixels or a CSS length).
        :param conditional_colors: a rule column name supplying per-row colours.
        :param scale: a colour scale for numeric chips, or ``"@column"`` to colour
            each chip from that column's values.
        :param stops: explicit colour stops.
        :param scale_column: take the scale range from another column.
        :param min: lower bound of the colour scale.
        :param max: upper bound of the colour scale.
        :param midpoint: midpoint for a diverging scale.

        Example::

            col.chip("status", min_width=72)
            col.number("aqi").chip(scale="red", min=0, max=250)
            col.chip("status").chip(scale="@status_color")
        """
        if isinstance(scale, str) and scale.startswith("@"):
            conditional_colors, scale = scale[1:], None
        changes: dict[str, Any] = {"viz": "chip"}
        chip = _clean(min_width=min_width)
        if chip:
            changes["chip_options"] = {**dict(self._spec.get("chip_options") or {}), **chip}
        color = _clean(
            conditional_colors=_field(conditional_colors),
            color_scale=scale,
            color_stops=stops,
            scale_column=_field(scale_column),
            min=min,
            max=max,
            midpoint=midpoint,
        )
        if color:
            changes["color_options"] = {**dict(self._spec.get("color_options") or {}), **color}
        return self._with(**changes)

    def symbols(
        self,
        *,
        symbol: str | None = None,
        shape: Literal["square", "rounded", "circle"] | None = None,
        empty: str | None = None,
        max: int | None = None,
        image: str | None = None,
        color: str | None = None,
        empty_color: str | None = None,
        size: float | None = None,
        gap: float | None = None,
    ) -> Self:
        """Render the value as that many repeated symbols — glyphs, emoji or images.

        :param symbol: the filled glyph (default ``"●"``).
        :param shape: draw a CSS box instead of a glyph — ``"square"``,
            ``"rounded"`` or ``"circle"`` — for a pixel-exact, font-independent mark.
        :param empty: the glyph for the unfilled slots (used with ``max``).
        :param max: draw this many slots — ``value`` filled, the rest ``empty``;
            omit to draw exactly ``value`` repeats.
        :param image: an image URL to repeat instead of a glyph.
        :param color: the filled colour.
        :param empty_color: the unfilled colour.
        :param size: the glyph size (or box side), in ``em``.
        :param gap: the space between glyphs, in ``em``.

        Example::

            col.number("twice").symbols(symbol="■", color="#2EC1D3")
            col.number("medals").symbols(shape="square", color="#f0a500", size=0.8)
            col.number("rating").symbols(symbol="★", empty="☆", max=5, color="#f59e0b")
        """
        return self._with(
            viz="symbols",
            **_merge_options(
                "symbol_options",
                symbol=symbol,
                shape=shape,
                empty=empty,
                max=max,
                image=image,
                color=color,
                empty_color=empty_color,
                size=size,
                gap=gap,
            ),
        )

    # ----------------------------------------------------------- output ---
    def to_config(self) -> dict[str, Any]:
        """Validate and return the plain column definition (the wire format).

        Every column is validated when the table is built; call this to check a
        spec on its own.

        Example::

            col.number("sales").fmt("usd0").to_config()
        """
        return _normalize_column_options(dict(self))


class ColumnGroup(Sequence[Column]):
    """An immutable group of columns that share a header label.

    Returned by :func:`subcolumns` (a shared leaf header) and :func:`group` (a
    spanner). It is a :class:`~collections.abc.Sequence`, so it can be splatted
    into ``columns=[...]`` (``*col.subcolumns("Latest", [...])``) and is also
    accepted directly there, where the table flattens it.
    """

    __slots__ = ("_kind", "_label", "_members")

    def __init__(self, kind: str, label: str | Sequence[str], members: Sequence[Column]) -> None:
        self._kind = kind
        self._label = label
        self._members = tuple(members)

    @property
    def kind(self) -> str:
        """``"subcolumns"`` or ``"group"``."""
        return self._kind

    @property
    def label(self) -> str | Sequence[str]:
        """The shared header label."""
        return self._label

    @property
    def members(self) -> tuple[Column, ...]:
        """The grouped columns."""
        return self._members

    def __getitem__(self, index: int | slice) -> Any:
        """Return the member at ``index``."""
        return self._members[index]

    def __len__(self) -> int:
        """The number of members."""
        return len(self._members)

    def __repr__(self) -> str:
        """A readable ``col.subcolumns('label', [...])`` form."""
        label = self._label if isinstance(self._label, str) else ".".join(self._label)
        members = ", ".join(repr(member) for member in self._members)
        return f"col.{self._kind}({label!r}, [{members}])"


def _as_column(item: Any) -> Column:
    """Coerce a column name, mapping or :class:`Column` to a ``Column``."""
    if isinstance(item, Column):
        return item
    if isinstance(item, str):
        return Column(item)
    if isinstance(item, Mapping):
        name = item.get("name")
        if not name:
            raise ValueError("a column mapping needs a 'name'")
        return Column(str(name), {key: value for key, value in item.items() if key != "name"})
    raise TypeError(f"expected a column name, mapping or col.* column, got {type(item).__name__}")


def _members(items: Iterable[Any]) -> list[Column]:
    """Return the columns in ``items``, flattening any nested groups."""
    result: list[Column] = []
    for item in items:
        if isinstance(item, ColumnGroup):
            result.extend(item.members)
        else:
            result.append(_as_column(item))
    return result


def _merge_options(key: str, **values: Any) -> dict[str, Any]:
    """Build a nested options dict, dropping ``None`` values."""
    options = _clean(**values)
    return {key: options} if options else {}


def _percent_code(whole: bool, decimals: int | None) -> str:
    """Map the percent kind to a format code.

    ``whole=False`` (a proportion, ``0.15``) uses the ``pct`` presets, which
    multiply by 100. ``whole=True`` (an already-percent value, ``15``) needs a
    literal-percent custom code.
    """
    if not whole:
        if decimals is None:
            return "pct"
        if not 0 <= decimals <= 3:
            raise ValueError(f"percent decimals must be 0-3, got {decimals}")
        return f"pct{decimals}"
    places = 1 if decimals is None else decimals
    if places < 0:
        raise ValueError(f"percent decimals must be >= 0, got {places}")
    digits = "." + "0" * places if places else ""
    return f'0{digits}"%"'


def _currency_code(code: str, decimals: int | None) -> str:
    """Map the currency kind to a format code, validating the currency."""
    normalized = code.lower()
    if normalized not in CURRENCY_CODES:
        raise ValueError(f"unknown currency code {code!r}; choose one of {', '.join(CURRENCY_CODES)}")
    if decimals is None:
        return normalized
    if not 0 <= decimals <= 2:
        raise ValueError(f"currency decimals must be 0-2, got {decimals}")
    return f"{normalized}{decimals}"


# ------------------------------------------------------------------ factories ---
def _column(name: str, type_name: str, **spec: Any) -> Column:
    """Build a ``Column`` from ``name``, a type and cleaned options."""
    alias(spec, "fmt", "format")
    return Column(name, {"type": type_name, **_clean(**spec)})


def auto(name: str, **overrides: Any) -> Column:
    """Include a column with its **inferred** definition, then refine it.

    Use it to list or reorder columns without restating what they are: the type,
    format, alignment and ``info`` come from the data (Arrow schema, DuckDB
    comment, …), exactly as if the column had not been listed, and anything you
    chain overrides that.

    :param name: the source column name.
    :param overrides: any column options, applied over the inferred definition.

    Example::

        columns=[
            col.text("city"),
            col.auto("gdp").color(scale="blue"),    # inferred number + shading
            col.auto("year").group("Time"),
        ]

    It is also the right value in ``column_config`` when you want to change one
    thing about a column: ``column_config={"gdp": col.auto("gdp").fmt("usd0")}``.
    """
    alias(overrides, "fmt", "format")
    return Column(name, _clean(**overrides))


def merge(name: str, spec: Mapping[str, Any]) -> Column:
    """Name a derived column built by a ``cols_merge_*`` helper.

    The ``cols_merge_*`` helpers return a partial definition (a template and the
    formats of its fields) with no name, so this gives it one and lets it join
    ``columns=[...]``.

    :param name: the name of the rendered column.
    :param spec: the mapping returned by ``cols_merge_range`` /
        ``cols_merge_uncert`` / ``cols_merge_n_pct``.

    Example::

        columns=[
            col.auto("low").hide(),
            col.auto("high").hide(),
            col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
        ]
    """
    return Column(name, {key: value for key, value in spec.items() if key != "name"})


def text(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A text column.

    :param name: the source column name.
    :param title: header text (defaults to a formatted column name).

    Example::

        col.text("city")
        col.text("first_name").title("First name")
    """
    return _column(name, "string", title=title, **extra)


def number(
    name: str,
    *,
    format: str | None = None,
    fmt: str | None = None,
    align: Align | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A number column with auto-scaling formatting.

    Use :func:`integer`, :func:`percent` or :func:`currency` for those kinds.

    :param name: the source column name.
    :param fmt: an explicit format code instead of the auto format.
    :param align: text alignment.
    :param title: header text.

    Example::

        col.number("sales")
        col.number("score", fmt="num2")
    """
    return _column(name, "number", fmt=format_code(format, fmt), align=align, title=title, **extra)


def integer(
    name: str, *, format: str | None = None, fmt: str | None = None, title: str | None = None, **extra: Any
) -> Column:
    """A whole-number column (counts, ids), formatted ``num0``.

    :param name: the source column name.
    :param fmt: an explicit format code instead of ``"num0"``.
    :param title: header text.

    Example::

        col.integer("orders")
    """
    return _column(name, "number", fmt=format_code(format, fmt) or "num0", title=title, **extra)


def percent(
    name: str,
    *,
    whole: bool = False,
    decimals: int | None = None,
    format: str | None = None,
    fmt: str | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A percentage column.

    :param name: the source column name.
    :param whole: ``False`` (default) for a proportion (``0.153`` → 15.3%);
        ``True`` for an already-percent value (``15.3`` → 15.3%).
    :param decimals: decimal places; omit to let the renderer choose a scale.
    :param fmt: an explicit format code instead of the derived one.
    :param title: header text.

    Example::

        col.percent("share")                       # 0.153  -> 15.3%
        col.percent("rate", whole=True)            # 15.3   -> 15.3%
        col.percent("share", decimals=2)
    """
    return _column(
        name,
        "number",
        fmt=format_code(format, fmt) or _percent_code(whole, decimals),
        title=title,
        **extra,
    )


def currency(
    name: str,
    *,
    code: str = "usd",
    decimals: int | None = None,
    format: str | None = None,
    fmt: str | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A money column.

    :param name: the source column name.
    :param code: one of :data:`CURRENCY_CODES` (``"usd"``, ``"eur"``, …).
    :param decimals: ``0``–``2`` decimal places; omit to let the renderer choose.
    :param fmt: an explicit format code instead of the derived one.
    :param title: header text.

    Example::

        col.currency("sales")                      # $12,400   (auto scale)
        col.currency("price", code="eur", decimals=2)   # €12.35
    """
    return _column(
        name,
        "number",
        fmt=format_code(format, fmt) or _currency_code(code, decimals),
        title=title,
        **extra,
    )


def date(
    name: str,
    *,
    format: str | None = None,
    fmt: str | None = None,
    relative: Relative | None = None,
    align: Align | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A date column (no time of day).

    :param name: the source column name.
    :param fmt: a date format code (``"yyyy"``, ``"mmm-yy"``, ``"longdate"``…).
    :param relative: render relative to now — ``True`` for an automatic unit or a
        unit such as ``"day"`` (e.g. ``"3 days ago"``).
    :param align: text alignment.
    :param title: header text.

    Example::

        col.date("order_date")
        col.date("due_date", relative="day")
    """
    return _column(name, "date", fmt=format_code(format, fmt), relative=relative, align=align, title=title, **extra)


def time(
    name: str,
    *,
    format: str | None = None,
    fmt: str | None = None,
    relative: Relative | None = None,
    align: Align | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A time-of-day column.

    :param name: the source column name.
    :param fmt: a time format code (default ``"hms"``); other presets include
        ``"HH:MM"``-style custom codes.
    :param relative: render relative to now — ``True`` for an automatic unit or a
        unit such as ``"hour"`` (e.g. ``"2 hours ago"``).
    :param align: text alignment.
    :param title: header text.

    Example::

        col.time("opened_at")
    """
    return _column(
        name,
        "date",
        fmt=format_code(format, fmt) or "hms",
        relative=relative,
        align=align,
        title=title,
        **extra,
    )


def datetime(
    name: str,
    *,
    format: str | None = None,
    fmt: str | None = None,
    relative: Relative | None = None,
    align: Align | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A date-and-time column.

    :param name: the source column name.
    :param fmt: a format code (default ``"datetime"`` → ``yyyy-mm-dd HH:MM:SS``).
    :param relative: render relative to now — ``True`` for an automatic unit or a
        unit such as ``"minute"`` (e.g. ``"5 minutes ago"``).
    :param align: text alignment.
    :param title: header text.

    Example::

        col.datetime("created_at")
        col.datetime("updated_at").relative()
    """
    return _column(
        name,
        "date",
        fmt=format_code(format, fmt) or "datetime",
        relative=relative,
        align=align,
        title=title,
        **extra,
    )


def boolean(
    name: str,
    *,
    title: str | None = None,
    true_text: str | None = None,
    false_text: str | None = None,
    true_symbol: str | None = None,
    false_symbol: str | None = None,
    **extra: Any,
) -> Column:
    """A true/false column, optionally written as a symbol and/or label.

    :param true_text: label for a true value (default ``"true"``).
    :param false_text: label for a false value (default ``"false"``).
    :param true_symbol: symbol shown before a true label (e.g. ``"✓"``).
    :param false_symbol: symbol shown before a false label (e.g. ``"✗"``).

    Example::

        col.boolean("is_active", true_symbol="✓", false_symbol="✗",
                    true_text="Active", false_text="Inactive")
    """
    return _column(
        name,
        "boolean",
        title=title,
        boolean_options=_clean(
            true_text=true_text,
            false_text=false_text,
            true_symbol=true_symbol,
            false_symbol=false_symbol,
        )
        or None,
        **extra,
    )


def icons(
    name: str,
    *,
    map: Mapping[str, str],
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A categorical column drawn as an icon per category.

    :param map: category → glyph (e.g. ``"▲"``) or image URL/data-URI; an
        unmapped value falls back to its text.

    Example::

        col.icons("signal", map={"buy": "▲", "sell": "▼", "hold": "●"})
    """
    return _column(name, "string", title=title, icon_map=dict(map), **extra)


def array(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A list-valued column (usually paired with :func:`sparkline`).

    Example::

        col.array("trend").sparkline(type="bar")
    """
    return _column(name, "array", title=title, **extra)


def flag(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A country/region column rendered as a flag.

    The value must be an ISO 3166 alpha-2 or alpha-3 code; unknown codes pass
    through unchanged.

    Example::

        col.flag("country")
    """
    return _column(
        name,
        "string",
        fmt=format_code(extra.pop("format", None), extra.pop("fmt", None)) or "flag",
        title=title,
        **extra,
    )


def markdown(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A column rendered as Markdown.

    Example::

        col.markdown("summary")
    """
    return _column(name, "string", title=title, markdown=True, **extra)


def html(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A column rendered as raw HTML.

    Example::

        col.html("badge")
    """
    return _column(name, "string", title=title, html=True, **extra)


def link(
    name: str, *, label: str | None = None, new_tab: bool = False, title: str | None = None, **extra: Any
) -> Column:
    """A hyperlink column.

    :param name: the column holding the URL (use :meth:`Column.link` to link to a
        different column).
    :param label: fixed link text.
    :param new_tab: open in a new tab.
    :param title: header text.

    Example::

        col.link("url", label="Open", new_tab=True)
    """
    return _column(name, "string", title=title, link=name, link_label=label, link_new_tab=new_tab or None, **extra)


def url(
    name: str, *, label: str | None = None, new_tab: bool = False, title: str | None = None, **extra: Any
) -> Column:
    """Alias for :func:`link`.

    Example::

        col.url("page", new_tab=True)
    """
    return link(name, label=label, new_tab=new_tab, title=title, **extra)


def image(
    name: str, *, height: float | None = None, width: float | None = None, alt: str | None = None, **extra: Any
) -> Column:
    """An image column.

    :param name: the column holding the image URL.
    :param height: image height in pixels.
    :param width: image width in pixels.
    :param alt: alt-text column.

    Example::

        col.image("poster", height=48)
    """
    return _column(
        name, "string", image=name, image_options=_clean(height=height, width=width, alt=alt) or None, **extra
    )


def logo(name: str, *, height: float | None = None, **extra: Any) -> Column:
    """A logo column (an image sized to the row).

    Example::

        col.logo("team", height=20)
    """
    return _column(name, "string", logo=name, logo_options=_clean(height=height) or None, **extra)


def color(name: str, *, title: str | None = None, **options: Any) -> Column:
    """A number column shaded by a colour scale.

    Shorthand for ``col.number(name).color(...)``. See :meth:`Column.color` for
    the options.

    Example::

        col.color("rating", scale="green", min=6, max=10)
    """
    return number(name, title=title).color(**options)


def sparkline(
    name: str,
    *,
    type: SparklineType = "line",
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    fit_to_data: bool | None = None,
    reference: float | None = None,
    reference_color: str | None = None,
    y_fmt: str | None = None,
    width: float | None = None,
    height: float | None = None,
    markers: bool | str | None = None,
    marker_color: str | None = None,
    signed: bool | None = None,
    delta: bool | None = None,
    steady: tuple[float, float] | None = None,
    color_scale: str | Sequence[str] | None = None,
    color_domain: tuple[float, float] | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """An array column drawn as a sparkline.

    :param name: the column holding the array.
    :param type: ``"line"`` (default), ``"area"``, ``"bar"``, ``"points"`` or ``"change"``.
    :param x: field for the x values.
    :param y: field for the y values.
    :param color: stroke/fill colour.
    :param fit_to_data: scale to the data's range rather than zero.
    :param reference: horizontal reference and area/bar origin (e.g. 1 for 100%).
    :param reference_color: reference line colour.
    :param y_fmt: format code for the tooltip y value.
    :param width: chart width (the viewBox, in pixels).
    :param height: chart height (the viewBox, in pixels).
    :param markers: draw a marker at every point (line/area too).
    :param signed: split an area fill at the zero baseline into up/down colours.
    :param delta: change-only adjacent differences; defaults to precomputed changes.
    :param steady: inclusive hold-steady interval for change rectangles (default 0..0).
    :param color_scale: named palette or color list for change magnitude.
    :param color_domain: fixed gradient endpoints; the steady interval anchors the midpoint.
    :param title: header text.

    See :meth:`Column.sparkline` for the same options on the chain.

    Example::

        col.sparkline("trend", type="area", x="date", y="trips", color="#53768a")
    """
    return array(name, title=title, **extra).sparkline(
        type=type,
        x=x,
        y=y,
        color=color,
        fit_to_data=fit_to_data,
        reference=reference,
        reference_color=reference_color,
        y_fmt=y_fmt,
        width=width,
        height=height,
        markers=markers,
        marker_color=marker_color,
        signed=signed,
        delta=delta,
        steady=steady,
        color_scale=color_scale,
        color_domain=color_domain,
    )


def chip(
    name: str,
    *,
    min_width: Any = None,
    conditional_colors: str | None = None,
    scale: Any = None,
    min: float | None = None,
    max: float | None = None,
    midpoint: float | None = None,
    **extra: Any,
) -> Column:
    """A text chip column.

    For a numeric chip use ``col.number("aqi").chip(scale=...)``.

    :param min_width: minimum chip width (pixels or a CSS length).
    :param conditional_colors: a rule column name supplying per-row colours.
    :param scale: a colour scale.
    :param min: lower bound of the colour scale.
    :param max: upper bound of the colour scale.
    :param midpoint: midpoint for a diverging scale.

    Example::

        col.chip("status", min_width=72)
    """
    return Column(name, {"type": "string", **_clean(**extra)}).chip(
        min_width=min_width,
        conditional_colors=conditional_colors,
        scale=scale,
        min=min,
        max=max,
        midpoint=midpoint,
    )


def delta(
    name: str, *, down_is_good: bool | None = None, neutral_range: Any = None, chip: bool | None = None, **extra: Any
) -> Column:
    """A number column shown as a change indicator.

    See :meth:`Column.delta` for the options; use :func:`percent` /
    :func:`currency` with ``.delta(...)`` to format the value.

    Example::

        col.delta("change", down_is_good=True, neutral_range="0.05")
    """
    return Column(name, {"type": "number", **_clean(**extra)}).delta(
        down_is_good=down_is_good,
        neutral_range=neutral_range,
        chip=chip,
    )


def symbols(
    name: str,
    *,
    symbol: str | None = None,
    shape: Literal["square", "rounded", "circle"] | None = None,
    empty: str | None = None,
    max: int | None = None,
    image: str | None = None,
    color: str | None = None,
    empty_color: str | None = None,
    size: float | None = None,
    gap: float | None = None,
    align: Align | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """A number shown as that many repeated symbols — glyphs, emoji or images.

    :param name: the numeric column holding the count.
    :param symbol: the filled glyph (default ``"●"``). ``"■"`` for squares, ``"★"``
        for stars, or any emoji.
    :param shape: draw a CSS box instead of a glyph — ``"square"``, ``"rounded"`` or
        ``"circle"`` — for a pixel-exact mark that does not depend on the font.
    :param empty: the glyph for the unfilled slots, used with ``max`` (e.g. ``"☆"``).
    :param max: draw this many slots — ``value`` filled, the rest ``empty``; omit to
        draw exactly ``value`` repeats.
    :param image: an image URL to repeat instead of a glyph.
    :param color: the filled colour.
    :param empty_color: the unfilled colour.
    :param size: the glyph size (or box side), in ``em``.
    :param gap: the space between glyphs, in ``em``.
    :param align: text alignment (``"left"``, ``"right"`` or ``"center"``).
    :param title: header text.

    Example::

        col.symbols("twice", symbol="■", color="#2EC1D3")
        col.symbols("medals", shape="square", color="#f0a500", size=0.8)
    """
    return number(name, align=align, title=title, **extra).symbols(
        symbol=symbol,
        shape=shape,
        empty=empty,
        max=max,
        image=image,
        color=color,
        empty_color=empty_color,
        size=size,
        gap=gap,
    )


def repeat(name: str, **options: Any) -> Column:
    """Alias for :func:`symbols` — repeat the value as symbols.

    Example::

        col.repeat("thrice", symbol="■", color="#2EC1D3")
    """
    return symbols(name, **options)


def rating(
    name: str,
    *,
    max: int = 5,
    symbol: str = "★",
    empty: str = "☆",
    color: str = "#f59e0b",
    **options: Any,
) -> Column:
    """A star rating: ``max`` slots, with ``value`` of them filled.

    Example::

        col.rating("stars", max=5)
        col.rating("score", max=10, color="#eab308")
    """
    return symbols(name, symbol=symbol, empty=empty, max=max, color=color, **options)


# ------------------------------------------------------------------- groups ---
def subcolumns(
    label: str,
    columns: Iterable[Any],
    *,
    group: str | Sequence[str] | None = None,
    highlight: str | None = None,
) -> ColumnGroup:
    """Give a group of columns one shared leaf header.

    Members are labelled with ``label`` and are therefore contiguous by
    construction — you cannot forget the label on one of them or misspell it.

    :param label: the shared header text.
    :param columns: the members (``col.*`` columns, names or mappings); may
        nest another group.
    :param group: an enclosing spanner header for the members.
    :param highlight: a background colour for the members.

    Example::

        col.subcolumns("Latest", [
            col.number("gdp").fmt("num1").red_negatives(),
            col.text("gdp_period").font_color("#808080"),
        ])

    The result goes straight into ``columns=[...]``::

        EvidentialTable(rows, columns=[
            col.text("country"),
            col.subcolumns("Latest", [col.number("gdp"), col.text("gdp_period")]),
        ])
    """
    members = [
        column._with(subcolumn_group=label, column_group=group, highlight=highlight) for column in _members(columns)
    ]
    return ColumnGroup("subcolumns", label, members)


def group(
    label: str | Sequence[str],
    columns: Iterable[Any],
    *,
    highlight: str | None = None,
) -> ColumnGroup:
    """Put a group of columns under a spanner header.

    The builder counterpart of ``column_groups={label: [...]}``: each member gets
    ``column_group=label``, so the group is named once and is contiguous by
    construction.

    :param label: the spanner text; a sequence nests (``["Root", "Sub"]``).
    :param columns: the members (``col.*`` columns, names or mappings).
    :param highlight: a background colour for the members.

    Example::

        col.group("Economy", [
            col.number("inflation"),
            col.number("unemployment"),
        ], highlight="#eef2ff")
    """
    members = [column._with(column_group=label, highlight=highlight) for column in _members(columns)]
    return ColumnGroup("group", label, members)
