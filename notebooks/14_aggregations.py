# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Built-in and custom aggregations for subtotals and totals."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import BUILTIN_AGGREGATIONS, col, grouped_records

    return BUILTIN_AGGREGATIONS, Path, col, duckdb, grouped_records, mo


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
def _(BUILTIN_AGGREGATIONS, mo):
    mo.md(f"""
    # Aggregations for subtotals and totals

    SQL computes sales per item. The `aggregations` argument to
    `grouped_records` controls how those item-level sums are summarized.

    - **Built-in names:** `{", ".join(sorted(BUILTIN_AGGREGATIONS))}`
    - **Custom callables:** any `values -> aggregate` function.
    """)
    return


@app.cell
def _(connection):
    item_sales = connection.sql("""
        SELECT category, item, sum(sales) AS sales
        FROM needful_things.orders
        GROUP BY category, item
    """).to_arrow_table()
    return (item_sales,)


@app.cell
def _(col, grouped_records, item_sales, mo):
    default_sum = mo.ui.anywidget(
        grouped_records(
            item_sales,
            group_by=["category", "item"],
            measures=["sales"],
            subtotal_position="top",
            title="Default (sum)",
            max_height="360px",
            measure_config={"sales": col.currency("sales", decimals=0)},
        )
    )
    default_sum
    return


@app.cell
def _(col, grouped_records, item_sales, mo):
    means = mo.ui.anywidget(
        grouped_records(
            item_sales,
            group_by=["category", "item"],
            measures=["sales"],
            subtotal_position="top",
            aggregations={"sales": "mean"},
            title='aggregations={"sales": "mean"}',
            max_height="360px",
            measure_config={"sales": col.currency("sales", decimals=2)},
        )
    )
    means
    return


@app.cell
def _(col, grouped_records, item_sales, mo):
    medians = mo.ui.anywidget(
        grouped_records(
            item_sales,
            group_by=["category", "item"],
            measures=["sales"],
            subtotal_position="top",
            aggregations={"sales": "median"},
            title='aggregations={"sales": "median"}',
            max_height="360px",
            measure_config={"sales": col.currency("sales", decimals=2)},
        )
    )
    medians
    return


@app.cell
def _(col, grouped_records, item_sales, mo):
    # A custom Python callable receives the list of detail values.
    def spread(values):
        return max(values) - min(values)

    custom = mo.ui.anywidget(
        grouped_records(
            item_sales,
            group_by=["category", "item"],
            measures=["sales"],
            subtotal_position="top",
            aggregations={"sales": spread},
            title="aggregations={'sales': spread} (max - min)",
            max_height="360px",
            measure_config={"sales": col.currency("sales", decimals=0)},
        )
    )
    custom
    return


if __name__ == "__main__":
    app.run()
