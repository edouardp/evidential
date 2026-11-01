"""The local OECD product drives the timeline, context and persistent drilldown."""

import pytest
from paint_helpers import painted_colors
from playwright.sync_api import expect

from scripts.api_screenshots import ROOT, _server

pytestmark = pytest.mark.browser


def test_year_range_country_selection_and_source_browser(page, oecd_dataset, monkeypatch):
    monkeypatch.setenv("OECD_DATASET", str(oecd_dataset))
    with _server(ROOT / "notebooks/58_oecd_economic_cycles.py") as url:
        page.goto(url)
        timeline = page.locator('[data-cell-name="timeline"] .et-root')
        quarterly = page.locator('[data-cell-name="quarterly_table"] .et-root')
        observations = page.locator('[data-cell-name="observations_table"] .et-root')
        expect(timeline.locator(".et-strip-run").first).to_be_visible(timeout=60_000)
        expect(timeline.locator("tbody tr")).to_have_count(2)
        expect(quarterly.locator(".et-title")).to_contain_text("New Zealand", timeout=30_000)
        expect(timeline.locator(".et-legend-label")).to_have_text(
            ["In technical recession", "Not in technical recession", "No data"]
        )
        assert set(
            timeline.locator(".et-strip-run").evaluate_all("els => els.map(el => getComputedStyle(el).backgroundColor)")
        ) == {"rgb(197, 34, 40)", "rgb(146, 206, 224)", "rgb(211, 211, 211)"}
        assert timeline.locator(".et-axis-row-top").bounding_box()["y"] < timeline.locator("tbody").bounding_box()["y"]
        for root in [timeline, quarterly, observations]:
            root.evaluate("el => el.dataset.originalWidget = 'yes'")

        # Missing quarters have explicit intervals and useful source-period metadata.
        nzl = timeline.locator("tbody tr").filter(has_text="New Zealand")
        nzl.locator(".et-strip-run").first.hover()
        expect(timeline.locator(".et-tooltip")).to_contain_text("1960-Q1")
        page.get_by_role("combobox").select_option(label="Government finance")
        expect(observations.locator(".et-title")).to_contain_text("Government finance")
        expect(observations.locator("tbody tr")).to_have_count(3)
        expect(observations.locator("tbody")).to_contain_text("12.5M")
        expect(observations.locator("tbody")).to_contain_text("US dollars")

        # Same country, new date domain: annual context must use 1961, not latest data.
        maximum = page.get_by_role("slider", name="Maximum", exact=True)
        maximum.focus()
        maximum.press("ArrowLeft")
        maximum.press("Tab")
        expect(timeline.locator(".et-title")).to_have_text("Technical recessions, 1960–1961", timeout=30_000)
        expect(nzl).to_contain_text("15M")
        expect(nzl).to_contain_text("35.0%")
        expect(nzl).to_contain_text("-4.0%")
        expect(quarterly.locator("tbody tr").first).to_contain_text("1961-Q4")
        expect(quarterly.locator("tbody tr").first).to_contain_text("Provisional value")
        gdp = nzl.locator("td").nth(3)
        gdp.hover()
        expect(timeline.locator(".et-tooltip")).to_contain_text("15,000,000.00")
        page.mouse.move(0, 0)
        expect(timeline.locator(".et-tooltip")).to_be_hidden()
        colors = painted_colors(page, timeline.locator("tbody tr td:last-child").all())
        assert colors[0] != colors[1]
        assert all(color != [255, 255, 255] for color in colors)

        timeline.get_by_role("searchbox").fill("United States")
        timeline.locator("tbody tr").first.click()
        expect(quarterly.locator(".et-title")).to_contain_text("United States", timeout=30_000)
        expect(observations.locator(".et-empty-body")).to_be_visible()
        page.get_by_role("combobox").select_option(label="Real GDP and component growth")
        expect(observations.locator("tbody tr").first).to_contain_text("1961-Q4")
        page.get_by_role("checkbox", name="Include regional aggregates").check()
        expect(timeline.get_by_role("searchbox")).to_have_value("United States")
        timeline.get_by_role("searchbox").fill("")
        expect(timeline.locator("tbody tr")).to_have_count(3)
        expect(timeline.locator("tbody")).to_contain_text("Aggregates")
        for root in [timeline, quarterly, observations]:
            assert root.get_attribute("data-original-widget") == "yes"
