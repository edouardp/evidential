# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb

    from evidence_tables import LiveEvidenceTable, query_values

    return LiveEvidenceTable, duckdb, mo, query_values


@app.cell
def _(mo):
    mo.md("""
    # Live, parameterised tables

    `LiveEvidenceTable` keeps a parameterised SQL query and re-runs it whenever
    a bound control changes — the widget itself is not recreated, so sort,
    search and page state are preserved.

    Controls are bound by passing them to `params` (or by interpolating the
    control itself in a t-string). Values are bound as query parameters, never
    spliced into the SQL text.
    """)
    return


@app.cell
def _(duckdb, mo):
    is_script_mode = mo.app_meta().mode == "script"

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs;")

    if is_script_mode:
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                *,
                tip_amount / nullif(fare_amount, 0) AS tip_rate
            FROM (VALUES
                (TIMESTAMP '2024-01-01 08:12:00', 1, 'Credit card', 2.4, 12.5, 3.1),
                (TIMESTAMP '2024-01-01 08:31:00', 2, 'Cash',        7.8, 24.0, 0.0),
                (TIMESTAMP '2024-01-06 09:02:00', 1, 'Credit card', 1.2,  9.0, 2.2),
                (TIMESTAMP '2024-01-07 09:41:00', 4, 'Dispute',     12.1, 41.0, 9.5),
                (TIMESTAMP '2024-01-08 10:15:00', 2, 'Cash',        4.9, 18.0, 0.0)
            ) AS v(tpep_pickup_datetime, payment_type, payment, trip_distance, fare_amount, tip_amount)
            """
        )
    else:
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                tpep_pickup_datetime,
                payment_type,
                CASE payment_type
                    WHEN 1 THEN 'Credit card'
                    WHEN 2 THEN 'Cash'
                    WHEN 3 THEN 'No charge'
                    WHEN 4 THEN 'Dispute'
                    ELSE 'Other'
                END AS payment,
                trip_distance,
                fare_amount,
                tip_amount,
                tip_amount / nullif(fare_amount, 0) AS tip_rate
            FROM read_parquet(
                'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
            )
            """
        )
    return (connection,)


@app.cell
def _(connection, mo, query_values):
    min_fare = mo.ui.slider(0, 80, value=10, label="Minimum fare ($)")
    payment_options = [
        "All",
        *query_values(connection, "SELECT DISTINCT payment FROM trips ORDER BY 1"),
    ]
    payment = mo.ui.dropdown(payment_options, value="All", label="Payment type")
    mo.hstack([min_fare, payment], justify="start", gap=2)
    return min_fare, payment


@app.cell
def _(LiveEvidenceTable, connection):
    # Persistent widget: created once, with no references to the controls, so
    # changing a control never recreates it (and never resets sort/page).
    live = LiveEvidenceTable(
        connection,
        """
        SELECT payment, trip_distance, fare_amount, tip_amount, tip_rate
        FROM trips
        WHERE fare_amount >= {min_fare}
          AND ({payment} = 'All' OR payment = {payment})
        ORDER BY fare_amount DESC
        LIMIT 500
        """,
        auto_run=False,
        title="Live filtered taxi trips",
        search=True,
        page_size=12,
        row_shading=True,
        column_config={
            "payment": {"title": "Payment", "align": "left"},
            "trip_distance": {"title": "Distance", "fmt": "num1", "viz": "bar"},
            "fare_amount": {"fmt": "usd2"},
            "tip_amount": {"title": "Tip", "fmt": "usd2"},
            "tip_rate": {
                "title": "Tip rate",
                "fmt": "pct1",
                "viz": "color",
                "color_scale": ["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
                "color_options": {"midpoint": 0.15, "min": 0, "max": 0.4},
            },
        },
    )
    live
    return (live,)


@app.cell
def _(live, min_fare, payment):
    # Reactive cell: re-runs when either control changes and pushes fresh rows
    # into the persistent widget (values are bound as SQL parameters).
    _ = live.set_controls(min_fare=min_fare, payment=payment)
    return


if __name__ == "__main__":
    app.run()
