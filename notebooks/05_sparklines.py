# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb

    from evidential import EvidentialTable, col

    return EvidentialTable, col, duckdb, mo


@app.cell
def _(mo):
    mo.md("""
    # Sparklines

    Evidence-style sparklines come from an **array in a cell** — one row per
    series point. In DuckDB you build that with `ARRAY_AGG({'x': ..., 'y': ...})`,
    then point a column at it with `viz="sparkline"` and `sparkline_options`:

    | Evidence attribute | `EvidentialTable` option |
    | --- | --- |
    | `contentType=sparkline` | `sparkline_options.type = "line"` |
    | `contentType=sparkarea` | `sparkline_options.type = "area"` |
    | `contentType=sparkbar` | `sparkline_options.type = "bar"` |
    | `sparkX` / `sparkY` | `sparkline_options.x` / `.y` |
    | `sparkColor` | `sparkline_options.color` |

    Hover a point to see its `x: y` value.
    """)
    return


@app.cell
def _(duckdb, mo):
    is_script_mode = mo.app_meta().mode == "script"

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs;")

    if is_script_mode:
        # Offline sample: ~83 days of hourly trips across three payment types.
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                TIMESTAMP '2024-01-01 00:00:00' + INTERVAL (i) HOUR AS pickup,
                ['Credit card', 'Cash', 'Dispute'][i % 3] AS payment,
                5 + (i % 40) + (i % 7) AS total_amount
            FROM range(1, 720) tbl(i)
            """
        )
    else:
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                tpep_pickup_datetime AS pickup,
                CASE payment_type
                    WHEN 1 THEN 'Credit card'
                    WHEN 2 THEN 'Cash'
                    WHEN 3 THEN 'No charge'
                    WHEN 4 THEN 'Dispute'
                    ELSE 'Other'
                END AS payment,
                total_amount
            FROM read_parquet(
                'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
            )
            """
        )
    return (connection,)


@app.cell
def _(EvidentialTable, col, connection, mo):
    # One ARRAY_AGG per sparkline column, each an array of {date, value} structs.
    trend_query = """
        WITH daily AS (
            SELECT
                payment,
                date_trunc('day', pickup) AS day,
                count(*) AS trips,
                sum(total_amount) AS revenue,
                avg(total_amount) AS aov
            FROM trips
            WHERE pickup BETWEEN TIMESTAMP '2024-01-01' AND TIMESTAMP '2024-02-01'
            GROUP BY payment, day
        )
        SELECT
            payment AS category,
            sum(trips) AS total_trips,
            round(sum(revenue), 0) AS total_revenue,
            ARRAY_AGG({'date': day, 'trips': trips}   ORDER BY day) AS trip_trend,
            ARRAY_AGG({'date': day, 'revenue': revenue} ORDER BY day) AS revenue_trend,
            ARRAY_AGG({'date': day, 'aov': aov}       ORDER BY day) AS aov_trend
        FROM daily
        GROUP BY payment
        ORDER BY total_revenue DESC
    """

    table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(trend_query),
            title="Payment types over time",
            subtitle="Each row carries three sparkline series built with ARRAY_AGG",
            page_size=10,
            row_shading=True,
            columns=[
                col.text("category"),
                col.integer("total_trips", title="Total trips"),
                col.currency("total_revenue", decimals=0, title="Revenue"),
                col.sparkline("trip_trend", title="Orders", x="date", y="trips", type="line"),
                col.sparkline("revenue_trend", title="Sales", x="date", y="revenue", type="area", color="#53768a"),
                col.sparkline("aov_trend", title="AOV", x="date", y="aov", type="bar", color="#97ba99"),
            ],
        )
    )
    table
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `sparkline_options` also accepts `width`, `height`, `fit_to_data`
      (scale to the data range instead of zero), `y_fmt`, and
      `x`/`y` field names.
    - Arrays of plain numbers (`[1, 2, 3]`) and `[[x, y], ...]` pairs also work;
      with no `x`/`y` config the first numeric struct field is used for the
      value and the first non-numeric field for the axis.
    - The data is passed through as-is, so this pairs naturally with
      `LiveEvidentialTable` — the sparkline arrays just update with the rows.
    """)
    return


if __name__ == "__main__":
    app.run()
