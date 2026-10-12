# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""`query_table` / date ranges, plus `page_size="all"`."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import LiveEvidentialTable, date_range_sql, query_table

    return LiveEvidentialTable, Path, date_range_sql, duckdb, mo, query_table


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
    # Query options

    `query_table` wraps a base query with Evidence's `where`, `order`, `limit`,
    `qualify` and `date_range` props. Date ranges accept presets
    (`last 12 months`, `previous year`, `month to date`), dynamic windows
    (`Last 90 days`), custom ranges (`2020-01-01 to 2021-01-01`) and partial
    ranges (`from 2020-01-01`).
    """)
    return


@app.cell
def _(connection, mo, query_table):
    recent = mo.ui.anywidget(
        query_table(
            connection,
            "SELECT category, order_datetime, sales FROM needful_things.orders",
            date_range={"range": "2019-01-01 to 2021-12-31", "date": "order_datetime"},
            where="sales > 10",
            order="sales DESC",
            limit=100,
            title="2019-2021, sales > $10",
            page_size=10,
            row_shading=True,
            column_config={
                "category": {"align": "left"},
                "order_datetime": {"title": "Ordered", "fmt": "shortdate", "align": "left"},
                "sales": {"fmt": "usd2", "viz": "bar"},
            },
        )
    )
    recent
    return


@app.cell
def _(connection, mo, query_table):
    everything = mo.ui.anywidget(
        query_table(
            connection,
            "SELECT category, order_datetime, sales FROM needful_things.orders",
            order="order_datetime DESC",
            title="All rows (page_size='all')",
            page_size="all",
            row_lines=False,
            column_config={
                "order_datetime": {"title": "Ordered", "fmt": "shortdate", "align": "left"},
                "sales": {"fmt": "usd2", "viz": "bar"},
            },
        )
    )
    everything
    return


@app.cell
def _(mo):
    mo.md("""
    ## Live date-range selector

    `date_range_sql` renders a preset, so a dropdown can drive a live table.
    """)
    return


@app.cell
def _(mo):
    preset = mo.ui.dropdown(
        ["last 30 days", "last 3 months", "last 12 months", "year to date", "all time"],
        value="all time",
        label="Date range",
    )
    preset
    return (preset,)


@app.cell
def _(LiveEvidentialTable, connection):
    live = LiveEvidentialTable(
        connection,
        "SELECT * FROM needful_things.orders",
        auto_run=False,
        title="Orders in range",
        page_size=10,
        row_shading=True,
        column_config={
            "order_datetime": {"title": "Ordered", "fmt": "shortdate", "align": "left"},
            "category": {"align": "left"},
            "sales": {"fmt": "usd2", "viz": "bar"},
        },
    )
    live
    return (live,)


@app.cell
def _(date_range_sql, live, preset):
    condition = date_range_sql(preset.value, "order_datetime")
    statement = "SELECT category, order_datetime, sales FROM needful_things.orders"
    if condition:
        statement += " WHERE " + condition
    _ = live.run(statement)
    return


if __name__ == "__main__":
    app.run()
