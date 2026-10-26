# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Table typography: readable by default, not over-styled.

Follows the principles in Richard Rutter's "Web Typography: Tables":
left-align text, right-align numbers, match headings to data, align to the
decimal, use tabular numerals, don't stretch the table, and keep furniture to a
minimum.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col

    return EvidentialTable, col, mo


@app.cell
def _(mo):
    mo.md("""
    # Table typography

    | Principle | How |
    | --- | --- |
    | Left-align text, right-align numbers | alignment defaults by column type |
    | Match headings to their data | header alignment follows the column |
    | Align to the decimal point | `align_decimals=True` (pads to a common precision) |
    | Tabular lining numerals | `lining-nums tabular-nums` (default); `figure_style` overrides |
    | Don't stretch the table | `stretch=False` sizes columns to their content |
    | Keep furniture to a minimum | `row_lines=False`, no fills, no frame |
    | Caption / provenance | `caption="..."` |
    """)
    return


@app.cell
def _():
    rows = [
        {"item": "Widget", "quantity": 1200, "unit_price": 3.5, "total": 4200.0, "share": 0.4500},
        {"item": "Gadget", "quantity": 85, "unit_price": 12.25, "total": 1041.25, "share": 0.1115},
        {"item": "Gizmo", "quantity": 300, "unit_price": 7.125, "total": 2137.5, "share": 0.2289},
        {"item": "Doohickey", "quantity": 7, "unit_price": 0.5, "total": 3.5, "share": 0.0004},
        {"item": "Sprocket", "quantity": 40, "unit_price": 99.0, "total": 3960.0, "share": 0.4242},
    ]
    return (rows,)


@app.cell
def _(EvidentialTable, col, mo, rows):
    mo.ui.anywidget(
        EvidentialTable(
            rows,
            title="Sales by item",
            caption="Figures are illustrative.",
            # don't stretch: size columns to their content
            stretch=False,
            # no rules or fills: alignment, spacing and grouping do the work
            row_lines=False,
            row_shading=False,
            # right-align numbers and pad to a common precision so the
            # decimal points line up down each column
            align_decimals=True,
            columns=[
                col.text("item"),
                col.integer("quantity"),
                col.number("unit_price", fmt="num"),
                col.currency("total"),
                col.percent("share", decimals=1),
            ],
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Rotated headings

    Long headings over narrow columns can be set **vertically**
    (`rotate_titles="vertical"`, 90° counter-clockwise) or **obliquely**
    (`rotate_titles=-60`). Set `rotate_title` on a single column to override.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = [
        {"metric": "Revenue", **{month: 1000 + index * 137 for index, month in enumerate(months)}},
        {"metric": "Orders", **{month: 40 + index * 3 for index, month in enumerate(months)}},
    ]
    mo.ui.anywidget(
        EvidentialTable(
            monthly,
            title="Monthly figures — vertical headings",
            rotate_titles="vertical",
            stretch=False,
            row_lines=False,
            align_decimals=True,
            columns=[col.text("metric"), *[col.number(month, fmt="num0") for month in months]],
        )
    )
    return


@app.cell
def _(EvidentialTable, col, mo):
    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025"]
    per_quarter = [
        {"metric": "Revenue", "metric_fmt": "usd0", **{quarter: 120000 + index * 9000 for index, quarter in enumerate(quarters)}},
        {"metric": "Gross margin", "metric_fmt": "pct1", **{quarter: 0.4 + index * 0.01 for index, quarter in enumerate(quarters)}},
    ]
    mo.ui.anywidget(
        EvidentialTable(
            per_quarter,
            title="Oblique headings (−60°)",
            rotate_titles=-60,
            stretch=False,
            row_lines=False,
            columns=[
                col.text("metric"),
                col.auto("metric_fmt").hide(),
                *[col.number(quarter, fmt_column="@metric_fmt") for quarter in quarters],
            ],
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Numerals: lining vs lowercase

    ALA recommends **lining tabular** figures in tables. Here two typefaces are
    compared: Iowan Old Style (lining by default, with `onum`/`tnum`) and
    **Hoefler Text**, whose figures are lowercase (oldstyle) by default. Hoefler
    exposes its features through AAT rather than OpenType, so the style comes
    from the font itself rather than `font-variant-numeric`.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo):
    numerals = [
        {"glyphs": "Sequence", "lining": 1111111111, "lowercase": 1111111111},
        {"glyphs": "Mixed", "lining": 104729.54, "lowercase": 104729.54},
        {"glyphs": "Headings", "lining": 1234567890, "lowercase": 1234567890},
    ]
    mo.ui.anywidget(
        EvidentialTable(
            numerals,
            title="Numerals",
            stretch=False,
            row_lines=False,
            columns=[
                col.text("glyphs"),
                col.number(
                    "lining",
                    fmt="num2",
                    title="Lining — Iowan Old Style",
                    font="'Iowan Old Style', Georgia, serif",
                ),
                col.number(
                    "lowercase",
                    fmt="num2",
                    title="Lowercase — Georgia",
                    font="Georgia, serif",
                ).figure_style("default"),
            ],
        )
    )
    return


if __name__ == "__main__":
    app.run()
