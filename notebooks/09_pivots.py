# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///
"""Pivoted columns (`pivot_table`) demonstrated on Evidence's sample data."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidence_tables import pivot_table

    return Path, duckdb, mo, pivot_table


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
    # Pivoted columns

    `pivot_table` pivots a dimension into columns: each distinct pivot value
    becomes its own column per measure, wrapped under a shared header. It
    reuses the same DuckDB `GROUPING SETS` machinery as `grouped_table`, so you
    also get subtotal rows and a grand total.
    """)
    return


@app.cell
def _(connection, mo, pivot_table):
    sales_by_year = mo.ui.anywidget(
        pivot_table(
            connection,
            "SELECT category, year(order_datetime) AS year, sales FROM needful_things.orders",
            dimensions=["category"],
            pivots=["year"],
            measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
            total_label="Total",
            title="Sales by category, pivoted by year",
            page_size=10,
            dimension_config={"category": {"align": "left"}},
            measure_config={
                "sales": {"fmt": "usd0"},
                "orders": {"fmt": "num0"},
            },
        )
    )
    sales_by_year
    return


@app.cell
def _(mo):
    mo.md("""
    ## `measures_first`

    Flip the header hierarchy so measures are the outer group
    (`Sales > 2019 | 2020 | 2021`) instead of pivot values.
    """)
    return


@app.cell
def _(connection, mo, pivot_table):
    measures_first = mo.ui.anywidget(
        pivot_table(
            connection,
            "SELECT category, year(order_datetime) AS year, sales FROM needful_things.orders",
            dimensions=["category"],
            pivots=["year"],
            measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
            measures_first=True,
            title="Same pivot, measures first",
            page_size=10,
            measure_config={"sales": {"fmt": "usd0"}, "orders": {"fmt": "num0"}},
        )
    )
    measures_first
    return


@app.cell
def _(mo):
    mo.md("""
    ## Subtotal rows

    Pivot by channel group, with subtotal rows (`subtotal_position="top"`).
    """)
    return


@app.cell
def _(connection, mo, pivot_table):
    by_channel = mo.ui.anywidget(
        pivot_table(
            connection,
            "SELECT category, channel_group, sales FROM needful_things.orders",
            dimensions=["category"],
            pivots=["channel_group"],
            measures=["round(sum(sales), 0) AS sales"],
            subtotal_position="top",
            title="Sales by category and channel group",
            max_height="460px",
            measure_config={"sales": {"fmt": "usd0", "viz": "bar"}},
        )
    )
    by_channel
    return


if __name__ == "__main__":
    app.run()
