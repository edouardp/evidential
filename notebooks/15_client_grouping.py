# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Client-side grouping of in-memory rows (`grouped_records`)."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import col, grouped_records

    return col, grouped_records, mo


@app.cell
def _():
    # A flat list of records already in Python — no database needed.
    sales = [
        {"region": "Americas", "category": "Toys", "sales": 1200.0, "orders": 12},
        {"region": "Americas", "category": "Fish", "sales": 800.0, "orders": 6},
        {"region": "Americas", "category": "Gear", "sales": 1500.0, "orders": 9},
        {"region": "Europe", "category": "Toys", "sales": 900.0, "orders": 7},
        {"region": "Europe", "category": "Gear", "sales": 2100.0, "orders": 14},
        {"region": "Asia", "category": "Gear", "sales": 700.0, "orders": 4},
    ]
    return (sales,)


@app.cell
def _(mo):
    mo.md("""
    # Client-side grouping

    `grouped_records` groups a flat table held in Python (a list of dicts, a
    DataFrame, …) into hierarchical rows with subtotals and a total — the
    equivalent of Evidence's legacy `groupBy`. Measures default to the numeric
    columns and are summed, or use `aggregations` (built-ins/callables) like
    `grouped_table`.
    """)
    return


@app.cell
def _(col, grouped_records, mo, sales):
    accordion = mo.ui.anywidget(
        grouped_records(
            sales,
            group_by=["region", "category"],
            measures=["sales", "orders"],
            total_label="All regions",
            subtotal_position="top",
            collapsible=True,
            title="Accordion groups",
            measure_config={
                "sales": col.currency("sales", decimals=0).bar(),
                "orders": col.integer("orders"),
            },
        )
    )
    accordion
    return


@app.cell
def _(col, grouped_records, mo, sales):
    section = mo.ui.anywidget(
        grouped_records(
            sales,
            group_by=["region", "category"],
            measures=["sales", "orders"],
            total_label="All regions",
            subtotal_position="top",
            group_type="section",
            title="Section groups (merged cells)",
            measure_config={
                "sales": col.currency("sales", decimals=0).bar(),
                "orders": col.integer("orders"),
            },
        )
    )
    section
    return


@app.cell
def _(col, grouped_records, mo, sales):
    averaged = mo.ui.anywidget(
        grouped_records(
            sales,
            group_by=["region"],
            measures=["sales"],
            aggregations={"sales": "mean"},
            title='aggregations={"sales": "mean"} (mean order value)',
            measure_config={"sales": col.currency("sales", decimals=2)},
        )
    )
    averaged
    return


if __name__ == "__main__":
    app.run()
