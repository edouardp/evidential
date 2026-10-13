"""Implementation of the ``col`` column builder (private).

The public, completable surface is :mod:`evidential.col`, which re-exports only
the factory entry points. ``Column``, ``ColumnGroup``, ``CURRENCY_CODES`` and
the helpers live here so that ``col.`` completion shows only the kinds you can
build a column from.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal

from .configuration import ColumnOptions, Relative, validate_options

Align = Literal["left", "right", "center"]
Rotation = Literal["vertical"] | float

__all__ = [
    "CURRENCY_CODES",
    "Column",
    "ColumnGroup",
    "array",
    "auto",
    "bar",
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
    "image",
    "integer",
    "link",
    "logo",
    "markdown",
    "merge",
    "number",
    "percent",
    "sparkline",
    "subcolumns",
    "text",
    "time",
    "url",
]

#: Currency codes the formatter knows (``col.currency(code=...)``).
CURRENCY_CODES = ("usd", "eur", "gbp", "aud", "cad", "cny", "jpy", "inr", "krw", "ngn", "sek")


def _clean(**values: Any) -> dict[str, Any]:
    """Drop unset (``None``) values, keeping ``False`` and ``0``."""
    return {key: value for key, value in values.items() if value is not None}


class Column(Mapping[str, Any]):
    """An immutable column definition; every method returns a new ``Column``.

    Build one with a ``col.<kind>("name")`` factory and refine it by chaining::

        col.currency("sales", code="eur").title("Revenue").bar(color="#93c5fd")

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
    def _with(self, **changes: Any) -> Column:
        """Return a copy with ``changes`` applied; ``None`` values remove a key."""
        spec = dict(self._spec)
        for key, value in changes.items():
            if value is None:
                spec.pop(key, None)
            else:
                spec[key] = value
        return Column(self._name, spec)

    def _merge(self, key: str, **values: Any) -> Column:
        """Return a copy with ``values`` merged into the nested ``key`` options."""
        merged = {**dict(self._spec.get(key) or {}), **_clean(**values)}
        return self._with(**{key: merged or None})

    # -- labels and formatting -------------------------------------------
    def title(self, value: str) -> Column:
        """Override the column's header text.

        A ``"\\n"`` in the title forces a line break.

        Example::

            col.text("first_name").title("First name")
        """
        return self._with(title=value)

    def fmt(self, code: str) -> Column:
        """Set the value format code.

        ``code`` is a named preset (``"usd0"``, ``"pct1"``, ``"num0k"``, ``"yyyy"``,
        ``"flag"``…) or a raw Excel/``ssf`` pattern. This is the escape hatch for
        anything the column kinds do not cover.

        Example::

            col.number("sales").fmt("usd0")
        """
        return self._with(fmt=code)

    #: ``format`` reads better in a chain; ``fmt`` matches the option name.
    format = fmt

    def relative(self, value: Relative = True) -> Column:
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

    def fmt_column(self, column: str) -> Column:
        """Take the format code from another column, per row.

        The named column holds a format code; each cell is formatted with its own
        row's code (Evidence's ``fmtColumn``).

        Example::

            col.number("amount").fmt_column("row_fmt")
        """
        return self._with(fmt_column=column)

    def total_fmt(self, code: str) -> Column:
        """Format the total row differently from the cells.

        Example::

            col.number("sales").fmt("usd0").total_fmt("usd2")
        """
        return self._with(total_fmt=code)

    def subtotal_fmt(self, code: str) -> Column:
        """Format subtotal rows differently from the cells.

        Example::

            col.number("sales").fmt("usd0").subtotal_fmt("usd1")
        """
        return self._with(subtotal_fmt=code)

    def align(self, value: Align) -> Column:
        """Set the text alignment: ``"left"``, ``"right"`` or ``"center"``.

        Numbers default to right and text to left.

        Example::

            col.text("year").align("center")
        """
        return self._with(align=value)

    def align_decimals(self, value: bool = True) -> Column:
        """Align the whole column on the decimal point.

        Example::

            col.number("price").fmt("usd2").align_decimals()
        """
        return self._with(align_decimals=value)

    def figure_style(self, value: str) -> Column:
        """Override the CSS ``font-variant-numeric`` for this column.

        The default is ``"lining-nums tabular-nums"``; pass e.g.
        ``"oldstyle-nums proportional-nums"``.

        Example::

            col.text("amount").figure_style("lining-nums proportional-nums")
        """
        return self._with(figure_style=value)

    def font(self, family: str) -> Column:
        """Set the CSS ``font-family`` for this column.

        Example::

            col.text("code").font("ui-monospace, monospace")
        """
        return self._with(font=family)

    def font_color(self, color: str) -> Column:
        """Set the cell text colour (any CSS colour).

        Example::

            col.number("change").font_color("#b91c1c")
        """
        return self._with(font_color=color)

    def wrap(self, value: bool = True) -> Column:
        """Allow (or forbid) the cell text to wrap onto several lines.

        Example::

            col.text("description").wrap()
        """
        return self._with(wrap=value)

    def null_text(self, text: str) -> Column:
        """Text to show for a NULL value (the default is the table's ``null_text``).

        Example::

            col.text("manager").null_text("—")
        """
        return self._with(null_text=text)

    def blank_below(self, value: float) -> Column:
        """Leave the cell blank when the value is below ``value``.

        Example::

            col.number("sales").blank_below(100)
        """
        return self._with(blank_below=value)

    def blank_above(self, value: float) -> Column:
        """Leave the cell blank when the value is above ``value``.

        Example::

            col.number("share").blank_above(1)
        """
        return self._with(blank_above=value)

    def blank(self, predicate: Any) -> Column:
        """Leave the cell blank when a rule matches.

        ``predicate`` is a rule name or expression, as understood by the rule
        engine (see ``docs`` on conditional rules).

        Example::

            col.number("delta").blank("delta == 0")
        """
        return self._with(blank=predicate)

    def red_negatives(self, value: bool = True) -> Column:
        """Colour negative values red.

        Example::

            col.number("profit").fmt("usd0").red_negatives()
        """
        return self._with(red_negatives=value)

    def rotate_title(self, value: Rotation) -> Column:
        """Rotate the header: ``"vertical"`` or an angle in degrees.

        Example::

            col.number("q1").rotate_title("vertical")
        """
        return self._with(rotate_title=value)

    # -- placement and metadata ------------------------------------------
    def group(self, value: str | Sequence[str]) -> Column:
        """Place the column under a header group.

        A string is one level; a sequence nests (``["Root", "Sub"]``). Dotted
        column names are grouped automatically, so this overrides that.

        Example::

            col.number("revenue").group("Financials")
        """
        return self._with(column_group=value)

    def subcolumn(self, value: str) -> Column:
        """Give the column a shared sub-header (the ``X`` in an ``X value`` pair).

        Example::

            col.number("gdp_2020").fmt("usd0").subcolumn("GDP")
        """
        return self._with(subcolumn_group=value)

    def repeat_values(self, value: bool = True) -> Column:
        """Repeat a grouped value on every row instead of only the first.

        Example::

            col.text("category").repeat_values()
        """
        return self._with(repeat_values=value)

    def hide(self, value: bool = True) -> Column:
        """Hide the column, keeping it available for ``sort_by`` / links.

        Example::

            col.number("id").hide()
        """
        return self._with(hide=value)

    def info(self, text: str) -> Column:
        """Set the column's description (shown behind the ⓘ and as the header ``title``).

        Example::

            col.percent("share").info("Share of total sales")
        """
        return self._with(info=text)

    def footnote(self, column: str) -> Column:
        """Attach a footnote column, rendered as a marker next to the value.

        Example::

            col.text("estimate").footnote("estimate_note")
        """
        return self._with(footnote=column)

    def sort_by(self, column: str) -> Column:
        """Sort this column by another column's values.

        The target may be hidden or not otherwise shown.

        Example::

            col.sparkline("trend").sort_by("growth")
        """
        return self._with(sort_by=column)

    def highlight(self, color: str) -> Column:
        """Shade the column with a background colour band.

        Wins over row shading; the group header is filled only when every
        column it spans shares the highlight.

        Example::

            col.number("rating").highlight("#fef3c7")
        """
        return self._with(highlight=color)

    # -- cell content ----------------------------------------------------
    def markdown(self) -> Column:
        """Render the cell text as Markdown.

        Example::

            col.text("summary").markdown()
        """
        return self._with(markdown=True)

    def html(self) -> Column:
        """Render the cell text as raw HTML.

        Example::

            col.text("badge").html()
        """
        return self._with(html=True)

    def link(self, column: str | None = None, *, label: str | None = None, new_tab: bool = False) -> Column:
        """Turn the cell into a hyperlink.

        :param column: the column holding the URL (defaults to this column).
        :param label: fixed link text (defaults to the cell value).
        :param new_tab: open the link in a new tab.

        Example::

            col.text("title").link("url", label="Open", new_tab=True)
        """
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
        """Render the cell as an image.

        :param column: the column holding the image URL (defaults to this column).
        :param height: image height in pixels.
        :param width: image width in pixels.
        :param alt: alt text column.

        Example::

            col.text("poster").image(height=48)
        """
        return self._with(
            image=column or self._name, **_merge_options("image_options", height=height, width=width, alt=alt)
        )

    def logo(self, column: str | None = None, *, height: float | None = None) -> Column:
        """Render the cell as a logo (an image sized to the row height).

        Example::

            col.text("team").logo(height=20)
        """
        return self._with(logo=column or self._name, **_merge_options("logo_options", height=height))

    def template(self, value: str, **formats: str) -> Column:
        """Render the cell with a template, e.g. ``"{last}, {first}"``.

        Extra keyword arguments are format codes for the referenced columns.

        Example::

            col.text("last_name").template("{last}, {first}", sales="usd0")
        """
        return self._with(template=value, template_fmt=_clean(**formats) or None)

    # -- visualizations --------------------------------------------------
    def viz(self, kind: str, **options: Any) -> Column:
        """Set a visualisation by name, passing its options.

        Prefer the typed helpers (:meth:`bar`, :meth:`color`, :meth:`delta`,
        :meth:`sparkline`, :meth:`chip`).

        Example::

            col.number("sales").viz("bar", color="#93c5fd")
        """
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
        """Show each value as an inline horizontal bar with its label.

        :param color: bar colour (default a light blue).
        :param negative_color: bar colour for negative values.
        :param fit_to_data: scale bars to the column's range rather than the max.
        :param hide_labels: show only the bar, not the value.
        :param background: track colour behind the bar.

        Example::

            col.number("sales").fmt("usd0").bar(color="#93c5fd", fit_to_data=True)
        """
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
        """Shade each cell with a background colour for its value.

        :param scale: named colour scale (e.g. ``"redgreen"``, ``"blues"``).
        :param stops: explicit colour stops.
        :param conditional_colors: a rule column name supplying per-row colours.
        :param scale_column: take the scale range from another column.
        :param min: lower bound of the scale.
        :param max: upper bound of the scale.
        :param midpoint: midpoint for a diverging scale.

        Example::

            col.number("rating").color(scale="redgreen", min=6, max=10)
        """
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
        type: Literal["line", "area", "bar"] | None = None,
        x: str | None = None,
        y: str | None = None,
        color: str | None = None,
        fit_to_data: bool | None = None,
        y_fmt: str | None = None,
        width: float | None = None,
        height: float | None = None,
    ) -> Column:
        """Draw the cell's array value as a small line/area/bar chart.

        :param type: ``"line"`` (default), ``"area"`` or ``"bar"``.
        :param x: field for the x values.
        :param y: field for the y values.
        :param color: stroke/fill colour.
        :param fit_to_data: scale to the data's range rather than zero.
        :param y_fmt: format code for the tooltip y value.
        :param width: chart width (the viewBox, in pixels).
        :param height: chart height (the viewBox, in pixels).

        Example::

            col.sparkline("trend", type="area", color="#0ea5e9")
        """
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
        stops: Any = None,
        scale_column: str | None = None,
        min: float | None = None,
        max: float | None = None,
        midpoint: float | None = None,
    ) -> Column:
        """Render the value in a rounded "chip".

        The fill follows the same rules as :meth:`color`.

        :param min_width: minimum chip width (a number of pixels or a CSS length).
        :param conditional_colors: a rule column name supplying per-row colours.
        :param scale: a colour scale for numeric chips.
        :param stops: explicit colour stops.
        :param scale_column: take the scale range from another column.
        :param min: lower bound of the colour scale.
        :param max: upper bound of the colour scale.
        :param midpoint: midpoint for a diverging scale.

        Example::

            col.chip("status", min_width=72)
            col.number("aqi").chip(scale="redgreen", min=0, max=250)
        """
        changes: dict[str, Any] = {"viz": "chip"}
        chip = _clean(min_width=min_width)
        if chip:
            changes["chip_options"] = {**dict(self._spec.get("chip_options") or {}), **chip}
        color = _clean(
            conditional_colors=conditional_colors,
            color_scale=scale,
            color_stops=stops,
            scale_column=scale_column,
            min=min,
            max=max,
            midpoint=midpoint,
        )
        if color:
            changes["color_options"] = {**dict(self._spec.get("color_options") or {}), **color}
        return self._with(**changes)

    # ----------------------------------------------------------- output ---
    def to_config(self) -> dict[str, Any]:
        """Validate and return the plain column definition (the wire format).

        Every column is validated when the table is built; call this to check a
        spec on its own.

        Example::

            col.number("sales").fmt("usd0").to_config()
        """
        config = {"name": self._name, **self._spec}
        validate_options(config, ColumnOptions, "column")
        return config


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
            col.auto("gdp").bar(color="#93c5fd"),   # inferred number + a bar
            col.auto("year").group("Time"),
        ]

    It is also the right value in ``column_config`` when you want to change one
    thing about a column: ``column_config={"gdp": col.auto("gdp").fmt("usd0")}``.
    """
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
    name: str, *, fmt: str | None = None, align: Align | None = None, title: str | None = None, **extra: Any
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
    return _column(name, "number", fmt=fmt, align=align, title=title, **extra)


def integer(name: str, *, fmt: str | None = None, title: str | None = None, **extra: Any) -> Column:
    """A whole-number column (counts, ids), formatted ``num0``.

    :param name: the source column name.
    :param fmt: an explicit format code instead of ``"num0"``.
    :param title: header text.

    Example::

        col.integer("orders")
    """
    return _column(name, "number", fmt=fmt or "num0", title=title, **extra)


def percent(
    name: str,
    *,
    whole: bool = False,
    decimals: int | None = None,
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
    return _column(name, "number", fmt=fmt or _percent_code(whole, decimals), title=title, **extra)


def currency(
    name: str,
    *,
    code: str = "usd",
    decimals: int | None = None,
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
    return _column(name, "number", fmt=fmt or _currency_code(code, decimals), title=title, **extra)


def date(
    name: str,
    *,
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
    return _column(name, "date", fmt=fmt, relative=relative, align=align, title=title, **extra)


def time(
    name: str,
    *,
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
    return _column(name, "date", fmt=fmt or "hms", relative=relative, align=align, title=title, **extra)


def datetime(
    name: str,
    *,
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
    return _column(name, "date", fmt=fmt or "datetime", relative=relative, align=align, title=title, **extra)


def boolean(name: str, *, title: str | None = None, **extra: Any) -> Column:
    """A true/false column.

    Example::

        col.boolean("is_active")
    """
    return _column(name, "boolean", title=title, **extra)


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
    return _column(name, "string", fmt="flag", title=title, **extra)


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


def bar(name: str, *, title: str | None = None, **options: Any) -> Column:
    """A number column shown as an inline bar.

    Shorthand for ``col.number(name).bar(...)``. See :meth:`Column.bar` for the
    options.

    Example::

        col.bar("sales", color="#93c5fd", fit_to_data=True)
    """
    return number(name, title=title).bar(**options)


def color(name: str, *, title: str | None = None, **options: Any) -> Column:
    """A number column shaded by a colour scale.

    Shorthand for ``col.number(name).color(...)``. See :meth:`Column.color` for
    the options.

    Example::

        col.color("rating", scale="redgreen", min=6, max=10)
    """
    return number(name, title=title).color(**options)


def sparkline(
    name: str,
    *,
    type: Literal["line", "area", "bar"] = "line",
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    fit_to_data: bool | None = None,
    y_fmt: str | None = None,
    width: float | None = None,
    height: float | None = None,
    title: str | None = None,
    **extra: Any,
) -> Column:
    """An array column drawn as a sparkline.

    :param name: the column holding the array.
    :param type: ``"line"`` (default), ``"area"`` or ``"bar"``.
    :param x: field for the x values.
    :param y: field for the y values.
    :param color: stroke/fill colour.
    :param fit_to_data: scale to the data's range rather than zero.
    :param y_fmt: format code for the tooltip y value.
    :param width: chart width (the viewBox, in pixels).
    :param height: chart height (the viewBox, in pixels).
    :param title: header text.

    See :meth:`Column.sparkline` for the same options on the chain.

    Example::

        col.sparkline("trend", type="area", x="date", y="trips", color="#53768a")
    """
    return array(name, title=title, **extra).sparkline(
        type=type, x=x, y=y, color=color, fit_to_data=fit_to_data, y_fmt=y_fmt, width=width, height=height
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
