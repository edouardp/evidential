"""Expanded-table shortcuts reuse measured paging and leave child controls their keys."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import mount

from evidential import col

pytestmark = pytest.mark.browser


def test_arrows_page_expanded_records_and_escape_restores_inline_page_and_focus(page, live_server):
    page.set_viewport_size({"width": 1000, "height": 550})
    data = [{"id": i, "name": f"Record {i:02d}"} for i in range(60)]
    mount(
        page,
        live_server,
        [
            (
                "Keyboard paging",
                data,
                [col.integer("id"), col.text("name")],
                {"page_size": 4, "search": True, "select": "id"},
            )
        ],
    )
    page.get_by_role("button", name="Next page", exact=True).click()
    page.get_by_role("button", name="Expand table", exact=True).click()
    dialog = page.get_by_role("dialog", name="Expanded data table")
    expect(dialog).to_be_visible()
    expect(dialog).to_be_focused()
    page.wait_for_timeout(100)

    def indices():
        return dialog.locator("tbody tr td:first-child").evaluate_all("els => els.map(el => Number(el.textContent))")

    first = indices()
    assert first[0] == 0
    page.keyboard.press("ArrowLeft")
    assert indices() == first
    page.keyboard.press("ArrowRight")
    assert indices()[0] == first[-1] + 1
    page.keyboard.press("ArrowLeft")
    assert indices() == first
    # The row that had focus is removed on paging; following arrows still work.
    dialog.locator("tbody tr").first.focus()
    page.keyboard.press("ArrowRight")
    expect(dialog).to_be_focused()
    second = indices()
    page.keyboard.press("ArrowRight")
    assert indices()[0] == second[-1] + 1
    for _ in range(61):
        if dialog.get_by_role("button", name="Next page", exact=True).is_disabled():
            break
        page.keyboard.press("ArrowRight")
    assert indices()[-1] == 59
    last = indices()
    page.keyboard.press("ArrowRight")
    assert indices() == last
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    expand = page.get_by_role("button", name="Expand table", exact=True)
    expect(expand).to_be_focused()
    inline = page.locator("#case-0 tbody tr td:first-child")
    expect(inline.first).to_have_text("4")
    page.keyboard.press("ArrowRight")
    expect(inline.first).to_have_text("4")


def test_search_and_graphic_tooltips_keep_arrows_and_escape_before_the_dialog(page, live_server):
    data = [{"name": f"Record {i}", "history": [1, 3, 5]} for i in range(100)]
    mount(
        page,
        live_server,
        [("Child key handling", data, [col.text("name"), col.sparkline("history")], {"page_size": 5, "search": True})],
    )
    page.get_by_role("button", name="Expand table", exact=True).click()
    dialog = page.get_by_role("dialog", name="Expanded data table")
    search = dialog.get_by_role("searchbox")
    search.fill("Record")
    page.wait_for_timeout(100)
    search.evaluate("el => el.setSelectionRange(0, 0)")
    search.press("ArrowRight")
    assert search.evaluate("el => el.selectionStart") == 1
    expect(dialog.locator(".et-page-current")).to_have_text("1")
    cell = dialog.locator("tbody tr td:last-child").first
    cell.focus()
    cell.press("ArrowRight")
    expect(dialog.locator(".et-page-current")).to_have_text("1")
    tip = dialog.locator(".et-tooltip")
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("3")
    cell.press("Escape")
    expect(tip).not_to_be_visible()
    expect(dialog).to_be_visible()
    cell.press("Escape")
    expect(dialog).not_to_be_visible()
