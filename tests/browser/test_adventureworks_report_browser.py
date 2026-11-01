"""The full company report updates stable tables and its Observable Plot map."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/59_adventureworks_company_report.py"


def test_company_report_filters_folded_sections_and_observable_map(page, adventureworks_dataset, monkeypatch):
    monkeypatch.setenv("ADVENTUREWORKS_DATASET", str(adventureworks_dataset))
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        scorecard = page.locator('[data-cell-name="scorecard_view"] .et-root')
        markets = page.locator('[data-cell-name="markets_view"] .et-root')
        products = page.locator('[data-cell-name="products_view"] .et-root')
        accounts = page.locator('[data-cell-name="accounts_view"] .et-root')
        chart = page.locator('[data-cell-name="market_map"] .observable-plot-root')
        expect(scorecard.locator("tbody tr")).to_have_count(7, timeout=60_000)
        expect(scorecard.locator("tbody tr").first).to_contain_text("$600")
        expect(chart.locator('svg[width="1050"]')).to_be_visible(timeout=60_000)
        expect(chart.locator(".observable-plot-error")).not_to_be_visible()
        roots = page.locator(".et-root")
        expect(roots).to_have_count(7)
        for root in roots.all():
            root.evaluate("el => el.dataset.originalWidget = 'yes'")
        chart.evaluate("el => el.dataset.originalWidget = 'yes'")
        markets.get_by_role("button", name="Toggle section North America", exact=True).click()
        expect(markets.locator(".et-display-section").filter(has_text="North America")).to_contain_text("400")
        products.get_by_role("searchbox").fill("Road bikes")
        page.get_by_role("combobox").nth(1).select_option(label="Online")
        expect(scorecard.locator("tbody tr").first).to_contain_text("$500")
        expect(products.get_by_role("searchbox")).to_have_value("Road bikes")
        expect(markets.get_by_role("button", name="Toggle section North America", exact=True)).to_have_attribute(
            "aria-expanded", "false"
        )
        expect(accounts.locator("tbody")).to_contain_text("Alpha Cycles")
        page.get_by_role("combobox").nth(0).select_option(label="2025")
        expect(scorecard.locator(".et-subtitle")).to_contain_text("29 Jun 2025")
        expect(scorecard.locator("tbody tr").first).to_contain_text("$50")
        expect(scorecard.locator("tbody tr").first).to_contain_text("$500")
        expect(chart.locator('svg[width="1050"]')).to_be_visible()
        expect(chart.locator(".observable-plot-error")).not_to_be_visible()
        assert all(root.get_attribute("data-original-widget") == "yes" for root in roots.all())
        assert chart.get_attribute("data-original-widget") == "yes"
