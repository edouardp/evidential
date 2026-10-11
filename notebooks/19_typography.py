# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidence-tables",
# ]
# ///
"""Table typography: readable by default, not over-styled.

Follows the principles in Richard Rutter's "Web Typography: Tables":
left-align text, right-align numbers, match headings to data, align to the
decimal, use tabular numerals, don't stretch the table, and keep furniture to a
minimum.
"""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidence_tables import EvidenceTable

    return EvidenceTable, mo


@app.cell
def _(mo):
    mo.md("""
    # Table typography

    | Principle | How |
    | --- | --- |
    | Left-align text, right-align numbers | alignment defaults by column type |
    | Match headings to their data | header alignment follows the column |
    | Align to the decimal point | `align_decimals=True` (pads to a common precision) |
    | Tabular lining numerals | `font-variant-numeric: tabular-nums` on numbers |
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
def _(EvidenceTable, mo, rows):
    mo.ui.anywidget(
        EvidenceTable(
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
            column_config={
                "item": {"title": "Item", "align": "left"},
                "quantity": {"title": "Quantity", "fmt": "num0", "align": "right"},
                "unit_price": {"title": "Unit price", "fmt": "num", "align": "right"},
                "total": {"title": "Total", "fmt": "usd", "align": "right"},
                "share": {"title": "Share", "fmt": "pct", "align": "right"},
            },
        )
    )
    return


if __name__ == "__main__":
    app.run()
