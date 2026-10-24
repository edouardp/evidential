# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "boto3>=1.35",
#     "evidential",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import os

    import marimo as mo

    from evidential import EvidentialTable, col, duck, grouped_table

    return EvidentialTable, col, duck, grouped_table, mo, os


@app.cell
def _(mo):
    mo.md("""
    # Amazon S3 Tables + Evidence-style grouped tables

    DuckDB's `iceberg` extension speaks the Iceberg REST protocol, and
    S3 Tables exposes a REST endpoint. `evidential.duck.connect_s3_tables()`
    builds an S3 secret from your ambient AWS credentials and `ATTACH`es the
    table bucket, so you can query it with plain SQL.

    Set `S3TABLES_TABLE_BUCKET_ARN` (and `AWS_PROFILE` / `AWS_REGION`) before
    running. This notebook is a companion to the
    [s3-tables](https://github.com/edouardp/s3-tables) playground, where the
    public NYC TLC data is ingested into a table bucket.
    """)
    return


@app.cell
def _(duck, mo, os):
    table_bucket_arn = os.environ.get("S3TABLES_TABLE_BUCKET_ARN")
    if table_bucket_arn:
        connection = duck.connect_s3_tables(table_bucket_arn=table_bucket_arn)
        status = mo.md(f"Connected to **{table_bucket_arn}**.")
    else:
        connection = None
        status = mo.callout(
            mo.md(
                "Set `S3TABLES_TABLE_BUCKET_ARN` to an S3 Tables table bucket ARN "
                "(plus `AWS_PROFILE`/`AWS_REGION`) to run this notebook."
            ),
            kind="warn",
        )
    status
    return (connection,)


@app.cell
def _(connection, mo):
    mo.stop(connection is None, mo.md(""))

    available = connection.sql("SHOW ALL TABLES")
    mo.vstack(
        [
            mo.md("**Tables visible through the S3 Tables catalog**"),
            mo.ui.table(available, selection=None, pagination=True, page_size=10),
        ]
    )
    return


@app.cell
def _(connection, mo):
    mo.stop(connection is None, mo.md(""))

    monthly = connection.sql(
        """
        SELECT
            date_trunc('day', tpep_pickup_datetime) AS pickup_day,
            CASE payment_type
                WHEN 1 THEN 'Credit card'
                WHEN 2 THEN 'Cash'
                WHEN 3 THEN 'No charge'
                WHEN 4 THEN 'Dispute'
                ELSE 'Other'
            END AS payment,
            count(*) AS trips,
            round(sum(trip_distance), 0) AS distance,
            round(sum(total_amount), 0) AS revenue
        FROM s3tables.taxi.yellow_trips
        WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01'
          AND tpep_pickup_datetime < TIMESTAMP '2024-02-01'
        GROUP BY ALL
        """
    )
    return (monthly,)


@app.cell
def _(EvidentialTable, col, mo, monthly):
    mo.ui.anywidget(
        EvidentialTable(
            monthly,
            title="Yellow taxi — daily totals",
            search=True,
            page_size=15,
            row_shading=True,
            max_height="480px",
            columns=[
                col.date("pickup_day", fmt="date", title="Day"),
                col.text("payment"),
                col.bar("distance", format='num0', label=True),
                col.currency("revenue", decimals=0),
                col.integer("trips"),
            ],
        )
    )
    return


@app.cell
def _(col, connection, grouped_table, mo):
    mo.stop(connection is None, mo.md(""))

    mo.ui.anywidget(
        grouped_table(
            connection,
            """
            SELECT
                CASE payment_type
                    WHEN 1 THEN 'Credit card'
                    WHEN 2 THEN 'Cash'
                    WHEN 3 THEN 'No charge'
                    WHEN 4 THEN 'Dispute'
                    ELSE 'Other'
                END AS payment,
                date_trunc('month', tpep_pickup_datetime) AS pickup_month,
                trip_distance,
                total_amount
            FROM s3tables.taxi.yellow_trips
            WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01'
              AND tpep_pickup_datetime < TIMESTAMP '2024-02-01'
            """,
            dimensions=["payment", "pickup_month"],
            measures=[
                "count(*) AS trips",
                "round(sum(trip_distance), 0) AS distance",
                "round(sum(total_amount), 0) AS revenue",
            ],
            total_label="All payments",
            subtotal_position="top",
            title="Trips by payment type and month",
            collapsible=True,
            collapsed=False,
            max_height="520px",
            dimension_config={"pickup_month": col.date("pickup_month", fmt="mmm-yy", title="Month")},
            measure_config={
                "trips": col.integer("trips"),
                "distance": col.integer("distance"),
                "revenue": col.bar("revenue", format='usd0', color="#8888ff66", label=True),
            },
        )
    )
    return


if __name__ == "__main__":
    app.run()
