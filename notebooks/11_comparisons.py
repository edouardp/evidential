# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""SQL prior-period comparisons and delta formatting."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import EvidentialTable, col

    return EvidentialTable, Path, col, duckdb, mo


@app.cell
def _(Path, duckdb):
    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    connection = duckdb.connect()
    connection.execute("CREATE SCHEMA IF NOT EXISTS needful_things")
    connection.execute(
        f"CREATE VIEW needful_things.orders AS SELECT * FROM read_parquet('{sample}')"
    )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Prior-period comparisons

    SQL finds the latest year or quarter in the sample and uses filtered
    aggregates for that period and the preceding one. The table renders
    explicitly named sales and change columns.

    ## Year over year
    """)
    return


@app.cell
def _(connection):
    yearly = connection.sql("""
        WITH periods AS (
            SELECT category, sales, year(order_datetime) AS year,
                   max(year(order_datetime)) OVER () AS latest
            FROM needful_things.orders
        ), totals AS (
            SELECT category,
                   sum(sales) FILTER (WHERE year = latest) AS sales,
                   sum(sales) FILTER (WHERE year = latest - 1) AS prior_sales,
                   count(*) FILTER (WHERE year = latest) AS orders,
                   count(*) FILTER (WHERE year = latest - 1) AS prior_orders,
                   count(*) FILTER (WHERE year = latest AND sales < 10) AS small_orders,
                   count(*) FILTER (WHERE year = latest - 1 AND sales < 10) AS prior_small_orders
            FROM periods
            WHERE year >= latest - 1
            GROUP BY category
        )
        SELECT *, sales - prior_sales AS change,
               (sales - prior_sales) / nullif(prior_sales, 0) AS change_pct,
               (small_orders - prior_small_orders) / nullif(prior_small_orders, 0) AS small_orders_pct
        FROM totals
        ORDER BY category
    """).to_arrow_table()
    return (yearly,)


@app.cell
def _(EvidentialTable, col, mo, yearly):
    mo.ui.anywidget(
        EvidentialTable(
            yearly,
            title="Sales by category vs prior year",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category"),
                col.currency("sales", title="Sales", decimals=0),
                col.currency("prior_sales", title="Prior-year sales", decimals=0),
                col.currency("change", decimals=0),
                col.percent("change_pct", title="% change", decimals=1).delta(),
                col.integer("orders"),
                col.integer("prior_orders"),
            ],
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Quarter over quarter

    Swap the comparison period; the column set is the same.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    qoq = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("""
                WITH periods AS (
                    SELECT category, channel_group, sales,
                           date_diff('quarter', order_datetime, max(order_datetime) OVER ()) AS periods_ago
                    FROM needful_things.orders
                ), totals AS (
                    SELECT category, channel_group,
                           sum(sales) FILTER (WHERE periods_ago = 0) AS sales,
                           sum(sales) FILTER (WHERE periods_ago = 1) AS prior_sales
                    FROM periods
                    WHERE periods_ago IN (0, 1)
                    GROUP BY category, channel_group
                )
                SELECT *, (sales - prior_sales) / nullif(prior_sales, 0) AS change_pct
                FROM totals
                ORDER BY category, channel_group
            """),
            title="Sales vs prior quarter",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category"),
                col.text("channel_group"),
                col.bar("sales", format="usd0", label=True),
                col.bar("prior_sales", format="usd0", label=True),
                col.percent("change_pct", title="% change", decimals=1).delta(),
            ],
        )
    )
    qoq
    return (qoq,)


@app.cell
def _(mo):
    mo.md("""
    ## Delta formatting

    The `% change` column is a `viz="delta"`. The indicator follows the value
    (`12.0% ▲`), **green** means an increase and **red** a decrease, and a value
    inside `neutral_range` shows a **grey dash** instead of an arrow.
    `down_is_good=True` flips the colours for a measure where lower is better.

    ### Neutral range

    Set `neutral_range` on the delta column. Here changes within ±25% read
    as neutral.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, yearly):
    mo.ui.anywidget(
        EvidentialTable(
            yearly,
            title="Sales changes within ±25% show a dash",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category"),
                col.currency("sales", decimals=0),
                col.currency("prior_sales", decimals=0),
                col.percent("change_pct", title="% change", decimals=1).delta(neutral_range="-0.25:0.25"),
            ],
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Flipping good and bad

    For a measure where a decrease is good, set `down_is_good=True`: the arrow
    is unchanged, but a fall is **green** and a rise is **red**.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, yearly):
    mo.ui.anywidget(
        EvidentialTable(
            yearly,
            title="Small orders: a fall is green",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category"),
                col.integer("small_orders"),
                col.integer("prior_small_orders"),
                col.percent("small_orders_pct", title="% change", decimals=1).delta(down_is_good=True),
            ],
        )
    )
    return


if __name__ == "__main__":
    app.run()
