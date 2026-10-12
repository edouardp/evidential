"""Functional tests for the renderer, driven through a real browser.

Run with ``make test-browser`` (or ``uv run pytest -m browser tests/browser``).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser


def open_preview(page, live_server, fragment=""):
    page.goto(f"{live_server}/frontend/preview.html{fragment}", wait_until="networkidle")
    page.wait_for_selector(".evidence-tables-widget .et-table")


def cell_text(page, scope, row, column):
    return page.locator(f"{scope} tbody tr").nth(row).locator("td").nth(column).inner_text()


def test_renders_and_sorts(page, live_server):
    open_preview(page, live_server)
    assert page.locator("#raw tbody tr").count() == 6

    trips_header = page.locator("#raw .et-th", has_text="Trips")
    trips_header.click()  # desc
    assert "London" in cell_text(page, "#raw", 0, 1)
    trips_header.click()  # asc
    assert "Chicago" in cell_text(page, "#raw", 0, 1)
    trips_header.click()  # cleared, original order
    assert "New York" in cell_text(page, "#raw", 0, 1)


def test_search_filters_rows(page, live_server):
    open_preview(page, live_server)
    search = page.locator("#raw .et-search")
    search.fill("London")
    page.wait_for_timeout(150)
    assert page.locator("#raw tbody tr").count() == 1
    assert "London" in page.locator("#raw tbody tr").first.inner_text()


def test_pagination(page, live_server):
    open_preview(page, live_server, "#pages")
    page.wait_for_selector("#paged tbody tr")
    assert page.locator("#paged tbody tr").count() == 8
    page.locator("#paged .et-page-controls button").nth(1).click()
    page.wait_for_timeout(150)
    assert page.locator("#paged tbody tr").count() == 8
    assert "2 /" in page.locator("#paged .et-page-current").inner_text()


def test_fullscreen_round_trip(page, live_server):
    open_preview(page, live_server, "#pages")
    dialog = page.locator("#paged dialog.et-dialog")
    page.locator("#paged .et-icon-btn").click()
    page.wait_for_timeout(300)
    assert dialog.evaluate("d => d.open") is True
    assert dialog.locator(".et-root.et-expanded").count() == 1

    dialog.locator(".et-icon-btn").click()
    page.wait_for_timeout(300)
    assert dialog.evaluate("d => d.open") is False
    assert page.locator("#paged .et-root .et-table").count() == 1


def test_sparklines_render(page, live_server):
    open_preview(page, live_server)
    assert page.locator("#raw svg.et-sparkline").count() >= 6


def test_bar_fills_row_without_growing_it(page, live_server):
    open_preview(page, live_server)
    bar_cell = page.locator("#raw .et-bar-cell").first
    # the bar cell must not grow the row: it matches the padded content height
    # of a normal cell in the same row (the td's own bounding box adds borders)
    data_client = page.locator("#raw tbody tr").first.locator("td").first.evaluate("el => el.clientHeight")
    assert bar_cell.bounding_box()["height"] == pytest.approx(data_client, abs=1)
    # the bar fills the row, leaving ~2px to the separators
    bar_box = bar_cell.locator(".et-bar").first.bounding_box()
    assert bar_box["height"] == pytest.approx(bar_cell.bounding_box()["height"] - 4, abs=1.5)


def test_accordion_indents_child_rows(page, live_server):
    open_preview(page, live_server)
    subtotal = page.locator("#grouped tbody tr.et-row-subtotal").first
    detail = page.locator("#grouped tbody tr.et-row:not(.et-row-subtotal):not(.et-row-total)").first

    def pad(cell):
        return cell.evaluate("el => parseFloat(getComputedStyle(el).paddingLeft)")

    # the parent (region) dimension is indented on detail rows...
    parent_pad = pad(detail.locator("td").first)
    # ...but the leaf dimension (city) and the subtotal label are not
    leaf_pad = pad(detail.locator("td").nth(1))
    subtotal_pad = pad(subtotal.locator("td").first)
    assert parent_pad >= leaf_pad + 24  # ~2rem indent
    assert leaf_pad <= 8  # base cell padding only
    assert subtotal_pad <= 8


def test_frozen_columns_have_an_opaque_backdrop(page, live_server):
    """Scrolled content must not show through frozen cells (shaded or not)."""
    open_preview(page, live_server)
    # Scroll horizontally so non-frozen cells slide underneath the frozen ones.
    page.eval_on_selector("#raw .et-scroller", "el => { el.scrollLeft = 300; }")
    page.wait_for_timeout(200)

    alphas = page.eval_on_selector_all(
        "#raw tbody .et-frozen",
        """cells => cells.map((cell) => {
            const value = getComputedStyle(cell).backgroundColor;
            const match = value.match(/rgba?\\(([^)]+)\\)/);
            if (!match) return 1;
            const parts = match[1].split(',').map((part) => parseFloat(part));
            return parts.length === 4 ? parts[3] : 1;
        })""",
    )
    assert alphas, "expected frozen cells in the preview table"
    assert min(alphas) == 1, f"a frozen cell is translucent: {alphas}"


def test_column_info_tooltip_is_immediate(page, live_server):
    open_preview(page, live_server, "#features")
    icon = page.locator("#features .et-th-info").first
    assert icon.count() == 1
    # no delayed native tooltip, and the cursor is left alone
    assert icon.get_attribute("title") is None
    assert icon.evaluate("el => getComputedStyle(el).cursor") != "help"

    icon.hover()
    tooltip = page.locator(".et-tooltip")
    tooltip.wait_for(state="visible", timeout=2000)
    assert tooltip.inner_text() == "The city name"

    page.mouse.move(0, 0)
    tooltip.wait_for(state="detached", timeout=2000)


def test_delta_indicator_follows_the_value(page, live_server):
    open_preview(page, live_server, "#features")
    text = page.locator("#features .et-delta").first.inner_text().strip()
    assert text[0].isdigit()  # value first...
    assert text.endswith("▲") or text.endswith("▼")  # ...indicator last


def test_display_features(page, live_server):
    open_preview(page, live_server, "#features")
    page.wait_for_selector("#features tbody tr")

    # default_sort asc by trips -> Chicago first
    assert "Chicago" in cell_text(page, "#features", 0, 1)
    # row numbers (header + 3 rows)
    assert page.locator("#features .et-row-num").count() == 4
    # compact density + column info icon
    assert page.locator("#features .et-root.et-compact").count() == 1
    assert page.locator("#features .et-th-info").count() == 1
    # delta chip
    assert page.locator("#features .et-delta-chip").count() >= 1
    # row conditional colour on the New York row (last after asc sort)
    background = (
        page.locator("#features tbody tr")
        .nth(2)
        .locator("td")
        .first.evaluate("el => getComputedStyle(el).backgroundColor")
    )
    assert background == "rgb(254, 249, 195)"
