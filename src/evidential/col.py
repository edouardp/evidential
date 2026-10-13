"""The ``col`` namespace: the entry points of the column fluent chain.

Only column *kinds* live here, so completion on ``col.`` shows exactly what you
can build a column from and nothing else::

    from evidential import col

    columns=[
        col.text("city"),
        col.currency("sales", code="usd").bar(color="#93c5fd"),
        col.percent("share"),
        col.integer("orders"),
        col.subcolumns("Latest", [col.number("gdp"), col.text("gdp_period")]),
    ]

Each factory names the column's **kind** and returns an immutable
:class:`~evidential.Column`; every chain method returns a new one, so a spec can
be built, reused and composed:

- labels and formatting: ``.title()``, ``.fmt()``/``.format()``, ``.align()``,
  ``.align_decimals()``, ``.figure_style()``, ``.font()``, ``.font_color()``,
  ``.wrap()``, ``.null_text()``, ``.blank()``/``.blank_below()``/``.blank_above()``,
  ``.red_negatives()``, ``.rotate_title()``
- placement and metadata: ``.group()``, ``.subcolumn()``, ``.repeat_values()``,
  ``.hide()``, ``.info()``, ``.footnote()``, ``.sort_by()``, ``.highlight()``
- cell content: ``.markdown()``, ``.html()``, ``.link()``, ``.image()``,
  ``.logo()``, ``.template()``
- visualisations: ``.viz()``, ``.bar()``, ``.color()``, ``.delta()``,
  ``.sparkline()``, ``.chip()``

``.fmt("…")`` is the escape hatch for a custom format code (``num0k``, date
codes, ``bytes``…). The result of :func:`subcolumns` / :func:`group` is a
sequence and goes straight into ``columns=[...]``.

A :class:`~evidential.Column` is a :class:`~collections.abc.Mapping`, so it is
accepted anywhere a column definition is — including
``column_config={"sales": col.currency("sales").bar(...)}``.
"""

from ._column import (
    array,
    auto,
    bar,
    boolean,
    chip,
    color,
    currency,
    date,
    datetime,
    delta,
    flag,
    group,
    html,
    image,
    integer,
    link,
    logo,
    markdown,
    number,
    percent,
    sparkline,
    subcolumns,
    text,
    time,
    url,
)

__all__ = [
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
    "number",
    "percent",
    "sparkline",
    "subcolumns",
    "text",
    "time",
    "url",
]
