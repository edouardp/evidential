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

    from evidential import BUILTIN_AGGREGATIONS, grouped_table

    return BUILTIN_AGGREGATIONS, Path, duckdb, grouped_table, mo


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

    By default a subtotal/total row re-runs the measure's SQL aggregate. The
    `aggregations` argument instead recomputes it from the **detail values**,
    matching Evidence's `totalAgg`.

    - **Built-in names:** `{", ".join(sorted(set(BUILTIN_AGGREGATIONS))) }`
    - **Custom callables:** any `values -> aggregate` function.
    - `weight_columns={{measure: column}}` supplies weights for `weighted_mean`.

    Each table below groups sales by category → item; the subtotal is the chosen
    aggregation over the item-level sums.
    """)
    return


@app.cell
def _(connection, grouped_table, mo):
    default_sum = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales"],
            subtotal_position="top",
            title="Default (sum)",
            max_height="360px",
            measure_config={"sales": {"fmt": "usd0"}},
        )
    )
    default_sum
    return


@app.cell
def _(connection, grouped_table, mo):
    means = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales"],
            subtotal_position="top",
            aggregations={"sales": "mean"},
            title='aggregations={"sales": "mean"}',
            max_height="360px",
            measure_config={"sales": {"fmt": "usd2"}},
        )
    )
    means
    return


@app.cell
def _(connection, grouped_table, mo):
    medians = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales"],
            subtotal_position="top",
            aggregations={"sales": "median"},
            title='aggregations={"sales": "median"}',
            max_height="360px",
            measure_config={"sales": {"fmt": "usd2"}},
        )
    )
    medians
    return


@app.cell
def _(connection, grouped_table, mo):
    # A custom Python callable receives the list of detail values.
    def spread(values):
        return max(values) - min(values)

    custom = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales"],
            subtotal_position="top",
            aggregations={"sales": spread},
            title="aggregations={'sales': spread} (max - min)",
            max_height="360px",
            measure_config={"sales": {"fmt": "usd0"}},
        )
    )
    custom
    return


if __name__ == "__main__":
    app.run()
