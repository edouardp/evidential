# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Evidence's own sample dataset (`needful_things.orders`) rendered with EvidentialTable.

The parquet file was copied from the published Evidence docs site
(``legacy-docs.evidence.dev/data/needful_things/orders/.../orders.parquet``) so
the examples here mirror Evidence's table docs.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import EvidentialTable, col, grouped_table

    return EvidentialTable, Path, col, duckdb, grouped_table, mo


@app.cell
def _(mo):
    mo.md("""
    # Evidence's sample data: `needful_things.orders`

    Evidence's docs are built on a small demo dataset — **10,000 orders** from
    2019–2021 across four categories, with dates, items, channels and sales.
    It isn't in the core Evidence repo; it ships as parquet under the docs site
    (`/data/needful_things/orders/...`). It's copied into
    `notebooks/sample_data/` here so these examples are self-contained.

    The tables below reproduce the `DataTable` examples from Evidence's docs.
    """)
    return


@app.cell
def _(Path, duckdb, mo):
    # Register the sample as `needful_things.orders`, exactly like Evidence.
    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    connection = duckdb.connect()
    connection.execute("CREATE SCHEMA IF NOT EXISTS needful_things")
    connection.execute(
        f"CREATE VIEW needful_things.orders AS SELECT * FROM read_parquet('{sample}')"
    )
    n_orders = connection.execute("SELECT count(*) FROM needful_things.orders").fetchone()[0]
    mo.md(f"Loaded **{n_orders:,}** orders from `sample_data/needful_things/{sample.name}`")
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    ## Sparklines

    The `categories` example from the docs: one `ARRAY_AGG` of `{date, value}`
    structs per row, rendered as line, area and bar sparklines.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    trend = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                WITH monthly AS (
                    SELECT
                        category,
                        date_trunc('month', order_datetime) AS date,
                        count(*) AS orders,
                        sum(sales) AS revenue,
                        avg(sales) AS aov
                    FROM needful_things.orders
                    GROUP BY ALL
                )
                SELECT
                    category,
                    sum(revenue) AS total_sales,
                    ARRAY_AGG({'date': date, 'v': orders}  ORDER BY date) AS orders_trend,
                    ARRAY_AGG({'date': date, 'v': revenue} ORDER BY date) AS sales_trend,
                    ARRAY_AGG({'date': date, 'v': aov}     ORDER BY date) AS aov_trend
                FROM monthly
                GROUP BY category
                ORDER BY total_sales DESC
                """
            ),
            title="Monthly trends by category",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category", title="Category"),
                col.currency("total_sales", decimals=0, title="Total sales"),
                col.sparkline("orders_trend", title="Orders", x="date", y="v", type="line"),
                col.sparkline("sales_trend", title="Sales", x="date", y="v", type="area", color="#53768a"),
                col.sparkline("aov_trend", title="AOV", x="date", y="v", type="bar", color="#97ba99"),
            ],
        )
    )
    trend
    return


@app.cell
def _(mo):
    mo.md("""
    ## Grouped subtotals

    `grouped_table` runs a DuckDB `GROUPING SETS` query over the same data to
    produce collapsible category → item subtotals.
    """)
    return


@app.cell
def _(col, connection, grouped_table, mo):
    grouped = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
            total_label="All categories",
            subtotal_position="top",
            title="Sales by category and item",
            search=True,
            max_height="460px",
            dimension_config={"category": col.text("category"), "item": col.text("item")},
            measure_config={
                "sales": col.bar("sales", format='usd0', label=True).total_fmt("usd2"),
                "orders": col.integer("orders"),
            },
        )
    )
    grouped
    return


@app.cell
def _(mo):
    mo.md("""
    ## Raw orders

    The `orders_summary` example — plain rows with formatting, bars and
    links.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    orders = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT id, order_datetime, category, item, channel_group, sales
                FROM needful_things.orders
                ORDER BY order_datetime DESC
                --LIMIT 200
                """
            ),
            title="Recent orders",
            search=True,
            page_size=12,
            row_shading=True,
            columns=[
                col.number("id", fmt="id", title="Order"),
                col.date("order_datetime", fmt="shortdate", title="Ordered"),
                col.text("category", title="Category"),
                col.text("item", title="Item"),
                col.text("channel_group", title="Channel"),
                col.bar("sales", title="Sales", format='usd2', label=True),
            ],
        )
    )
    orders
    return


if __name__ == "__main__":
    app.run()
