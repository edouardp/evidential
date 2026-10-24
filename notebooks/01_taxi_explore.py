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

    from evidential import EvidentialTable, col, grouped_table

    return EvidentialTable, col, duckdb, grouped_table, mo


@app.cell
def _(mo):
    mo.md("""
    # NYC yellow taxi — Evidence-style tables

    This notebook streams the public NYC TLC Parquet files with DuckDB and
    renders them with `EvidentialTable`, an anywidget that mirrors the
    formatting, conditional colours, bars and interactions of
    [Evidence.dev](https://evidence.dev) tables.

    No AWS account is needed: DuckDB's `httpfs` reads the parquet files
    straight from the TLC CloudFront bucket.
    """)
    return


@app.cell
def _(duckdb, mo):
    is_script_mode = mo.app_meta().mode == "script"

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs;")

    if is_script_mode:
        # Fast, offline source so `marimo run --sandbox`/CI stays quick.
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                *,
                dayofweek(tpep_pickup_datetime) IN (0, 6) AS is_weekend,
                tip_amount / nullif(fare_amount, 0) AS tip_rate,
                CASE payment_type
                    WHEN 1 THEN 'Credit card'
                    WHEN 2 THEN 'Cash'
                    WHEN 3 THEN 'No charge'
                    WHEN 4 THEN 'Dispute'
                    ELSE 'Other'
                END AS payment
            FROM (VALUES
                (TIMESTAMP '2024-01-01 08:12:00', 1, 1, 2.4, 12.5, 3.1, 17.8),
                (TIMESTAMP '2024-01-01 08:31:00', 2, 2, 7.8, 24.0, 0.0, 27.5),
                (TIMESTAMP '2024-01-06 09:02:00', 1, 3, 1.2,  9.0, 2.2, 12.4),
                (TIMESTAMP '2024-01-07 09:41:00', 4, 1, 12.1, 41.0, 9.5, 55.1),
                (TIMESTAMP '2024-01-08 10:15:00', 2, 3, 4.9, 18.0, 0.0, 21.0)
            ) AS v(tpep_pickup_datetime, payment_type, passenger_count,
                   trip_distance, fare_amount, tip_amount, total_amount)
            """
        )
        source_label = "synthetic sample"
    else:
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                *,
                dayofweek(tpep_pickup_datetime) IN (0, 6) AS is_weekend,
                tip_amount / nullif(fare_amount, 0) AS tip_rate,
                CASE payment_type
                    WHEN 1 THEN 'Credit card'
                    WHEN 2 THEN 'Cash'
                    WHEN 3 THEN 'No charge'
                    WHEN 4 THEN 'Dispute'
                    ELSE 'Other'
                END AS payment
            FROM read_parquet(
                'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
            )
            """
        )
        source_label = "yellow_tripdata_2024-01.parquet"
    return connection, source_label


@app.cell(expand_output=True)
def _(EvidentialTable, connection, mo, source_label):
    sample_table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT
                    tpep_pickup_datetime AS pickup,
                    payment,
                    passenger_count,
                    trip_distance,
                    fare_amount,
                    tip_amount,
                    total_amount,
                    tip_rate
                FROM trips
                WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01'
                ORDER BY tpep_pickup_datetime
                LIMIT 5000
                """
            ),
            title="Recent yellow taxi trips",
            subtitle=f"`{source_label}`",
            #search=True,
            #page_size=15,
            #row_shading=True,
            #freeze_columns=2,
            #max_height="520px",
            #columns=[
            #    col.date("pickup", fmt="shortdate", title="Pickup"),
            #    col.text("payment"),
            #    col.integer("passenger_count", fmt="id", title="Pax"),
            #    col.bar("trip_distance", format="num1", title="Distance", label=True),
            #    col.currency("fare_amount", decimals=2),
            #    col.bar("tip_amount", format="usd2", title="Tip", label=True),
            #    col.currency("total_amount", decimals=2, title="Total"),
            #    col.percent("tip_rate", decimals=1, title="Tip rate").color(
            #        scale=["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"], midpoint=0.15, min=0, max=0.4
            #    ),
            #],
        )
    )
    sample_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Grouped, collapsible totals

    `grouped_table` runs a single DuckDB `GROUPING SETS` query and tags each
    row with the metadata the widget needs to render collapsible groups,
    subtotals and a grand total. Click a subtotal row to collapse it.
    """)
    return


@app.cell
def _(col, connection, grouped_table, mo):
    grouped = mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT * FROM trips WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01'",
            dimensions=["payment", "is_weekend"],
            measures=[
                "count(*) AS trips",
                "round(sum(trip_distance), 0) AS distance",
                "round(sum(total_amount), 0) AS revenue",
                "round(avg(tip_rate) * 100, 1) AS avg_tip_pct",
            ],
            total_label="All trips",
            subtotal_position="top",
            title="Trips by payment type and weekend",
            search=True,
            max_height="460px",
            dimension_config={
                "is_weekend": col.boolean("is_weekend", title="Weekend"),
            },
            measure_config={
                "trips": col.integer("trips"),
                "distance": col.bar("distance", format='num0', label=True),
                "revenue": col.currency("revenue", decimals=0),
                "avg_tip_pct": col.number("avg_tip_pct", fmt="num1", title="Avg tip %"),
            },
        )
    )
    grouped
    return


@app.cell
def _(mo):
    mo.md("""
    ## Hierarchical (grouped) columns

    A pivot puts each payment type in its own column; `column_groups` wraps the
    pivoted columns under shared headers. The leading `month` column is left
    ungrouped and keeps its place.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    pivoted = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT
                    date_trunc('day', tpep_pickup_datetime)         AS day,
                    count(*) FILTER (WHERE payment = 'Credit card') AS credit_card,
                    count(*) FILTER (WHERE payment = 'Cash')        AS cash,
                    count(*) FILTER (WHERE payment = 'No charge')   AS no_charge,
                    count(*) FILTER (WHERE payment = 'Dispute')     AS dispute,
                    count(*)                                        AS 'total.trips',
                    round(sum(total_amount), 0)                     AS total_revenue
                FROM trips
                WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01'
                GROUP BY ALL
                ORDER BY day
                """
            ),
            title="Monthly trips pivoted by payment type",
            search=True,
            row_shading=True,
            columns=[
                col.date("day", fmt="yyyy-mm-dd", title="Day"),
                col.group(
                    "Payment type",
                    [
                        col.bar("credit_card", title="Credit card", format='num0', label=True),
                        col.bar("cash", title="Cash", format='num0', label=True),
                        col.bar("no_charge", title="No charge", format='num0', label=True),
                        col.bar("dispute", title="Dispute", format='num0', label=True),
                    ],
                ),
                col.group(
                    "Totals",
                    [
                        col.integer("total.trips", title="Total trips"),
                        col.currency("total_revenue", decimals=0, title="Revenue"),
                    ],
                ),
            ],
        )
    )
    pivoted
    return


if __name__ == "__main__":
    app.run()
