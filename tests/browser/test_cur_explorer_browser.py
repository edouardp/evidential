"""The real CUR explorer links filters, cards and persistent result tables."""

import re

import pytest
from playwright.sync_api import expect

from scripts.api_screenshots import ROOT, _server

pytestmark = pytest.mark.browser


def test_cur_filters_multi_select_and_detail_limit_keep_persistent_widgets(page, aws_cur_dataset, monkeypatch):
    monkeypatch.setenv("AWS_CUR_DATASET", str(aws_cur_dataset))
    with _server(ROOT / "notebooks/57_aws_cur_explorer.py") as url:
        page.goto(url)
        grid = page.locator('[data-cell-name="cost_filters"] .edg-root')
        drivers = page.locator('[data-cell-name="drivers_table"] .et-root')
        details = page.locator('[data-cell-name="detail_table"] .et-root')
        cards = page.locator('[data-cell-name="summary_cards"]')
        expect(grid.locator(".edg-dimension")).to_have_count(9, timeout=30000)
        expect(details.locator("tbody tr")).to_have_count(6, timeout=30000)
        expect(cards).to_contain_text("$46.00")
        for root in [grid, drivers, details]:
            root.evaluate("el => el.dataset.originalWidget = 'yes'")
        service = grid.get_by_role("region", name="Service", exact=True)
        service.get_by_role("button", name=re.compile("Service: AmazonRDS,")).click()
        expect(details.locator("tbody tr")).to_have_count(3)
        expect(cards).to_contain_text("$25.00")
        usage = grid.get_by_role("region", name="Usage type", exact=True)
        expect(usage.locator(".edg-status")).to_have_text("1 available")
        assert all(text == "RDS:Instance" for text in usage.locator(".edg-category").all_text_contents())
        service.get_by_role("button", name=re.compile("Service: AmazonEC2,")).click()
        expect(details.locator("tbody tr")).to_have_count(6)
        expect(cards).to_contain_text("$46.00")
        environment = grid.get_by_role("region", name="Environment", exact=True)
        environment.get_by_role("button", name=re.compile("Environment: dev,")).click()
        expect(details.locator("tbody tr")).to_have_count(3)
        expect(cards).to_contain_text("$21.00")
        details.get_by_role("searchbox").fill("Compute")
        expect(details.locator("tbody tr")).to_have_count(2)
        page.get_by_role("combobox").select_option(label="250")
        expect(details.get_by_role("searchbox")).to_have_value("Compute")
        for root in [grid, drivers, details]:
            assert root.get_attribute("data-original-widget") == "yes"
