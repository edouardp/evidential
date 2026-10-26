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
                ('AAA', 'NE.IMP.GNFS.CD', 2003, 50e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2003, 200e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2004, 50e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2004, 100e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2006, 0),
                ('AAA', 'NE.EXP.GNFS.CD', 2006, 100e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2007, 50e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2008, 50e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2008, 0),
                ('AAA', 'NE.IMP.GNFS.CD', 2022, 90e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2022, 80e9),
                ('AAA', 'NE.IMP.GNFS.CD', 2024, 10e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2024, 200e9)
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


def test_trade_history_covers_twenty_calendar_years_without_bridging_missing_values(trade_connection):
    _, definitions = runpy.run_path(str(NOTEBOOK))["trade_comparison"].run(connection=trade_connection)
    table = definitions["trade_balance"]
    table.set_controls(year=2023, region="North")
    row = next(row for row in table.rows if row["country"] == "Alpha")
    history = row["trade_history"]
    assert [point["year"] for point in history] == list(range(2004, 2024))
    by_year = {point["year"]: point["ratio"] for point in history}
    assert by_year[2004] == 2
    assert by_year[2005] is None  # Neither measure reported.
    assert by_year[2006] is None  # Zero denominator.
    assert by_year[2007] is None  # Missing exports.
    assert by_year[2008] == 0  # Zero exports is a valid ratio.
    assert by_year[2022] == pytest.approx(80 / 90)
    assert by_year[2023] == row["exports_imports_ratio"]
    assert all(point["ratio"] is None for point in table.rows[1]["trade_history"])
    sparkline = next(column for column in table.columns if column["name"] == "trade_history")
    assert sparkline["sparkline_options"]["x"] == "year"
    assert sparkline["sparkline_options"]["y"] == "ratio"
    assert sparkline["sparkline_options"]["y_fmt"] == "pct1"
    assert sparkline["sparkline_options"]["type"] == "area"
    assert sparkline["sparkline_options"]["signed"] is True
    assert sparkline["sparkline_options"]["reference"] == 1


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
    assert [point["year"] for point in table.rows[0]["trade_history"]] == list(range(2003, 2023))
    assert table.rows[0]["trade_history"][0]["ratio"] == 4
    assert table.rows[0]["trade_history"][-1]["ratio"] == pytest.approx(80 / 90)
    assert table.options["title"] == "Imports versus exports · 2022"
    table.set_controls(year=2021, region="All regions")
    assert table.rows == []
