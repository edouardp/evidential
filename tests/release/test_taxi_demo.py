"""Notebook 01 demonstrates fluent labels and SQL-computed trip summaries."""

import runpy
from pathlib import Path

import duckdb
import pytest


def test_taxi_demo_runs_offline_with_fluent_label_placement():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE trips AS SELECT *,
                isodow(tpep_pickup_datetime) >= 6 AS is_weekend,
                tip_amount / nullif(fare_amount, 0) AS tip_rate
            FROM (VALUES
                (TIMESTAMP '2024-01-01', 'Credit card', 1, 2.5, 10.0, 2.0, 12.0),
                (TIMESTAMP '2024-01-02', 'Cash', 2, 3.0, 15.0, 0.0, 15.0),
                (TIMESTAMP '2024-01-03', 'No charge', 1, 1.0, 0.0, 0.0, 0.0),
                (TIMESTAMP '2024-01-04', 'Dispute', 1, 4.0, 20.0, 0.0, 20.0),
                (TIMESTAMP '2024-01-06', 'Credit card', 1, 1.0, 10.0, 0.0, 10.0),
                (TIMESTAMP '2024-01-07', 'Credit card', 1, 1.0, 10.0, 1.0, 11.0)
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
    assert credit["value"] is True
    assert credit["position"] == "outside_end" and credit["auto"] is True
    assert (credit.get("format") or columns["credit_card"].get("fmt")) == "num0"
    for name in ("cash", "no_charge", "dispute"):
        annotation = columns[name]["encodings"][0]["label"]
        assert annotation["value"] is True
        assert annotation["position"] == "inside_end" and annotation["auto"] is False
        assert (annotation.get("format") or columns[name].get("fmt")) == "num0"
    grouped = {column["name"]: column for column in definitions["grouped"].widget.columns}
    assert grouped["distance"]["encodings"][0]["label"]["value"] is True

    table = definitions["grouped"].widget
    summaries = {group["section"]["label"]: group["summary"]["cells"] for group in table.row_layout["groups"]}
    assert len(table.raw) == 5
    assert summaries["Credit card"]["trips"]["value"] == 3
    assert summaries["Credit card"]["avg_tip_pct"]["value"] == pytest.approx(10)
    assert summaries["No charge"]["avg_tip_pct"]["value"] is None
    assert table.row_layout["grand_summary"]["cells"]["avg_tip_pct"]["value"] == pytest.approx(6)
