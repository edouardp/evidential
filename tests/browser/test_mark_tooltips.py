"""Inspect real browser geometry, overlap, full precision and keyboard/touch use."""

import runpy
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import EvidentialTable, col, label
from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/55_tooltips.py"


@pytest.fixture(autouse=True)
def tooltip_timeouts(page):
    page.set_default_timeout(10_000)


@pytest.fixture(scope="module")
def demos():
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return {name: value.widget for name, value in definitions.items() if hasattr(value, "widget")}


def test_full_values_overlap_enlarged_hit_area_and_keyboard(page, live_server, demos):
    mount(page, live_server, [("Precision", demos["precision_table"], []), ("Overlap", demos["overlap_table"], [])])
    cells = page.locator("#case-0 tbody td")
    for index, expected in [
        (1, "1,253,224,564,123.12"),
        (2, "12.3456%"),
        (3, "$1,253,224,564.12"),
        (4, "0.000000123456"),
    ]:
        cells.nth(index).hover()
        expect(page.locator("#case-0 .et-tooltip-value")).to_have_text(expected)
    dot = page.locator("#case-1 .et-mark-point").first
    dot.hover(force=True)
    tip = page.locator("#case-1 .et-tooltip")
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-name")).to_have_text(["Younger:", "Middle:"])
    expect(tip.locator(".et-tooltip-value")).to_have_text(["20%", "20%"])
    box = dot.bounding_box()
    page.mouse.move(box["x"] - 3, box["y"] + box["height"] / 2)
    expect(tip.locator(".et-tooltip-entry")).to_have_count(2)
    capture(page, "tooltips-overlap.png")
    cell = dot.locator("xpath=ancestor::td")
    assert cell.get_attribute("tabindex") == "0"
    assert cell.locator("[tabindex]").count() == 0
    cell.focus()
    cell.press("End")
    expect(tip.locator(".et-tooltip-name")).to_have_text("Older:")
    cell.press("ArrowRight")
    expect(tip.locator(".et-tooltip-entry")).to_have_count(2)
    cell.press("Escape")
    expect(tip).to_be_hidden()
    assert cell.get_attribute("aria-describedby") is None
    assert dot.get_attribute("title") is None


