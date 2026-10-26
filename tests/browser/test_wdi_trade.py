"""Render the WDI notebook's paired trade bars and derived comparisons."""

import runpy
from pathlib import Path

import duckdb
import pytest
from test_spec_conformance import capture, mount

pytestmark = pytest.mark.browser


def test_trade_demo_uses_shared_zero_compact_amounts_and_surplus_deficit_colors(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "23_wdi.py"
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE country AS SELECT * FROM (VALUES
                ('AAA', 'Alpha', 'North'), ('BBB', 'Beta', 'South'),
                ('CCC', 'Partial', 'North')
            ) AS t("Country Code", "Short Name", Region);
            CREATE TABLE observations AS SELECT * FROM (VALUES
                ('AAA', 'NE.IMP.GNFS.CD', 2023, 234.5e9),
                ('AAA', 'NE.EXP.GNFS.CD', 2023, 1.7e12),
                ('BBB', 'NE.IMP.GNFS.CD', 2023, 1.7e12),
                ('BBB', 'NE.EXP.GNFS.CD', 2023, 234.5e9),
                ('CCC', 'NE.EXP.GNFS.CD', 2023, 90e9)
            ) AS t(country_code, indicator_code, year, value)
        """)
        _, definitions = runpy.run_path(str(notebook))["trade_comparison"].run(connection=connection)
        table = definitions["trade_balance"]
        table.set_controls(year=2023, region="All regions")
        mount(page, live_server, [("WDI trade", table, [])])
        page.locator("section").evaluate("el => el.style.width = '1100px'")
        rows = page.locator("tbody tr")
        for index in range(2):
            track = rows.nth(index).locator(".et-marks").bounding_box()
            left = rows.nth(index).locator(".et-mark-bar-left").bounding_box()
            right = rows.nth(index).locator(".et-mark-bar-right").bounding_box()
            assert left["x"] + left["width"] == pytest.approx(track["x"] + track["width"] / 2, abs=1)
            assert right["x"] == pytest.approx(track["x"] + track["width"] / 2, abs=1)
            ratio = 234.5e9 / 1.7e12 if index == 0 else 1.7e12 / 234.5e9
            assert left["width"] == pytest.approx(right["width"] * ratio, abs=1)
            assert rows.nth(index).locator(".et-mark-label-text").all_text_contents() == [
                "234.5B" if index == 0 else "1.7T",
                "1.7T" if index == 0 else "234.5B",
            ]
        assert rows.nth(2).locator(".et-mark-bar").count() == 1
        assert rows.nth(0).locator("td").nth(2).inner_text() == "724.9%"
        assert rows.nth(1).locator("td").nth(3).inner_text() == "-1.5T"
        for column in (2, 3):
            surplus = rows.nth(0).locator("td").nth(column).evaluate("el => getComputedStyle(el).backgroundColor")
            deficit = rows.nth(1).locator("td").nth(column).evaluate("el => getComputedStyle(el).backgroundColor")
            assert surplus != deficit
        assert rows.nth(2).locator("td").nth(2).inner_text() == "–"
        assert rows.nth(2).locator("td").nth(3).inner_text() == "–"
        geometry = page.locator(".et-scroller").evaluate("el => [el.clientWidth, el.scrollWidth]")
        assert geometry[1] <= geometry[0] + 1
        capture(page, "wdi-trade.png")
