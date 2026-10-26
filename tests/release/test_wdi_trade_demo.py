"""The WDI trade chart queries paired measures without conflating missing and zero."""

import runpy
from pathlib import Path
from types import SimpleNamespace

import duckdb
import pytest

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks" / "23_wdi.py"


@pytest.fixture
def trade_connection():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE country AS SELECT * FROM (VALUES
                ('AAA', 'Alpha', 'North'), ('BBB', 'Beta', 'South'),
                ('ZER', 'Zero', 'North'), ('NUL', 'Unreported', 'North'),
                ('GDP', 'Unrelated', 'North'), ('WLD', 'World', NULL)
            ) AS t("Country Code", "Short Name", Region);
            CREATE TABLE observations AS SELECT * FROM (VALUES
                ('AAA', 'NE.IMP.GNFS.CD', 2023, 200e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2023, 100e9),
                ('BBB', 'NE.EXP.GNFS.CD', 2023, 400e9),
                ('ZER', 'NE.IMP.GNFS.CD', 2023, 0),
                ('ZER', 'NE.EXP.GNFS.CD', 2023, 0),
                ('NUL', 'NE.IMP.GNFS.CD', 2023, NULL),
                ('GDP', 'NY.GDP.MKTP.CD', 2023, 500e9),
                ('WLD', 'NE.IMP.GNFS.CD', 2023, 900e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2022, 90e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2022, 80e9)
            ) AS t(country_code, indicator_code, year, value)
        """)
        yield connection


def test_trade_chart_reads_both_measures_and_retains_partial_data(trade_connection):
    _, definitions = runpy.run_path(str(NOTEBOOK))["trade_comparison"].run(connection=trade_connection)
    table = definitions["trade_balance"]
    assert table.rows == []  # Creation is independent of the filter controls.
    table.set_controls(year=2023, region="All regions")
    assert [row["country"] for row in table.rows] == ["Beta", "Alpha", "Zero"]
    by_country = {row["country"]: row for row in table.rows}
    assert by_country["Alpha"]["imports"] == 200e9
    assert by_country["Alpha"]["exports"] == 100e9
    assert by_country["Alpha"]["exports_imports_ratio"] == 0.5
    assert by_country["Alpha"]["net_exports"] == -100e9
    assert by_country["Alpha"]["total_trade"] == 300e9
    assert by_country["Beta"]["imports"] is None
    assert by_country["Beta"]["exports"] == 400e9
    assert by_country["Beta"]["exports_imports_ratio"] is None
    assert by_country["Beta"]["net_exports"] is None
    assert by_country["Beta"]["total_trade"] == 400e9
    assert by_country["Zero"]["imports"] == by_country["Zero"]["exports"] == 0
    assert by_country["Zero"]["exports_imports_ratio"] is None
    assert by_country["Zero"]["net_exports"] == 0
    marks = table.columns[1]
    assert [(enc["source"], enc["side"]) for enc in marks["encodings"]] == [("imports", "left"), ("exports", "right")]
    assert all(enc["label"]["auto"] for enc in marks["encodings"])
    assert marks["references"][0]["value"] == 0
    assert marks["sort_by"] == "total_trade"
    columns = {column["name"]: column for column in table.columns}
    assert columns["exports_imports_ratio"]["color_options"]["midpoint"] == 1
    assert columns["net_exports"]["color_options"]["midpoint"] == 0
    assert columns["total_trade"]["fmt"] == "compact"


def test_trade_filters_requery_the_same_widget_using_the_selected_year_and_region(trade_connection):
    namespace = runpy.run_path(str(NOTEBOOK))
    _, definitions = namespace["trade_comparison"].run(connection=trade_connection)
    table = definitions["trade_balance"]
    model_id = table.model_id
    namespace["update_trade"].run(
        trade_balance=table, year=SimpleNamespace(value=2023), region=SimpleNamespace(value="North")
    )
    assert [row["country"] for row in table.rows] == ["Alpha", "Zero"]
    namespace["update_trade"].run(
        trade_balance=table, year=SimpleNamespace(value=2022), region=SimpleNamespace(value="All regions")
    )
    assert table.model_id == model_id
    assert len(table.rows) == 1
    assert table.rows[0]["imports"] == 90e9 and table.rows[0]["exports"] == 80e9
    assert table.options["title"] == "Imports versus exports · 2022"
    table.set_controls(year=2021, region="All regions")
    assert table.rows == []
