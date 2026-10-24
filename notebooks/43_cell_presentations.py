# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Cell chrome — `cell_style`.

A single value can carry several visual presentations at once: the formatted
text, a bar, a value label, and the **cell's own** background and text colour.
`cell_style` styles the cell independently of the marks on it, so a bar keeps
its own fill colour while the cell behind it is shaded.
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
    funds = [
        {"fund": "Growth", "return_pct": 12.4, "band": "#dcfce7"},
        {"fund": "Income", "return_pct": 3.1, "band": "#fef9c3"},
        {"fund": "Balanced", "return_pct": 6.8, "band": "#dcfce7"},
        {"fund": "Property", "return_pct": -2.5, "band": "#fee2e2"},
        {"fund": "Cash", "return_pct": 0.4, "band": "#fef9c3"},
    ]
    return (funds,)


@app.cell
def _(mo):
    mo.md("""
    # Cell chrome

    `cell_style(background=, color=, border=, padding=)` styles the **cell**,
    not the mark: a bar keeps its own fill while the cell behind it is shaded.
    Write `background="@column"` to take each row's colour from a column.

    This is the design system's *single datum, several presentations*: the same
    `return_pct` is formatted as text, drawn as a bar with a value label, and
    given a conditional background — each independent of the others.
    """)
    return


@app.cell
def _(EvidentialTable, col, funds, mo, settings):
    presentations = mo.ui.anywidget(
        EvidentialTable(
            funds,
            settings=settings(
                title="Fund returns",
                subtitle="Text + bar + value label + a per-row cell background",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("fund"),
                col.bar("return_pct", fmt="num1", title="Return", color="#2563eb", label=True)
                .cell_style(background="@band"),
                col.text("band").hide(),
            ],
        )
    )
    presentations
    return


@app.cell
def _(mo):
    mo.md("""
    ## Static chrome

    `background=`, `color=`, `border=` and `padding=` also take literals, applied
    to every row of the column. For a full-width band use `highlight=`; for a
    value-driven background (a gradient) use `col.color(...)` or
    `cell_style(background="@column")` as above.
    """)
    return


@app.cell
def _(EvidentialTable, col, funds, mo):
    static = mo.ui.anywidget(
        EvidentialTable(
            funds,
            title="A styled column",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("fund"),
                col.number("return_pct", fmt="num1", title="Return").cell_style(
                    background="#f8fafc", color="#0f172a", border="1px solid #e2e8f0", padding="4px 8px"
                ),
            ],
        )
    )
    static
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - Precedence: table defaults < row/column defaults < `cell_style` <
      matching `rules` for the **same** style property. A `tab_style` rule that
      sets `background-color` still wins over `cell_style`.
    - `cell_style` never recolours a mark's fill; use the mark's `color=` for
      that.
    - `background="@column"` is the `@column` reference convention, so a colour
      can be computed upstream in SQL or Python.
    """)
    return


if __name__ == "__main__":
    app.run()
