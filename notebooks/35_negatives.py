# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Negative values — `.neg(color=, bracket=)`.

Colour negative numbers (in a custom colour if you like) and wrap them in
accounting-style brackets.
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
    # Negative values with `.neg(...)`

    `.neg()` marks negative numbers: it colours them (the theme's red by default)
    and can wrap them in **accounting brackets**.

    ```python
    col.currency("profit").neg()                               # red negatives
    col.currency("profit").neg(color="#b91c1c")                # a set colour
    col.currency("profit").neg(bracket=True)                   # -1,234 -> (1,234)
    col.currency("profit").neg(color="#b91c1c", bracket=True)  # both
    ```

    `bracket=True` replaces the sign with parentheses, so the column stays
    right-aligned and the digits still line up. `red_negatives()` is the older
    boolean-only spelling; `.neg()` is the richer one.
    """)
    return


@app.cell
def _():
    pnl = [
        {"line_item": "Revenue", "amount": 1_284_500.0},
        {"line_item": "Cost of sales", "amount": -612_300.0},
        {"line_item": "Gross profit", "amount": 672_200.0},
        {"line_item": "Sales & marketing", "amount": -188_400.0},
        {"line_item": "Research & development", "amount": -96_750.0},
        {"line_item": "General & admin", "amount": -71_200.0},
        {"line_item": "Operating profit", "amount": 315_850.0},
        {"line_item": "Interest", "amount": -24_100.0},
        {"line_item": "Tax", "amount": -73_440.0},
        {"line_item": "Net profit", "amount": 218_310.0},
    ]
    return (pnl,)


@app.cell
def _(EvidentialTable, col, mo, pnl):
    table = mo.ui.anywidget(
        EvidentialTable(
            pnl,

            title="Income statement (illustrative)",
            row_shading=True,
            row_lines=False,
            border=False,
            stretch=False,
            width="820px",

            columns=[
                col.text("line_item", title="").bold(),
                col.currency("amount", decimals=0, title="Plain"),
                col.currency("amount", decimals=0, title=".neg()").neg(),
                col.currency("amount", decimals=0, title=".neg(color=…, bracket=True)").neg(color="darkred", bracket=True),
            ],
        )
    )
    table
    return


@app.cell
def _(mo):
    mo.md("""
    ## With a centred bar

    `.neg()` composes with the other column helpers — here a month-over-month
    change as a centred bar, and the same change with bracketed negatives.
    """)
    return


@app.cell
def _():
    changes = [
        {"month": "Jan", "revenue": 1_120_000, "mom_pct": 4.2},
        {"month": "Feb", "revenue": 1_080_500, "mom_pct": -3.5},
        {"month": "Mar", "revenue": 1_240_900, "mom_pct": 14.8},
        {"month": "Apr", "revenue": 1_198_300, "mom_pct": -3.4},
        {"month": "May", "revenue": 1_284_500, "mom_pct": 7.2},
        {"month": "Jun", "revenue": 1_169_000, "mom_pct": -9.0},
    ]
    return (changes,)


@app.cell
def _(EvidentialTable, changes, col, mo, settings):
    change_table = mo.ui.anywidget(
        EvidentialTable(
            changes,
            settings=settings(
                title="Revenue, month over month",
                subtitle="Hero graphic for monthly growth",
                caption="In the style of The Economist",
                row_shading=True,
                row_lines=False,
                font_size="+8",
                border=False,
                stretch=True,
                width="600px",
            ),
            columns=[
                col.text("month"),
                col.currency("revenue", decimals=0, title="Revenue"),
                col.percent("mom_pct", whole=True, decimals=1, title="Change").neg(bracket=True),
                col.bar("mom_pct", title="Change (bar)", align="center", format='0.0"%"', center=True, pad=3, color="tab:blue", negative_color="tab:red", label=True),
            ],
        )
    )
    change_table
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `.neg()` sets three options: `red_negatives` (marking on), `negative_color`
      (when `color` is given) and `bracket_negatives` (when `bracket`).
    - `bracket=True` strips the leading `-` and wraps the value, so a currency
      column reads `(1,234)` and stays right-aligned.
    - It composes with `col.bar(..., label=True)`, `.delta(...)`, `.color(...)` and the rest of
      the chain; colours accept the matplotlib names (`tab:red`, `C3`, `k`, …).
    - `.neg()` turns marking **on**; there is not yet a "brackets only, no colour"
      spelling.
    """)
    return


if __name__ == "__main__":
    app.run()
