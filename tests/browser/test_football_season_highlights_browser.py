"""The SQL-colored season bar demo renders twenty complete teams offline."""

from pathlib import Path

import duckdb
import pytest
from paint_helpers import painted_colors
from playwright.sync_api import expect

from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/60_football_season_highlights.py"


def test_sql_colors_render_twenty_teams_and_explain_highlighted_matches(page, monkeypatch, tmp_path):
    monkeypatch.setenv("FOOTBALL_PARQUET", str(tmp_path / "missing.parquet"))
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        root = page.locator(".et-root")
        expect(root.locator("tbody tr")).to_have_count(20, timeout=30_000)
        expect(root.locator("tbody .et-sparkline rect")).to_have_count(760)
        first_cells = root.locator("tbody tr").first.locator("td")
        win_color, loss_color = painted_colors(page, [first_cells.nth(7), first_cells.nth(8)])
        assert win_color[2] > win_color[0]  # Blue for the biggest win.
        assert loss_color[0] > loss_color[2]  # Red for the heaviest loss.
        assert root.locator('tbody rect[fill="#2166ac"]').count() >= 20
        assert root.locator('tbody rect[fill="#b2182b"]').count() >= 20
        row = root.locator("tbody tr").filter(has_text="Nottingham Forest")
        expect(row.locator(".et-sparkline rect")).to_have_count(38)
        row.locator('rect[fill="#2166ac"]').first.hover(force=True)
        tip = root.locator(".et-tooltip")
        expect(tip).to_be_visible()
        expect(tip.locator(".et-tooltip-name")).to_contain_text("Brighton")
        expect(tip.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("7")
        expect(tip.locator(".et-tooltip-detail")).to_have_text(["Score: 7–0", "Highlight: Biggest win"])
        expect(tip.locator(".et-tooltip-swatch")).to_have_css("background-color", "rgb(33, 102, 172)")
        root.get_by_role("searchbox").fill("Nottingham")
        expect(root.locator("tbody tr")).to_have_count(1)
        expect(row.locator(".et-sparkline rect")).to_have_count(38)
        expect(row.locator('rect[fill="#2166ac"]')).to_have_count(1)
        sql_cell = page.locator('[data-cell-name="sql_explanation"]')
        sql_cell.scroll_into_view_if_needed()
        page.get_by_text("Show the query used by this table", exact=True).click()
        query = page.get_by_role("region", name="Show the query used by this table")
        expect(query.locator("pre")).to_contain_text("MAX(margin) OVER (PARTITION BY team_id)")


def test_league_year_and_calendar_controls_update_the_same_widget(page, monkeypatch, tmp_path):
    parquet = tmp_path / "leagues.parquet"
    with duckdb.connect() as connection:
        connection.execute("""CREATE TABLE games AS SELECT * FROM (VALUES
            ('Alpha','Beta','Alpha (England)','Beta (England)',DATE '2024-08-01',2,0,'england','national'),
            ('Beta','Alpha','Beta (England)','Alpha (England)',DATE '2025-02-01',1,1,'england','national'),
            ('Alpha','Beta','Alpha (England)','Beta (England)',DATE '2025-08-01',0,3,'england','national'),
            ('Rouge','Bleu','Rouge (France)','Bleu (France)',DATE '2023-08-01',4,0,'france','national'),
            ('Rouge','Bleu','Rouge (France)','Bleu (France)',DATE '2024-08-01',1,0,'france','national'),
            ('Bleu','Rouge','Bleu (France)','Rouge (France)',DATE '2025-02-01',0,2,'france','national'),
            ('Rouge','Bleu','Rouge (France)','Bleu (France)',DATE '2025-08-01',0,5,'france','national')
        ) AS t(home,away,home_ident,away_ident,date,gh,ga,competition,level)""")
        connection.execute("COPY games TO ? (FORMAT PARQUET)", [str(parquet)])
    monkeypatch.setenv("FOOTBALL_PARQUET", str(parquet))
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        root = page.locator(".et-root")
        expect(root.locator(".et-title")).to_have_text("England · 2024/25", timeout=30_000)
        expect(root.locator("tbody rect")).to_have_count(4)
        root.evaluate("el => el.dataset.originalWidget = 'yes'")
        controls = page.get_by_role("combobox")
        controls.nth(2).select_option(label="2025/26")
        expect(root.locator(".et-title")).to_have_text("England · 2025/26")
        expect(root.locator("tbody rect")).to_have_count(2)
        controls.nth(0).select_option(label="France")
        expect(root.locator(".et-title")).to_have_text("France · 2024/25")
        expect(root.locator("tbody tr")).to_have_count(2)
        root.get_by_role("searchbox").fill("Rouge")
        expect(root.locator("tbody tr")).to_have_count(1)
        controls.nth(2).select_option(label="2023/24")
        expect(root.locator(".et-title")).to_have_text("France · 2023/24")
        expect(root.locator("tbody rect")).to_have_count(1)
        expect(root.locator("tbody rect")).to_have_attribute("fill", "#2166ac")
        controls.nth(1).select_option(label="Calendar year")
        expect(root.locator(".et-title")).to_have_text("France · 2024")
        controls.nth(2).select_option(label="2025")
        expect(root.locator(".et-title")).to_have_text("France · 2025")
        expect(root.locator("tbody rect")).to_have_count(2)
        expect(root.locator('tbody rect[fill="#b2182b"]')).to_have_count(1)
        expect(root.locator('tbody rect[fill="#2166ac"]')).to_have_count(1)
        expect(root.locator(".et-caption")).to_contain_text("2025-02-01 to 2025-08-01")
        expect(root.get_by_role("searchbox")).to_have_value("Rouge")
        assert root.get_attribute("data-original-widget") == "yes"
