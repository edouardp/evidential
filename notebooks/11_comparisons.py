# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///
"""Prior-period comparisons (`comparison_table`)."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidence_tables import comparison_table

    return Path, comparison_table, duckdb, mo


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

    `comparison_table` computes each measure for the current period and the
    matching prior period, anchored on the latest date in the data, then adds
    `<measure>_prior`, `<measure>_delta` (absolute change) and `<measure>_pct`
    (percentage change, shown as a delta).

    ## Year over year
    """)
    return


@app.cell
def _(comparison_table, connection, mo):
    yoy = mo.ui.anywidget(
        comparison_table(
            connection,
            "SELECT category, order_datetime, sales FROM needful_things.orders",
            dimensions=["category"],
            measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
            date_column="order_datetime",
            compare_vs="prior year",
            title="Sales by category vs prior year",
            page_size=10,
            row_shading=True,
            dimension_config={"category": {"align": "left"}},
            measure_config={
                "sales": {"fmt": "usd0"},
                "orders": {"fmt": "num0"},
            },
        )
    )
    yoy
    return


@app.cell
def _(mo):
    mo.md("""
    ## Quarter over quarter

    Swap the comparison period; the column set is the same.
    """)
    return


@app.cell
def _(comparison_table, connection, mo):
    qoq = mo.ui.anywidget(
        comparison_table(
            connection,
            "SELECT category, channel_group, order_datetime, sales FROM needful_things.orders",
            dimensions=["category", "channel_group"],
            measures=["round(sum(sales), 0) AS sales"],
            date_column="order_datetime",
            compare_vs="prior quarter",
            title="Sales vs prior quarter",
            page_size=10,
            row_shading=True,
            measure_config={"sales": {"fmt": "usd0", "viz": "bar"}},
        )
    )
    qoq
    return


if __name__ == "__main__":
    app.run()
