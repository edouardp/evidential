"""Company-report metrics retain fact grains, effective costs and honest periods."""

import datetime as dt
import json
import runpy
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/59_adventureworks_company_report.py"


@pytest.fixture
def loaded(adventureworks_dataset):
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, dt=dt, duckdb=duckdb)
    connection = helpers["load_adventureworks"](adventureworks_dataset)
    yield connection, helpers
    connection.close()


def metrics(report):
    return {row["metric"]: row for row in report["scorecard"]}


def test_reconciles_order_line_market_product_customer_and_monthly_grains(loaded):
    connection, helpers = loaded
    report, _ = helpers["query_report"](connection, 2024, "All channels")
    score = metrics(report)
    assert score["Net sales"]["current"] == 600
    assert score["Net sales"]["previous"] == 700
    assert score["Orders"]["current"] == 3
    assert score["Average order value"]["current"] == 200
    for name in ["monthly", "markets", "products", "customers", "countries", "fulfilment"]:
        assert sum(row["net_sales"] for row in report[name]) == pytest.approx(600)
    assert score["Est. gross contribution"]["current"] == 320
    assert score["Est. contribution margin"]["current"] == pytest.approx(320 / 600)
    assert report["quality"]["header_rounding_difference"] == 0
    assert connection.sql("SELECT net_sales FROM aw_orders WHERE order_id=1").fetchone()[0] == 200
    assert connection.sql("SELECT count(*) FROM aw_orders WHERE order_id=7").fetchone()[0] == 0


def test_historical_cost_intervals_fallback_and_unknown_cost_are_explicit(loaded):
    connection, helpers = loaded
    assert connection.sql("SELECT unit_cost FROM aw_lines WHERE order_id=1 AND product_id=1").fetchone()[0] == 20
    assert connection.sql("SELECT unit_cost FROM aw_lines WHERE order_id=3").fetchone()[0] == 80
    report, _ = helpers["query_report"](connection, 2024, "All channels")
    assert report["quality"]["fallback_sales"] == 200
    assert report["quality"]["missing_cost_sales"] == 0


def test_missing_cost_is_not_silently_zero_or_a_partial_group_total(adventureworks_dataset):
    directory = adventureworks_dataset / "data/processed/parquet"
    product_path = directory / "Product.parquet"
    product = pq.read_table(product_path)
    records = [
        {**row, "StandardCost": None if row["ProductID"] == 1 else row["StandardCost"]} for row in product.to_pylist()
    ]
    pq.write_table(pa.Table.from_pylist(records, schema=product.schema), product_path)
    history_path = directory / "ProductCostHistory.parquet"
    history = pq.read_table(history_path)
    pq.write_table(history.slice(0, 0), history_path)
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, dt=dt, duckdb=duckdb)
    connection = helpers["load_adventureworks"](adventureworks_dataset)
    try:
        report, _ = helpers["query_report"](connection, 2024, "All channels")
        assert metrics(report)["Est. gross contribution"]["current"] is None
        assert report["quality"]["missing_cost_sales"] == 400
        assert next(row for row in report["markets"] if row["territory"] == "Northwest")["margin"] is None
        assert next(row for row in report["products"] if row["category"] == "Bikes")["margin"] is None
    finally:
        connection.close()


def test_partial_periods_align_calendar_dates_and_missing_prior_coverage_is_not_zero(loaded):
    connection, helpers = loaded
    report, window = helpers["query_report"](connection, 2025, "All channels")
    assert window["end"] == dt.date(2025, 6, 29)
    assert window["prior_end"] == dt.date(2024, 6, 29)
    assert metrics(report)["Net sales"]["previous"] == 500
    assert metrics(report)["Net sales"]["change"] == pytest.approx(-0.9)
    assert len(report["monthly"]) == 6
    earliest, window = helpers["query_report"](connection, 2023, "All channels")
    assert not window["comparable"]
    assert all(row["previous"] is None and row["change"] is None for row in earliest["scorecard"])
    assert all(row["prior_sales"] is None for row in earliest["monthly"])


def test_channel_scope_does_not_reset_first_seen_and_prior_only_accounts_remain(loaded):
    connection, helpers = loaded
    online, _ = helpers["query_report"](connection, 2024, "Online")
    assert metrics(online)["Net sales"]["current"] == 500
    assert online["customers"][0]["cohort"] == "Previously observed"
    assert online["customers"][0]["customers"] == 2
    all_channels, _ = helpers["query_report"](connection, 2024, "All channels")
    dormant = next(row for row in all_channels["accounts"] if row["customer"] == "Dormant Cycles")
    assert dormant["net_sales"] == 0 and dormant["prior_sales"] == 400
    alpha = next(row for row in all_channels["accounts"] if row["customer"] == "Alpha Cycles")
    assert alpha["company_sales_share"] == pytest.approx(0.5)
    bike = next(row for row in all_channels["products"] if row["category"] == "Bikes")
    assert len(bike["monthly_sales"]) == 12
    assert bike["monthly_sales"][1]["value"] == 0
    assert sum(point["value"] for point in bike["monthly_sales"]) == bike["net_sales"]
    with pytest.raises(ValueError, match="sales channel"):
        helpers["query_report"](connection, 2024, "' OR true --")


def test_notebook_executes_with_real_widget_types_and_local_map_geometry(adventureworks_dataset, monkeypatch):
    monkeypatch.setenv("ADVENTUREWORKS_DATASET", str(adventureworks_dataset))
    namespace = runpy.run_path(str(NOTEBOOK))
    _, definitions = namespace["app"].run()
    try:
        assert definitions["default_year"] == 2024
        assert len(definitions["report_tables"]) == 7
        assert all(table.rows for table in definitions["report_tables"].values())
        monthly = next(
            column for column in definitions["report_tables"]["products"].columns if column["name"] == "monthly_sales"
        )
        assert monthly["sparkline_options"]["type"] == "area"
        assert monthly["sparkline_options"]["fill_opacity"] == (0, 0.6)
        assert definitions["country_map"].__class__.__name__ == "ObservablePlot"
        assert definitions["country_map"].version == "0.6.17"
        world = json.loads((NOTEBOOK.parent / "sample_data/adventureworks/world-110m.geojson").read_text())
        codes = {feature["properties"]["code"] for feature in world["features"]}
        assert {row["country_code"] for row in definitions["report_data"]["countries"]} <= codes
        assert definitions["parquet_directory"](adventureworks_dataset / "data/processed/parquet") is not None
    finally:
        definitions["con"].close()
