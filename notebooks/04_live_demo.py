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
    # LiveEvidenceTable demo

    A `LiveEvidenceTable` keeps a **parameterised SQL query** and re-runs it when
    its controls change — without recreating the widget, so sort, search and page
    state survive. Values are bound as query parameters, never spliced into SQL.

    Move the slider or change either dropdown below and watch the table update
    in place. (Try sorting the *Fare* column first — the sort survives the
    update.)
    """)
    return


@app.cell
def _(duckdb, mo):
    is_script_mode = mo.app_meta().mode == "script"

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs; LOAD httpfs;")

    if is_script_mode:
        # Offline sample so the notebook is fast and deterministic in CI.
        connection.execute(
            """
            CREATE TABLE trips AS
            SELECT
                *,
                tip_amount / nullif(fare_amount, 0) AS tip_rate
            FROM (VALUES
                (TIMESTAMP '2024-01-01 05:12:00', 'Credit card', 2.4,  12.5, 3.1),
                (TIMESTAMP '2024-01-01 08:31:00', 'Cash',        7.8,  24.0, 0.0),
                (TIMESTAMP '2024-01-01 13:02:00', 'Credit card', 1.2,   9.0, 2.2),
                (TIMESTAMP '2024-01-01 19:41:00', 'Dispute',    12.1,  41.0, 9.5),
                (TIMESTAMP '2024-01-02 22:15:00', 'Cash',        4.9,  18.0, 0.0)
            ) AS v(pickup, payment, trip_distance, fare_amount, tip_amount)
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
                trip_distance,
                fare_amount,
                tip_amount,
                tip_amount / nullif(fare_amount, 0) AS tip_rate
            FROM read_parquet(
                'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
            )
            LIMIT 300000
            """
        )
    return (connection,)


@app.cell
def _(connection, mo, query_values):
    min_fare = mo.ui.slider(0, 80, value=10, label="Minimum fare ($)")
    payment = mo.ui.dropdown(
        ["All", *query_values(connection, "SELECT DISTINCT payment FROM trips ORDER BY 1")],
        value="All",
        label="Payment type",
    )
    part = mo.ui.dropdown(
        ["All", "Night", "Morning", "Afternoon", "Evening"],
        value="All",
        label="Time of day",
    )
    mo.hstack([min_fare, payment, part], justify="start", gap=2)
    return min_fare, part, payment


@app.cell
def _(LiveEvidenceTable, connection):
    # Created once, with no references to the controls, so changing a control
    # never recreates the widget (and never resets sort/search/page).
    live = LiveEvidenceTable(
        connection,
        """
        WITH enriched AS (
            SELECT
                *,
                CASE
                    WHEN extract(hour FROM pickup) < 6 THEN 'Night'
                    WHEN extract(hour FROM pickup) < 12 THEN 'Morning'
                    WHEN extract(hour FROM pickup) < 18 THEN 'Afternoon'
                    ELSE 'Evening'
                END AS part_of_day
            FROM trips
        )
        SELECT
            strftime(pickup, '%a %H:%M') AS pickup,
            payment,
            part_of_day,
            trip_distance,
            fare_amount,
            tip_amount,
            tip_rate
        FROM enriched
        WHERE fare_amount >= {min_fare}
          AND ({payment} = 'All' OR payment = {payment})
          AND ({part} = 'All' OR part_of_day = {part})
        ORDER BY fare_amount DESC
        LIMIT 500
        """,
        auto_run=False,
        title="Filtered taxi trips",
        search=True,
        page_size=12,
        row_shading=True,
        freeze_columns=1,
        column_config={
            "pickup": {"title": "Pickup", "align": "left"},
            "payment": {"title": "Payment", "align": "left"},
            "part_of_day": {"title": "Time of day", "align": "left"},
            "trip_distance": {"title": "Distance", "fmt": "num1", "viz": "bar"},
            "fare_amount": {"title": "Fare", "fmt": "usd2"},
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
def _(live, min_fare, part, payment):
    # Reactive cell: re-runs when any control changes and pushes fresh rows into
    # the persistent widget.
    _ = live.set_controls(min_fare=min_fare, payment=payment, part=part)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ### How it works

    - The widget is created in its own cell (`auto_run=False`) so it is **not**
      tied to the controls and is never recreated.
    - A separate reactive cell reads the controls' values and calls
      `set_controls(...)`; Marimo re-runs that cell whenever a control changes,
      pushing fresh rows into the persistent widget.
    - `{min_fare}`, `{payment}` and `{part}` are placeholders filled with bound
      query parameters.
    - `query_values(connection, "SELECT DISTINCT ...")` populated the payment
      dropdown from the data — the basis for cascading drill-down selectors.
    """)
    return


if __name__ == "__main__":
    app.run()
