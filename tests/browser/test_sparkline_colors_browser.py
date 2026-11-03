"""Y-value gradients render through the public fluent API and actual notebook demo."""

import runpy
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col

pytestmark = pytest.mark.browser


def test_notebook_gradient_demo_renders_all_styles_and_matching_tooltip_colors(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks/40_sparklines_and_booleans.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["gradient_table"].widget
    mount(page, live_server, [("Gradient styles", table, [])])
    expect(page.locator("tbody .et-sparkline")).to_have_count(15)
    cells = page.locator("tbody tr").first.locator("td")
    bars = cells.nth(1).locator("rect")
    points = cells.nth(2).locator("circle")
    expect(bars).to_have_count(7)
    expect(points).to_have_count(7)
    for marks in (bars, points):
        expect(marks.first).to_have_attribute("fill", "#b2182b")
        expect(marks.nth(3)).to_have_attribute("fill", "#b8bcc2")
        expect(marks.last).to_have_attribute("fill", "#2166ac")
    expect(cells.nth(3).locator("polyline")).to_have_count(6)
    expect(cells.nth(4).locator("polygon")).to_have_count(6)
    expect(cells.nth(3).locator("polyline").first).to_have_attribute("stroke", "#b2182b")
    expect(cells.nth(4).locator("polygon").nth(3)).to_have_attribute("fill", "#b8bcc2")
    # Explicit colors survive the gradient for every style, including change.
    override = page.locator("tbody tr").last.locator("td")
    for index in (1, 2, 5):
        selector = "circle" if index == 2 else "rect"
        expect(override.nth(index).locator(selector).nth(2)).to_have_attribute("fill", "#7c3aed")
    expect(override.nth(3).locator("polyline").nth(1)).to_have_attribute("stroke", "#7c3aed")
    expect(override.nth(4).locator("polygon").nth(1)).to_have_attribute("fill", "#7c3aed")
    points.last.hover(force=True)
    tip = page.locator(".et-tooltip")
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("10")
    expect(tip.locator(".et-tooltip-swatch")).to_have_css("background-color", "rgb(33, 102, 172)")
    capture(page, "sparkline-y-gradients.png")


def test_auto_gradient_ranges_cover_all_pages_and_recompute_on_search(page, live_server):
    data = [{"name": "Keep", "history": [0, 5]}, {"name": "Other", "history": [10, 20]}]
    mount(
        page,
        live_server,
        [
            (
                "Automatic gradient",
                data,
                [
                    col.text("name"),
                    col.sparkline("history", type="bar").color(scale=["red", "blue"]),
                ],
                {"page_size": 1, "search": True},
            )
        ],
    )
    marks = page.locator("tbody rect")
    expect(marks.first).to_have_attribute("fill", "#ff0000")
    initial = marks.last.get_attribute("fill")
    assert initial not in ("#ff0000", "#0000ff")
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(marks.last).to_have_attribute("fill", "#0000ff")
    page.get_by_role("button", name="Previous page", exact=True).click()
    expect(marks.last).to_have_attribute("fill", initial)
    page.get_by_role("searchbox").fill("Keep")
    expect(marks.last).to_have_attribute("fill", "#0000ff")
