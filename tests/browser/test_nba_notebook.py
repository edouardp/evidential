"""Drive NBA filters and linked tables through marimo's widget connection."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/53_nba_shooting.py"


def test_player_selection_season_phase_and_team_filters_keep_stable_tables(page, nba_dataset, monkeypatch):
    monkeypatch.setenv("NBA_DATASET", str(nba_dataset))
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        roots = page.locator('[data-cell-name="tables"] .et-root')
        expect(roots).to_have_count(3, timeout=30000)
        players, zones, games = roots.nth(0), roots.nth(1), roots.nth(2)
        expect(players.locator("tbody tr")).to_have_count(2)
        expect(zones.locator(".et-empty-body")).to_be_visible()
        players.get_by_role("searchbox").fill("Alpha")
        players.locator("tbody tr").click()
        expect(zones.locator("tbody tr")).to_have_count(1)
        expect(games.locator("tbody tr")).to_have_count(1)
        expect(games.locator(".et-mark-label-text")).to_have_text("150.0%")
        players.evaluate("el => el.dataset.originalWidget = 'yes'")
        zones.evaluate("el => el.dataset.originalWidget = 'yes'")
        games.evaluate("el => el.dataset.originalWidget = 'yes'")
        page.get_by_role("combobox").nth(1).select_option(label="Playoffs")
        expect(players.locator(".et-title")).to_contain_text("Playoffs")
        expect(games.locator("tbody")).to_contain_text("2026-04-01")
        page.get_by_role("combobox").nth(0).select_option(label="2024–25")
        expect(players.locator(".et-title")).to_contain_text("2024–25")
        expect(games.locator("tbody tr")).to_have_count(3)
        page.get_by_role("combobox").nth(2).select_option(label="North")
        expect(games.locator("tbody tr")).to_have_count(2)
        expect(players.get_by_role("searchbox")).to_have_value("Alpha")
        assert all(root.get_attribute("data-original-widget") == "yes" for root in roots.all())
        minimum = page.locator('[data-cell-name="season_control"] input').first
        minimum.fill("5000")
        minimum.press("Enter")
        minimum.press("Tab")
        expect(players.locator(".et-empty-body")).to_be_visible()
        expect(zones.locator(".et-empty-body")).to_be_visible()
        expect(games.locator(".et-empty-body")).to_be_visible()
