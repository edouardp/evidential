# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Illustrative Evidential report; replace its data and prose for your task."""

# Marimo renders each cell's final expression.
# ruff: noqa: B018

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo

    from evidential import EvidentialTable, col, label, rows

    return EvidentialTable, col, label, mo, rows


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Product sales report

    An illustrative report with group headings, detail bars, footnotes,
    subtotals and a grand total. Summary rows are presentation metadata;
    the underlying records remain individual products.
    """)
    return


@app.cell
def data():
    orders = [
        {"region": "North", "product": "Lamp", "units": 12, "sales": 1200, "note": "Launch month."},
        {"region": "North", "product": "Chair", "units": 9, "sales": 1800, "note": None},
        {"region": "South", "product": "Desk", "units": 4, "sales": 2400, "note": None},
    ]
    return (orders,)


@app.cell
def report(EvidentialTable, col, label, orders, rows):
    report_table = EvidentialTable(
        orders,
        columns=[
            col.text("product").bold().footnote("note"),
            col.integer("units"),
            col.bar("sales", format="usd0", label=label.auto_position("outside end")),
        ],
        row_layout=rows.group_by("region")
        .section(values={"product": rows.count(suffix=" products")})
        .summary("Region total", values={"units": "sum", "sales": "sum"})
        .grand_summary("All regions", values={"units": "sum", "sales": "sum"}),
        section_indent=1,
        title="Product sales by region",
        subtitle="Three products · illustrative data",
        caption="Amounts in US dollars. Bars encode detail sales; summaries show totals.",
        page_size=0,
        border=False,
        row_lines=False,
        row_shading=True,
        width=800,
    )
    report_table
    return (report_table,)


if __name__ == "__main__":
    app.run()