def test_stacks_hidden_labels_and_both_neutral_halves(page, live_server, demos):
    mount(page, live_server, [("Stack", demos["stack_table"], []), ("Neutral", demos["neutral_table"], [])])
    root = page.locator("#case-0")
    root.locator(".et-mark-stack-seg").first.hover()
    expect(root.locator(".et-tooltip-name")).to_have_text("Storage:")
    expect(root.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("61%")
    expect(root.locator(".et-tooltip-detail")).to_have_text(["Value: $1,235", "Total: $2,018"])
    root.locator(".et-mark-stack-label").first.hover()
    expect(root.locator(".et-tooltip-name")).to_have_text("Storage:")
    last = root.locator(".et-mark-stack-seg").last
    assert last.locator(".et-mark-stack-label").evaluate("el => getComputedStyle(el).visibility") == "hidden"
    last.hover(force=True)
    expect(root.locator(".et-tooltip-name")).to_have_text("Other:")
    expect(root.locator(".et-tooltip-detail")).to_have_text(["Value: $1", "Total: $2,018"])
    neutral = page.locator("#case-1")
    for index in (0, 2):
        neutral.locator(".et-mark-stack-seg").nth(index).hover()
        expect(neutral.locator(".et-tooltip-name")).to_have_text("Neutral:")
        expect(neutral.locator(".et-tooltip-detail")).to_have_text(["Value: 30", "Total: 100"])
    capture(page, "tooltips-neutral.png")


def test_metadata_ranges_boxes_and_multiline_overrides(page, live_server, demos):
    mount(
        page,
        live_server,
        [
            ("Matches", demos["match_table"], []),
            ("Ranges", demos["range_table"], []),
            ("Overrides", demos["custom_table"], []),
        ],
    )
    page.locator("#case-0 .et-strip-seg").first.hover()
    tip = page.locator("#case-0 .et-tooltip")
    expected = demos["match_table"].raw[0]["form"][0]
    assert expected["category"] in tip.inner_text()
    for key in ("date", "opponent", "score", "venue", "competition"):
        assert expected[key] in tip.inner_text()
    capture(page, "tooltips-football.png")
    page.locator("#case-1 .et-mark-range").first.hover()
    expect(page.locator("#case-1 .et-tooltip-detail")).to_have_text(["Before: 30", "After: 80", "Change: 50"])
    page.locator("#case-1 .et-box-iqr").first.hover(force=True)
    expect(page.locator("#case-1 .et-tooltip-detail")).to_have_text(
        ["Minimum: 10", "Lower quartile: 25", "Median: 45", "Upper quartile: 65", "Maximum: 90"]
    )
    page.locator("#case-1 .et-box-outlier").first.hover()
    expect(page.locator("#case-1 .et-tooltip-value")).to_have_text("97")
    custom = page.locator("#case-2")
    custom.locator("tbody td").first.hover()
    expect(custom.locator(".et-tooltip-value")).to_have_text("Regional total\nIncludes online orders\nExcludes refunds")
    assert custom.locator(".et-tooltip-content").evaluate("el => getComputedStyle(el).whiteSpace") == "pre-wrap"
    custom.locator("tbody td").nth(1).hover()
    expect(custom.locator(".et-tooltip-value")).to_have_text("Reported amount\nProvisional estimate")
    custom.locator(".et-mark-bar").hover()
    expect(custom.locator(".et-tooltip")).to_be_hidden()


def test_label_inherits_data_tooltip_and_popup_stays_in_viewport_dark_fullscreen(page, live_server):
    table = EvidentialTable(
        [{"actual": 50, "forecast": 75}],
        columns=[
            col.bar("actual", format="usd0", label=label.text("Actual estimate").position("outside end")).scale(
                domain=(0, 100)
            ),
            col.point("forecast", format="pct0"),
        ],
        theme={"surface": "#111827", "text": "#f9fafb"},
        search=False,
        page_size=0,
    )
    mount(page, live_server, [("Labels", table, [])])
    page.locator(".et-mark-label").hover()
    tip = page.locator(".et-tooltip")
    expect(tip.locator(".et-tooltip-name")).to_have_text("Actual:")
    expect(tip.locator(".et-tooltip-value")).to_have_text("$50")
    assert tip.evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(17, 24, 39)"
    assert tip.evaluate("el => getComputedStyle(el).color") == "rgb(249, 250, 251)"
    page.set_viewport_size({"width": 360, "height": 420})
    page.get_by_role("button", name="Expand table").click()
    page.locator("dialog .et-mark-point").hover()
    expect(tip).to_be_visible()
    assert tip.evaluate("el => el.matches(':popover-open')")
    box = tip.bounding_box()
    assert 0 <= box["x"] <= 360 - box["width"]
    assert 0 <= box["y"] <= 420 - box["height"]
    capture(page, "tooltips-dark-fullscreen.png")


def test_real_marimo_tooltip_notebook_renders_and_inspects(page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        overlap = page.locator('[data-cell-name="overlapping_points"] .et-root')
        overlap.locator(".et-mark-point").first.hover(force=True)
        expect(overlap.locator(".et-tooltip-name")).to_have_text(["Younger:", "Middle:"])
        stack = page.locator('[data-cell-name="stacked_values"] .et-root').first
        stack.locator(".et-mark-stack-seg").first.hover()
        expect(stack.locator(".et-tooltip-name")).to_have_text("Storage:")
        expect(stack.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("61%")
        page.locator('[data-cell-name="custom_tooltips"] .et-mark-bar').wait_for()
        page.locator('[data-cell-name="sparkline_inspection"] .et-sparkline').wait_for()
        assert page.locator(".et-root").count() == 8
        capture(page, "tooltips-marimo.png")
    assert errors == []


def test_sparkline_chooses_one_x_value_with_signed_color_and_separate_delays(page, live_server, demos):
    mount(page, live_server, [("Sparklines and delay", demos["spark_table"], [])])
    spark = page.locator(".et-sparkline")
    circles = spark.locator("circle")
    bounds = spark.bounding_box()
    dot = circles.first.bounding_box()
    page.mouse.move(dot["x"] + dot["width"] / 2, bounds["y"] + bounds["height"] - 1)
    tip = page.locator(".et-tooltip")
    page.wait_for_timeout(400)
    expect(tip).to_be_hidden()
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-entry")).to_have_count(1)
    expect(tip.locator(".et-tooltip-value")).to_have_text("80%")
    assert (
        tip.locator(".et-tooltip-swatch").evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(220, 38, 38)"
    )
    point = circles.nth(3).bounding_box()
    page.mouse.move(point["x"] + point["width"] / 2, bounds["y"] + 1)
    expect(tip.locator(".et-tooltip-entry")).to_have_count(1)
    expect(tip.locator(".et-tooltip-value")).to_have_text("112%")
    assert (
        tip.locator(".et-tooltip-swatch").evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(15, 118, 110)"
    )
    page.locator("tbody td").first.hover()
    page.wait_for_timeout(1000)
    expect(tip).to_be_hidden()
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-value")).to_have_text("Illustrative exports / imports\n100% means balanced trade")
    page.locator(".et-mark-bar").hover(force=True)
    # The explicit per-column override bypasses the table's 0.8s graphics delay.
    expect(tip).to_be_visible(timeout=300)
    expect(tip.locator(".et-tooltip-value")).to_have_text("1,253,224,564.12")
    capture(page, "tooltips-delays-and-signed-area.png")
