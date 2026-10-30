"""GDP filters, quarter adjacency, honest missing periods and source units."""

import runpy
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
import pytest

from evidential import col

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/58_oecd_economic_cycles.py"


@pytest.fixture
def loaded(oecd_dataset):
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, col=col, duckdb=duckdb)
    con, sources, inventory = helpers["load_oecd"](oecd_dataset)
    yield con, sources, inventory, helpers
    con.close()


def states(con, code):
    return dict(
        con.execute(
            "SELECT year || '-Q' || quarter, category FROM gdp_quarters WHERE country_code = ?", [code]
        ).fetchall()
    )


def test_only_comparable_real_quarterly_gdp_is_used(loaded):
    con, _, _, _ = loaded
    assert con.sql("SELECT count(*) FROM gdp_observed WHERE country_code='USA'").fetchone()[0] == 11
    assert (
        con.sql(
            "SELECT growth_percent FROM gdp_observed WHERE country_code='USA' AND time_period='1960-Q1'"
        ).fetchone()[0]
        == -1
    )


def test_runs_include_first_quarter_isolated_falls_and_zero_do_not_qualify(loaded):
    con, _, _, _ = loaded
    usa = states(con, "USA")
    assert usa["1959-Q4"] == usa["1960-Q1"] == "recession"
    assert usa["1960-Q3"] == usa["1960-Q4"] == "other"
    assert usa["1961-Q1"] == usa["1961-Q4"] == "recession"


def test_missing_quarters_break_runs_and_never_become_zero_growth(loaded):
    con, _, _, helpers = loaded
    nzl = states(con, "NZL")
    assert nzl["1960-Q1"] == nzl["1960-Q3"] == "missing"
    assert nzl["1960-Q2"] == "other"
    assert nzl["1960-Q4"] == nzl["1961-Q1"] == "recession"
    quarters = helpers["query_quarters"](con, "NZL", 1960, 1960).to_pylist()
    assert quarters[1]["growth"] is None  # Q3: absent, not a zero.
    assert quarters[2]["growth"] == -0.005  # Percentage points are converted once for pct formatting.


def test_classification_precedes_date_clipping_and_intervals_cover_domain(loaded):
    con, _, _, helpers = loaded
    rows = helpers["query_timeline"](con, 1960, 1961).to_pylist()
    assert len(rows) == 2
    usa = next(row for row in rows if row["country_code"] == "USA")
    assert usa["periods"][0]["category"] == "recession"  # Confirmed by 1959-Q4.
    for row in rows:
        assert row["periods"][0]["start"] == 1960
        assert row["periods"][-1]["end"] == 1962
        assert sum(segment["quarters"] for segment in row["periods"]) == 8
        for first, second in zip(row["periods"], row["periods"][1:], strict=False):
            assert first["end"] == second["start"]
            assert first["category"] != second["category"]


def test_partial_boundary_years_show_unobserved_quarters_as_missing(loaded):
    con, _, _, helpers = loaded
    rows = helpers["query_timeline"](con, 1959, 1962).to_pylist()
    usa = next(row for row in rows if row["country_code"] == "USA")
    assert usa["periods"][0]["start"] == 1959
    assert usa["periods"][0]["end"] == 1959.75
    assert usa["periods"][0]["category"] == "missing"
    assert usa["periods"][-1]["start"] == 1962.5
    assert usa["periods"][-1]["end"] == 1963
    assert usa["periods"][-1]["category"] == "missing"
    assert sum(segment["quarters"] for segment in usa["periods"]) == 16


def test_aggregate_economies_are_opt_in(loaded):
    con, _, _, helpers = loaded
    assert helpers["query_timeline"](con, 1960, 1961, aggregates=True).num_rows == 3


def test_raw_source_browser_keeps_individual_series_and_restores_multiplier(loaded):
    con, sources, inventory, helpers = loaded
    rows = helpers["browse_source"](con, sources, "gov_finance", "NZL", 1960, 1962)
    currency = next(row for row in rows if row["unit_measure"] == "USD")
    assert currency["value"] == 12_500_000
    assert currency["unit"] == "US dollars"
    assert currency["frequency"] == "Annual"
    assert "General government" in currency["dimensions"]
    assert {row["file"] for row in inventory} == {
        "gdp_growth.parquet",
        "gov_finance.parquet",
        "gdp_quarterly_usd.parquet",
    }
    with pytest.raises(ValueError, match="available"):
        helpers["browse_source"](con, sources, "not_a_source", "NZL", 1960, 1962)


def test_duplicate_series_fail_instead_of_being_averaged(oecd_dataset):
    path = oecd_dataset / "data/processed/gdp_growth.parquet"
    table = pq.read_table(path)
    records = table.to_pylist()
    pq.write_table(type(table).from_pylist([*records, records[0]]), path)
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, col=col, duckdb=duckdb)
    with pytest.raises(ValueError, match="Multiple GDP"):
        helpers["load_oecd"](oecd_dataset)


def test_notebook_executes_against_local_product(oecd_dataset, monkeypatch):
    monkeypatch.setenv("OECD_DATASET", str(oecd_dataset))
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    assert len(definitions["cycle_table"].widget.raw) == 2
    assert definitions["selected_code"] == "NZL"
    assert definitions["quarterly"].widget.raw
    assert definitions["observations_table"].widget.raw
    assert definitions["cycle_table"].widget.columns[2]["scale"]["domain"] == (1960, 1963)
    share_colors = definitions["cycle_table"].widget.columns[-1]["color_options"]
    assert (share_colors["min"], share_colors["max"]) == (0, 1)
    definitions["oecd_connection"].close()


def test_context_uses_exact_year_annual_current_price_gdp_and_comparable_fiscal_ratios(loaded):
    con, _, _, helpers = loaded
    rows = helpers["query_timeline"](con, 1960, 1961).to_pylist()
    usa, nzl = rows
    assert usa["region"] == "Americas"
    assert nzl["region"] == "Oceania"
    assert usa["gdp_ppp"] == 100_000_000  # Neither a quarterly value nor constant-price GDP.
    assert nzl["gdp_ppp"] == 15_000_000
    assert nzl["debt_ratio"] == 0.35
    assert nzl["fiscal_ratio"] == -0.04
    assert "1961" in nzl["gdp_detail"]
    assert "15,000,000.00\n" in nzl["gdp_detail"]
    assert nzl["recession_share"] == 2 / 5  # Missing observations are not the denominator.
    assert "5 observed quarters (8 possible)" in nzl["coverage"]
    later = helpers["query_timeline"](con, 1960, 1962).to_pylist()[1]
    assert later["gdp_ppp"] is None  # Do not carry 1961 figures forward.
    assert later["debt_ratio"] is None


def test_context_is_optional_and_missing_sources_do_not_prevent_timeline(oecd_dataset):
    (oecd_dataset / "data/processed/gdp_quarterly_usd.parquet").unlink()
    (oecd_dataset / "data/processed/gov_finance.parquet").unlink()
    notebook = runpy.run_path(str(NOTEBOOK))
    _, helpers = notebook["queries"].run(Path=Path, col=col, duckdb=duckdb)
    con, _, _ = helpers["load_oecd"](oecd_dataset)
    rows = helpers["query_timeline"](con, 1960, 1961).to_pylist()
    assert len(rows) == 2
    assert all(row["gdp_ppp"] is None and row["fiscal_ratio"] is None for row in rows)
    con.close()
