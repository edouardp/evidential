# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Illustrative persistent live summary and selection-driven monthly detail."""

# Marimo renders each cell's final expression.
# ruff: noqa: B018

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, LiveEvidentialTable, col, label

    return EvidentialTable, LiveEvidentialTable, col, duckdb, label, mo


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Product sales explorer

    Filter products by total units and click a row for its monthly detail.
    This is illustrative data. Controls update the existing table models;
    table creation is independent of the controls.
    """)
    return


@app.cell
def data(duckdb):
    connection = duckdb.connect()
    _ = connection.execute("""
        CREATE TABLE sales AS SELECT * FROM (VALUES
            ('lamp', 'Lamp', DATE '2026-01-01', 12, 1200),
            ('lamp', 'Lamp', DATE '2026-02-01', 18, 1800),
            ('chair', 'Chair', DATE '2026-01-01', 9, 1800),
            ('chair', 'Chair', DATE '2026-02-01', 11, 2200),
            ('desk', 'Desk', DATE '2026-01-01', 4, 2400),
            ('desk', 'Desk', DATE '2026-02-01', 6, 3600)
        ) AS source(product_id, product, month, units, sales)
    """)
    return (connection,)


@app.cell
def controls(mo):
    minimum_units = mo.ui.slider(start=0, stop=40, step=5, value=0, label="Minimum total units")
    minimum_units
    return (minimum_units,)


@app.cell
def summary(LiveEvidentialTable, col, connection, label, mo):
    live = mo.ui.anywidget(
        LiveEvidentialTable(
            connection,
            """
        SELECT product_id, product, sum(units) AS units, sum(sales) AS sales
        FROM sales GROUP BY product_id, product
        HAVING sum(units) >= $minimum ORDER BY sales DESC, product
        """,
            auto_run=False,
            select="product_id",
            title="Product totals",
            subtitle="Click a product for monthly detail",
            search=True,
            page_size=10,
            border=False,
            columns=[
                col.text("product").bold(),
                col.integer("units"),
                col.bar("sales", format="usd0", label=label.auto_position("outside end")),
            ],
        )
    )
    live
    return (live,)


@app.cell
def refresh_summary(live, minimum_units):
    live.widget.set_controls(minimum=minimum_units.value)
    available_products = {record["product_id"] for record in live.widget.raw}
    if live.widget.selected not in available_products:
        live.widget.selected = None
    return (available_products,)


@app.cell
def selection(available_products, live):
    selected_id = live.widget.selected if live.widget.selected in available_products else None
    return (selected_id,)


@app.cell
def detail(EvidentialTable, col, label, mo):
    detail_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Monthly detail",
            empty_message="Select a product above",
            empty_rows=1,
            page_size=0,
            border=False,
            columns=[
                col.date("month"),
                col.integer("units"),
                col.bar("sales", format="usd0", label=label.auto_position("outside end")),
            ],
        )
    )
    detail_table
    return (detail_table,)


@app.cell
def refresh_detail(connection, detail_table, selected_id):
    data = (
        connection.execute(
            "SELECT month, units, sales FROM sales WHERE product_id = ? ORDER BY month",
            [selected_id],
        )
        if selected_id is not None
        else []
    )
    with detail_table.widget.hold_sync():
        detail_table.widget.set_data(data)
        detail_table.widget.update_options(
            title=f"{selected_id.title()} · Monthly detail" if selected_id else "Monthly detail"
        )
    return


if __name__ == "__main__":
    app.run()
