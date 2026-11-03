"""The SQL-colored season bar demo renders twenty complete teams offline."""

from pathlib import Path

import pytest
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
