"""The bundled skill templates render and interact through real marimo kernels."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
ASSETS = Path(__file__).resolve().parents[2] / "skills/evidential/assets"


def test_skill_report_template_renders_detail_annotations_and_footnotes(page):
    with _server(ASSETS / "report.py") as url:
        page.goto(url, wait_until="networkidle")
        report = page.locator('[data-cell-name="report"] .et-root')
        expect(report.locator("tbody tr.et-row-section")).to_have_count(2, timeout=30000)
        expect(report.locator("tbody tr.et-row-subtotal")).to_have_count(2)
        expect(report.locator("tbody tr.et-row-total")).to_contain_text("$5,400")
        expect(report.locator("tbody sup")).to_have_count(1)
        expect(report.locator(".et-footnotes-list")).to_contain_text("Launch month.")


def test_skill_explorer_template_keeps_widgets_and_clears_filtered_selection(page):
    with _server(ASSETS / "explorer.py") as url:
        page.goto(url, wait_until="networkidle")
        summary = page.locator('[data-cell-name="summary"] .et-root')
        detail = page.locator('[data-cell-name="detail"] .et-root')
        expect(summary.locator("tbody tr")).to_have_count(3, timeout=30000)
        expect(page.locator("body")).not_to_contain_text("DuckDBPyConnection")
        expect(detail.locator(".et-empty-body")).to_be_visible()
        summary.get_by_role("searchbox").fill("Desk")
        summary.locator("tbody tr").click()
        expect(detail.locator("tbody tr")).to_have_count(2)
        expect(detail.locator(".et-title")).to_have_text("Desk · Monthly detail")
        summary.evaluate("el => el.dataset.originalWidget = 'yes'")
        detail.evaluate("el => el.dataset.originalWidget = 'yes'")
        summary.get_by_role("searchbox").fill("")
        slider = page.get_by_role("slider")
        slider.focus()
        slider.press("End")
        expect(summary.locator(".et-empty-body")).to_be_visible()
        expect(detail.locator(".et-empty-body")).to_be_visible()
        slider.press("Home")
        expect(summary.locator("tbody tr")).to_have_count(3)
        expect(detail.locator(".et-empty-body")).to_be_visible()
        assert summary.get_attribute("data-original-widget") == "yes"
        assert detail.get_attribute("data-original-widget") == "yes"
