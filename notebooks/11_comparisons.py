# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Prior-period comparisons (`comparison_table`) and delta formatting."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import comparison_table

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


@app.cell
def _(mo):
    mo.md("""
    ## Delta formatting

    The `% change` column is a `viz="delta"`. The indicator follows the value
    (`12.0% ▲`), **green** means an increase and **red** a decrease, and a value
    inside `neutral_range` shows a **grey dash** instead of an arrow.
    `down_is_good=True` flips the colours for a measure where lower is better.

    ### Neutral range

    `neutral_range` accepts an inclusive range — a `"-0.1:0.1"` string, a
    `[lo, hi]` pair, or a single ±value — and can be set at the top level of
    `measure_config` / `column_config` next to `fmt`. Here changes within ±25%
    read as neutral (widened from the usual ±10% so this data shows the dash).
    """)
    return


@app.cell
def _(comparison_table, connection, mo):
    neutral = mo.ui.anywidget(
        comparison_table(
            connection,
            "SELECT category, order_datetime, sales FROM needful_things.orders",
            dimensions=["category"],
            measures=["round(sum(sales), 0) AS sales"],
            date_column="order_datetime",
            compare_vs="prior year",
            title='neutral_range="-0.25:0.25" — changes within ±25% show a dash',
            page_size=10,
            row_shading=True,
            measure_config={"sales": {"fmt": "usd0", "neutral_range": "-0.25:0.25"}},
        )
    )
    neutral
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
def _(comparison_table, connection, mo):
    down_is_good = mo.ui.anywidget(
        comparison_table(
            connection,
            "SELECT category, order_datetime, sales FROM needful_things.orders",
            dimensions=["category"],
            measures=["count(*) FILTER (WHERE sales < 10) AS small_orders"],
            date_column="order_datetime",
            compare_vs="prior year",
            title="`small_orders with down_is_good=True — a fall is green`",
            page_size=10,
            row_shading=True,
            measure_config={"small_orders": {"fmt": "num0", "down_is_good": True}},
        )
    )
    down_is_good
    return


if __name__ == "__main__":
    app.run()
