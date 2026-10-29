"""The CUR explorer preserves source cost semantics and linked-filter totals."""

import runpy
from pathlib import Path

import duckdb
import pytest

from evidential import DimensionGrid

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/57_aws_cur_explorer.py"


@pytest.fixture
def loaded(aws_cur_dataset):
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, duckdb=duckdb)
    con = helpers["load_cur"](aws_cur_dataset / "data/processed/cur_line_items.parquet")
    yield con, helpers
    con.close()


def test_amortized_cost_uses_reserved_effective_cost_and_retains_fee_rows(loaded):
    con, helpers = loaded
    results = helpers["query_cur"](con)
    assert results["summary"]["amortized_cost"] == 46
    assert results["summary"]["unblended_cost"] == 34
    assert results["summary"]["line_items"] == 6
    assert con.sql("SELECT cost FROM cur_facets WHERE charge_type = 'DiscountedUsage'").fetchone()[0] == 12
    assert sum(row["amortized_cost"] for row in results["drivers"].to_pylist()) == 46
    assert sum(row["cost"] for row in con.table("cur_facets").to_arrow_table().to_pylist()) == 46


def test_service_and_tag_selections_filter_every_result_before_aggregation(loaded):
    con, helpers = loaded
    grid = DimensionGrid(con.table("cur_facets"), dimensions=helpers["cur_dimensions"], metric="cost")
    grid.selected = {"service": ["AmazonRDS"], "environment": ["prod"]}
    predicate, values = grid.where()
    result = helpers["query_cur"](con, predicate, values)
    assert result["summary"]["amortized_cost"] == 20
    assert result["summary"]["line_items"] == 2
    assert all(row["service"] == "AmazonRDS" for row in result["details"].to_pylist())
    assert sum(row["amortized_cost"] for row in result["drivers"].to_pylist()) == 20
    assert sum(row["share"] for row in result["drivers"].to_pylist()) == 1
    grid.selected = {"service": ["AmazonRDS", "AmazonEC2"], "environment": [None]}
    result = helpers["query_cur"](con, *grid.where())
    assert result["summary"]["amortized_cost"] == 5
    assert result["details"].to_pylist()[0]["charge_type"] == "RIFee"


def test_daily_trends_fill_calendar_gaps_and_keep_usage_units_separate(loaded):
    con, helpers = loaded
    rows = helpers["query_cur"](con)["drivers"].to_pylist()
    assert {row["unit"] for row in rows} == {"Hrs", "GB-Mo"}
    for row in rows:
        assert len(row["daily_cost"]) == 3
        assert row["daily_cost"][1]["value"] == 0
        assert sum(point["value"] for point in row["daily_cost"]) == row["amortized_cost"]


def test_empty_matches_are_empty_tables_and_zero_cards(loaded):
    con, helpers = loaded
    result = helpers["query_cur"](con, "service = ?", ["absent"])
    assert result["summary"]["amortized_cost"] == 0
    assert result["summary"]["line_items"] == 0
    assert result["drivers"].num_rows == result["details"].num_rows == 0
    with pytest.raises(ValueError, match="limit"):
        helpers["query_cur"](con, detail_limit=-1)


def test_detail_limit_does_not_limit_summary_or_driver_totals(loaded):
    con, helpers = loaded
    con.execute("CREATE TEMP TABLE expanded AS SELECT cur.* FROM cur CROSS JOIN range(100)")
    con.execute("CREATE OR REPLACE TEMP VIEW cur AS SELECT * FROM expanded")
    result = helpers["query_cur"](con, detail_limit=250)
    assert result["summary"]["line_items"] == 600
    assert result["summary"]["amortized_cost"] == 4600
    assert result["details"].num_rows == 250
    assert sum(row["amortized_cost"] for row in result["drivers"].to_pylist()) == 4600


def test_notebook_executes_with_local_product_and_creates_persistent_widgets(aws_cur_dataset, monkeypatch):
    monkeypatch.setenv("AWS_CUR_DATASET", str(aws_cur_dataset))
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    assert definitions["cur_summary"]["line_items"] == 6
    assert len(definitions["cur_slicer"].widget.facets) == 9
    assert len(definitions["cur_details"].widget.raw) == 6
    assert sum(row["amortized_cost"] for row in definitions["cost_drivers"].widget.raw) == 46
    account = next(column for column in definitions["cur_details"].widget.columns if column["name"] == "account")
    assert account["fmt"] == "000000000000"  # Account IDs must never become compact numbers.
    trend = next(column for column in definitions["cost_drivers"].widget.columns if column["name"] == "daily_cost")
    assert trend["sparkline_options"]["width"] == 160
    definitions["cur_connection"].close()
