"""Expanded pages reserve all header tiers and keep their rows inside the dialog."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import mount

from evidential import col, rows

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("wrapped", [False, True])
def test_expanded_grouped_headers_and_statistics_fit_without_vertical_scroll(page, live_server, wrapped):
    data = [
        {
            "country": f"Country {i:03d}" if not wrapped or i == 0 else "Several lines of country data.",
            "value": i,
            "other": i / 2,
        }
        for i in range(120)
    ]
    mount(
        page,
        live_server,
        [
            (
                "Grouped headings",
                data,
                [
                    col.text("country"),
                    col.group(
                        "Economic indicators",
                        [
                            col.group(
                                "Annual observations",
                                [
                                    col.bar("value", title="A multiline\ncolumn heading").scale(axis=True),
                                    col.number("other"),
                                ],
                            )
                        ],
                    ),
                ],
                {
                    "width": "100%",
                    "title": "Economic indicators",
                    "subtitle": "Grouped headings and statistics",
                    "column_stats": True,
                    "page_size": 10,
                    "search": True,
                    "wrap": wrapped,
                    "caption": "Source: illustrative observations.",
                },
            )
        ],
    )
    page.get_by_role("button", name="Expand table", exact=True).click()
    dialog = page.get_by_role("dialog", name="Expanded data table")
    expect(dialog).to_be_visible()
    page.wait_for_timeout(300)
    sizes = dialog.evaluate("""dialog => {
        const root=dialog.querySelector('.et-root'), scroller=root.querySelector('.et-scroller');
        return {dialogHeight:dialog.clientHeight, dialogScroll:dialog.scrollHeight,
          rootHeight:root.clientHeight, rootScroll:root.scrollHeight,
          rows:root.querySelectorAll('tbody tr').length,
          scrollerHeight:scroller.clientHeight, scrollerScroll:scroller.scrollHeight,
          headerHeight:root.querySelector('thead').getBoundingClientRect().height};
    }""")
    assert sizes["scrollerScroll"] <= sizes["scrollerHeight"], sizes
    assert sizes["rootScroll"] <= sizes["rootHeight"], sizes
    assert sizes["dialogScroll"] <= sizes["dialogHeight"], sizes
    page.set_viewport_size({"width": 1024, "height": 600})
    page.wait_for_timeout(300)
    resized = dialog.evaluate("""dialog => {
        const root=dialog.querySelector('.et-root'), scroller=root.querySelector('.et-scroller');
        return {rootHeight:root.clientHeight, rootScroll:root.scrollHeight,
          scrollerHeight:scroller.clientHeight, scrollerScroll:scroller.scrollHeight};
    }""")
    assert resized["rootScroll"] <= resized["rootHeight"], resized
    assert resized["scrollerScroll"] <= resized["scrollerHeight"], resized

    def indices():
        return dialog.locator("tbody tr td:last-child").evaluate_all("els => els.map(el => Number(el.textContent) * 2)")

    previous = indices()
    for _ in range(3):
        dialog.get_by_role("button", name="Next page", exact=True).click()
        page.wait_for_timeout(100)
        current = indices()
        assert current == list(range(previous[-1] + 1, previous[-1] + len(current) + 1))
        assert dialog.locator(".et-scroller").evaluate("el => el.scrollHeight <= el.clientHeight"), dialog.evaluate("""el => ({
            scroller:el.querySelector('.et-scroller').clientHeight,
            table:el.querySelector('table').getBoundingClientRect().height,
            head:el.querySelector('thead').getBoundingClientRect().height,
            rows:[...el.querySelectorAll('tbody tr')].map(row=>row.getBoundingClientRect().height)
        })""")
        previous = current
    dialog.get_by_role("button", name="Previous page", exact=True).click()
    page.wait_for_timeout(100)
    assert indices()[-1] + 1 == previous[0]
    before_growing = indices()
    page.set_viewport_size({"width": 1280, "height": 1100})
    page.wait_for_timeout(200)
    assert indices()[0] == before_growing[0]
    assert len(indices()) >= len(before_growing)
    assert dialog.locator(".et-scroller").evaluate("el => el.scrollHeight <= el.clientHeight")
    dialog.get_by_role("button", name="Close expanded table", exact=True).click()
    expect(dialog).not_to_be_visible()
    expect(page.locator("#case-0 tbody tr")).to_have_count(10)


def test_expanded_synthetic_rows_and_totals_fit_on_every_page_without_losing_details(page, live_server):
    page.set_viewport_size({"width": 1024, "height": 650})
    data = [{"region": f"Region {i // 3}", "country": f"Item {i}", "value": i, "ordinal": i} for i in range(30)]
    layout = (
        rows.group_by("region")
        .section()
        .summary("Region total", values={"value": "sum"})
        .grand_summary(values={"value": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Sections and summaries",
                data,
                [
                    col.text("country"),
                    col.group(
                        "Measures",
                        [
                            col.bar("value").scale(axis=True, axis_position="bottom"),
                            col.integer("ordinal"),
                        ],
                    ),
                ],
                {
                    "title": "Sections and summaries",
                    "row_layout": layout,
                    "page_size": 5,
                    "column_stats": True,
                    "caption": "Synthetic headings and totals use display space, not detail slots.",
                    "footnotes": ["A note below the table also needs to fit."],
                },
            )
        ],
    )
    page.get_by_role("button", name="Expand table", exact=True).click()
    dialog = page.get_by_role("dialog", name="Expanded data table")
    expect(dialog).to_be_visible()
    page.wait_for_timeout(200)
    assert dialog.locator(".et-root").bounding_box()["width"] > 900  # Ignore the inline 520px width.
    observed = []
    for _ in range(31):
        assert dialog.locator(".et-scroller").evaluate("el => el.scrollHeight <= el.clientHeight")
        assert dialog.locator(".et-root").evaluate("el => el.scrollHeight <= el.clientHeight")
        observed.extend(
            dialog.locator("tbody tr:not(.et-display-row) td:last-child").evaluate_all(
                "els => els.map(el => Number(el.textContent))"
            )
        )
        next_page = dialog.get_by_role("button", name="Next page", exact=True)
        if next_page.is_disabled():
            break
        next_page.click()
        page.wait_for_timeout(50)
    assert observed == list(range(30))
    expect(dialog.locator("tbody .et-row-total")).to_have_count(1)
    dialog.screenshot(path="/private/tmp/evidential-fullscreen-summaries.png")
