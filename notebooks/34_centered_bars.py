# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Centred ("diverging") bars — `bar(center=True)`.

A zero centre line, the bar growing left (negative) or right (positive) by its
magnitude, and the value on the opposite side of the line: the shape The
Economist uses for its league-table-of-nations charts.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, mo, settings


@app.cell
def _(mo):
    mo.md("""
    # Centred (diverging) bars

    The plain bar fills from one edge. Add **`center=True`** and the bar is drawn
    against a **centre line** instead: it grows **right** for a positive value and
    **left** for a negative one, by how far the value sits from zero, and the value
    is placed on the **opposite side** of the line.

    ```python
    col.percent("gdp", whole=True, decimals=1).bar(center=True)
    ```

    Each side is scaled to `max(|min|, |max|)`, so a +5 and a −5 draw the same
    length. Colour follows the usual rule (`color`, `negative_color`).

    The data below is **illustrative**, in the style of The Economist's league
    table of nations.
    """)
    return


@app.cell
def _():
    leagues = [
        {"country": "**Denmark** (1)", "gdp": 2.1, "income": 3.4, "prices": 57.3, "investment": 12.1, "debt": 3.5},
        {"country": "**Chile** (5)", "gdp": 10.4, "income": 32.7, "prices": -5.6, "investment": 6.7, "debt": 11.9},
        {"country": "**Ireland** (=6)", "gdp": 22.3, "income": 4.8, "prices": 17.1, "investment": -78.8, "debt": 0.9},
        {"country": "**United States** (9)", "gdp": 1.4, "income": 6.2, "prices": 24.4, "investment": 3.6, "debt": 18.9},
        {"country": "**Australia** (=10)", "gdp": -0.2, "income": 3.5, "prices": 9.1, "investment": 7.4, "debt": 10.2},
        {"country": "**Canada** (=10)", "gdp": -1.4, "income": 9.4, "prices": 25.9, "investment": 0.7, "debt": 11.6},
        {"country": "**France** (=15)", "gdp": -0.1, "income": 0.7, "prices": 17.4, "investment": 1.3, "debt": 14.4},
        {"country": "**Portugal** (=17)", "gdp": -3.2, "income": -0.3, "prices": 27.1, "investment": 0.5, "debt": 12.0},
        {"country": "**Germany** (20)", "gdp": -1.1, "income": -0.9, "prices": 15.6, "investment": -1.9, "debt": 13.6},
        {"country": "**Spain** (23)", "gdp": -6.6, "income": -6.3, "prices": -7.2, "investment": -6.5, "debt": 22.3},
    ]
    return (leagues,)


