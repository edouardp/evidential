# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Column scales — tick axes and gridlines (design system: column scales).

`scale(axis=True)` draws a tick axis for a marks column, above the cells by
default (or below with `axis_position="bottom"`). `gridlines=True` adds faint
vertical lines through the cells so a value can be read against the scale.
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
def _():
    shares = [
        {"party": "National", "share": 38},
        {"party": "Labour", "share": 34},
        {"party": "Green", "share": 11},
        {"party": "ACT", "share": 9},
        {"party": "Māori", "share": 4},
        {"party": "Other", "share": 4},
    ]
    return (shares,)


@app.cell
def _(mo):
    mo.md("""
    # Column scales

    A bar or point is only readable against an axis. `scale(domain=..., axis=True)`
    puts a tick axis for the column **above** the cells (below the column label),
    and `gridlines=True` draws faint vertical lines down the cells so the value
    can be followed from the axis.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, settings, shares):
    axis_top = mo.ui.anywidget(
        EvidentialTable(
            shares,
            settings=settings(
                title="Share of the vote",
                subtitle="Axis above the bars, with gridlines",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("party"),
                col.bar("share", color="#2563eb")
                   .scale(domain=(0, 40), axis=True, gridlines=True, unit="%"),
            ],
        )
    )
    axis_top
    return


@app.cell
def _(mo):
    mo.md("""
    ## Axis below the cells

    `axis_position="bottom"` places the axis under the last row instead, and the
    axis shares the marks' domain — including a fixed `domain=(lo, hi)`.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, shares):
    axis_below = mo.ui.anywidget(
        EvidentialTable(
            shares,
            title="Share of the vote",
            subtitle="Axis below the bars",
            row_lines=True,
            border=False,
            stretch=True, width=600,
            columns=[
                col.text("party"),
                col.bar("share", color="#0ea5e9").label("@share")
                   .scale(domain=(0, 40), axis=True, axis_position="bottom", unit="%"),
            ],
        )
    )
    axis_below
    return


@app.cell
def _(mo):
    mo.md("""
    ## A log-scale axis

    `transform="log"` gives the axis a power-of-ten tick ladder (with 2× and 5×
    subdivisions), which is how a forest plot or a ratio chart is read.
    """)
    return


@app.cell
def _():
    ratios = [
        {"study": "A", "low": 1.4, "estimate": 3.2, "high": 8.1},
        {"study": "B", "low": 0.8, "estimate": 1.1, "high": 1.6},
        {"study": "C", "low": 2.2, "estimate": 4.9, "high": 12.0},
    ]
    return (ratios,)


@app.cell
def _(EvidentialTable, col, mo, ratios):
    log_axis = mo.ui.anywidget(
        EvidentialTable(
            ratios,
            title="Odds ratios",
            subtitle="A log axis with gridlines and the null at 1",
            row_lines=False,
            border=False,
            stretch=True, width=600,
            columns=[
                col.text("study"),
                col.range("low", "high", cap="line", color="#94a3b8")
                .point("estimate", color="#1d4ed8", size=8)
                .scale(
                    domain=(0.5, 20),
                    transform="log",
                    axis=True,
                    gridlines=True,
                )
                #.reference_line(1, label="null")
                .title("Range").align("center")
            ],
        )
    )
    log_axis
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - The axis and gridlines use the column's shared scale (`domain`, `transform`
      and `include_zero`), so an explicit domain also fixes the ticks.
    - Tick values are rounded to "nice" steps; the label uses the column's own
      format code.
    - `gridlines=True` works without `axis=True` if only the lines are wanted.
    """)
    return


if __name__ == "__main__":
    app.run()
