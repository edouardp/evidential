"""Notebook 01 demonstrates fluent labels while keeping label placement explicit."""

import runpy
from pathlib import Path

import duckdb


def test_taxi_demo_runs_offline_with_fluent_label_placement():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE trips AS SELECT *,
                false AS is_weekend,
                tip_amount / fare_amount AS tip_rate
            FROM (VALUES
                (TIMESTAMP '2024-01-01', 'Credit card', 1, 2.5, 10.0, 2.0, 12.0),
                (TIMESTAMP '2024-01-02', 'Cash', 2, 3.0, 15.0, 0.0, 15.0),
                (TIMESTAMP '2024-01-03', 'No charge', 1, 1.0, 0.0, 0.0, 0.0),
                (TIMESTAMP '2024-01-04', 'Dispute', 1, 4.0, 20.0, 0.0, 20.0)
            ) AS t(tpep_pickup_datetime, payment, passenger_count, trip_distance,
                   fare_amount, tip_amount, total_amount)
        """)
        path = Path(__file__).resolve().parents[2] / "notebooks/01_taxi_explore.py"
        _, definitions = runpy.run_path(str(path))["app"].run(
            defs={
                "connection": connection,
                "source_label": "Offline test fixture",
                "is_script_mode": True,
            }
        )
    columns = {column["name"]: column for column in definitions["pivoted"].widget.columns}
    credit = columns["credit_card"]["encodings"][0]["label"]
    assert credit == {"value": True, "position": "outside_end", "auto": True}
    for name in ("cash", "no_charge", "dispute"):
        assert columns[name]["encodings"][0]["label"] == {
            "value": True,
            "position": "inside_end",
            "auto": False,
        }
    grouped = {column["name"]: column for column in definitions["grouped"].widget.columns}
    assert grouped["distance"]["encodings"][0]["label"] == {"value": True}
