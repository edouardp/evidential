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
        {"country": "Denmark (1)", "gdp": 2.1, "income": 3.4, "prices": 57.3, "investment": 12.1, "debt": 3.5},
        {"country": "Chile (5)", "gdp": 10.4, "income": 32.7, "prices": -5.6, "investment": 6.7, "debt": 11.9},
        {"country": "Ireland (=6)", "gdp": 22.3, "income": 4.8, "prices": 17.1, "investment": -78.8, "debt": 0.9},
        {"country": "United States (9)", "gdp": 1.4, "income": 6.2, "prices": 24.4, "investment": 3.6, "debt": 18.9},
        {"country": "Australia (=10)", "gdp": -0.2, "income": 3.5, "prices": 9.1, "investment": 7.4, "debt": 10.2},
        {"country": "Canada (=10)", "gdp": -1.4, "income": 9.4, "prices": 25.9, "investment": 0.7, "debt": 11.6},
        {"country": "France (=15)", "gdp": -0.1, "income": 0.7, "prices": 17.4, "investment": 1.3, "debt": 14.4},
        {"country": "Portugal (=17)", "gdp": -3.2, "income": -0.3, "prices": 27.1, "investment": 0.5, "debt": 12.0},
        {"country": "Germany (20)", "gdp": -1.1, "income": -0.9, "prices": 15.6, "investment": -1.9, "debt": 13.6},
        {"country": "Spain (23)", "gdp": -6.6, "income": -6.3, "prices": -7.2, "investment": -6.5, "debt": 22.3},
    ]
    columns = [
        ("gdp", "GDP"),
        ("income", "Household income\nper person"),
        ("prices", "Share prices"),
        ("investment", "Investment"),
        ("debt", "Public debt\nto GDP"),
    ]
    return columns, leagues


@app.cell
def _(EvidentialTable, col, columns, leagues, mo, settings):
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
                width="760px",
            ),
            columns=[
                col.text("country"),
                *[
                    col.percent(key, whole=True, decimals=1, title=title).bar(
                        center=True, color=positive, negative_color=negative
                    )
                    for key, title in columns
                ],
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
    `color`/`negative_color` set one colour for both signs (or two); and
    `fit_to_data` scales to the column's own range rather than the min…max span
    (which matters most when the data does not straddle zero).
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
                border=False,
                stretch=False,
                width="760px",
            ),
            columns=[
                col.text("country"),
                col.percent("gdp", whole=True, decimals=1, title="With values").bar(
                    center=True, color="#1f8fae", negative_color="#6aa8bf"
                ),
                col.percent("gdp", whole=True, decimals=1, title="Bar only").bar(
                    center=True, color="#1f8fae", negative_color="#6aa8bf", hide_labels=True
                ),
                col.percent("gdp", whole=True, decimals=1, title="One colour").bar(
                    center=True, color="#53768a"
                ),
            ],
        )
    )
    variants
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `bar(center=True)` is a second bar **geometry**, not a new visualisation —
      it reuses the bar cell, colour options and label.
    - The centre line is drawn at the middle of the cell; the bar grows from it
      and the value sits on the other half, so the centred cell has a wider
      minimum width than a plain bar column.
    - It composes with the usual helpers, e.g.
      `col.currency("change").bar(center=True).neg(bracket=True)` or a
      `@column` colour reference.
    """)
    return


if __name__ == "__main__":
    app.run()