@app.cell
def _(EvidentialTable, col, leagues, mo, settings):
    positive, negative = "#1f8fae", "#6aa8bf"
    league_table = mo.ui.anywidget(
        EvidentialTable(
            leagues,
            settings=settings(
                title="League table of nations",
                subtitle="Selected OECD countries, % change during the covid-19 pandemic*",
                caption="Illustrative data, in the style of The Economist.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                # a small table reads better a step above the dense baseline
                font_size="+1",
            ),
            columns=[
                col.markdown("country"),
                col.number("gdp", align="center", fmt="num1")
                    .bar(center=True, color="#01A9C3", pad=3),
                col.number("income", title="Household income\nper person", align="center")
                    .bar(center=True, color="#086FA1", pad=3),
                col.number("prices", title="Share prices", align="center")
                    .bar(center=True, color="#8BB9CE", pad=3),
                col.number("investment", align="center")
                    .bar(center=True, color="#559CB8", pad=3),
                col.number("debt", title="Public debt\nto GDP", align="center")
                    .bar(center=True, color="#2EC1D3", pad=3),
            ],
        )
    )
    league_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Options

    The same column, three ways. `hide_labels=True` shows the bar alone;
    `color`/`negative_color` set one colour for both signs (or two); `pad=N` insets
    the bar from the top and bottom (a number of px or a CSS length) so it does not
    fill the row — the centre line is never padded, so it stays continuous; and
    `fit_to_data` scales to the column's own range rather than the min…max span.

    Colours accept matplotlib's names too — `tab:blue`, `C0`–`C9`, `k`, … — as the
    third column shows (`tab:blue` with `pad=4`).
    """)
    return


@app.cell
def _(EvidentialTable, col, leagues, mo, settings):
    variants = mo.ui.anywidget(
        EvidentialTable(
            leagues,
            settings=settings(
                title="The same % change, three ways",
                row_shading=True,
                row_lines=False,
                #border=False,
                #stretch=False,
                width="760px",
            ),
            columns=[
                col.text("country"),
                col.percent("gdp", whole=True, decimals=1, title="With values").bar(
                    center=True, color="blue", negative_color="red"
                ),
                col.percent("gdp", whole=True, decimals=1, title="Bar only").bar(
                    center=True, color="blue", negative_color="red", hide_labels=True
                ),
                col.percent("gdp", whole=True, decimals=1, title="tab:blue, pad=4").bar(
                    center=True, color="tab:blue", pad=4
                ),
            ],
        )
    )
    variants
    return


@app.cell
def _(mo):
    mo.md("""
    ## Back-to-back bars and a benchmark rule

    `direction="left"` fills a bar from the **right** edge, growing left — the
    mirror of the default. Put one of each either side of a label column and you
    get a **back-to-back** ("tornado") league table, the shape The Economist uses
    for its drug-price tables.

    `reference=N` draws a vertical rule at a value on the bar's own scale — a
    benchmark such as the OECD median. `reference_label` captions it once, on the
    last row. `color="@column"` takes each bar's colour from a column, so the same
    colour keys both panels.
    """)
    return


@app.cell
def _():
    # Values transcribed from The Economist's "Foreign-to-Canadian rate of
    # consumption per capita per drug", fig. 2-3e.
    _rows = [
        ("Switzerland", 26.0, 1.52, "7"),
        ("Canada", 19.1, 1.00, "6"),
        ("Australia", 18.2, 1.38, "5"),
        ("United Kingdom", 13.3, 1.00, "7"),
        ("France", 12.5, 0.98, "7"),
        ("Germany", 10.0, 0.55, "7"),
        ("Slovenia", 9.6, 0.96, "5"),
        ("Belgium", 9.0, 0.66, "5"),
        ("Sweden", 7.4, 0.79, "7"),
        ("Ireland", 6.5, 0.40, "5"),
        ("United States", 6.1, 0.15, "7"),
        ("Japan", 6.0, 0.38, "5"),
        ("Slovakia", 6.0, 0.46, "5"),
        ("Finland", 4.5, 0.35, "5"),
        ("Norway", 4.3, 0.35, "5"),
        ("Netherlands", 4.0, 0.32, "5"),
        ("Spain", 3.9, 0.23, "5"),
        ("Italy", 3.8, 0.28, "7"),
        ("Austria", 1.8, 0.14, "5"),
        ("Portugal", 1.7, 0.13, "5"),
        ("Turkey", 1.2, 0.24, "5"),
        ("Hungary", 1.0, 0.06, "5"),
        ("South Korea", 1.0, 0.10, "5"),
        ("Poland", 1.0, 0.09, "5"),
        ("New Zealand", 0.9, 0.03, "5"),
        ("Estonia", 0.2, 0.02, "5"),
    ]
    _category = {"5": "#3a9b9b", "6": "#b23a2e", "7": "#d9a01c"}
    price_table = [
        {"country": c, "spend": s, "rate": r, "color": _category[k]}
        for c, s, r, k in _rows
    ]
    return (price_table,)


@app.cell
def _(EvidentialTable, col, mo, price_table, settings):
    back_to_back = mo.ui.anywidget(
        EvidentialTable(
            price_table,
            settings=settings(
                title="Back-to-back league table",
                subtitle="Mirrored bars either side of a label, one benchmark rule per panel",
                caption=(
                    "Illustrative data, in the style of The Economist. Bar colour "
                    "marks the drug's review category."
                ),
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                width="820px",
            ),
            columns=[
                col.currency("spend", decimals=1, title="Sales per capita (CAD)")
                .bar(
                    direction="left",
                    reference=4.3,
                    reference_label="OECD median 4.3",
                    color="@color",
                    pad=3,
                )
                .align("left"),
                col.text("country", title="", align="center"),
                col.number("rate", fmt="num2", title="Foreign-to-Canadian rate")
                .bar(
                    reference=0.32,
                    reference_label="OECD median 0.32",
                    color="@color",
                    pad=3,
                )
                .align("right"),
                col.auto("color").hide(),
            ],
        )
    )
    back_to_back
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `bar(center=True)` is a second bar **geometry**, not a new visualisation —
      it reuses the bar cell, colour options and label.
    - `direction="left"` and `reference=N` are further bar options: the fill
      direction and a benchmark rule (with an optional `reference_label`).
      `color="@column"` colours each bar from a column.
    - The centre line is drawn at the middle of the cell; the bar grows from it
      and the value sits on the other half, so the centred cell has a wider
      minimum width than a plain bar column.
    - It composes with the usual helpers, e.g.
      `col.currency("change").bar(center=True).neg(bracket=True)` or a
      `@column` colour reference.
    - `font_size` raises or lowers the whole table from the shared baseline: a
      CSS length (`"14px"`) sets it absolutely, a step (`"+1"`, `"-1"`) adds
      that many 1px steps. This table uses `font_size="+1"`.
    """)
    return


if __name__ == "__main__":
    app.run()
