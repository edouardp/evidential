"""Display-only group headings follow frozen columns during horizontal scrolling."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, rows

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("frozen", [0, 1, 2])
def test_plain_group_heading_stays_with_frozen_details(page, live_server, frozen):
    data = [
        {
            "region": "Northern region",
            "product": "Item A",
            "sales": 12,
            "units": 3,
            "description": "A wide descriptive column to require horizontal scrolling in this compact viewport",
        }
    ]
    mount(
        page,
        live_server,
        [
            (
                "Frozen group headings",
                data,
                [col.text("product"), col.bar("sales"), col.bar("units"), col.text("description")],
                {
                    "row_layout": rows.group_by("region").section(rule="below", style={"color": "#666666"}),
                    "freeze_columns": frozen,
                    "width": 320,
                },
            )
        ],
    )
    heading = page.locator(".et-display-heading")
    detail = page.locator('tbody tr:not(.et-display-row) [data-column-index="0"]')

    def text_x():
        return heading.evaluate("""el => {
            const range = document.createRange(); range.selectNodeContents(el);
            return range.getBoundingClientRect().x;
        }""")

    before = text_x()
    detail_before = detail.bounding_box()["x"]
    scroller = page.locator(".et-scroller")
    assert scroller.evaluate("el => el.scrollWidth > el.clientWidth + 200")
    scroller.evaluate("el => el.scrollLeft = 250")
    page.wait_for_timeout(100)
    movement = 0 if frozen else -250
    assert detail.bounding_box()["x"] == pytest.approx(detail_before + movement, abs=1)
    after = text_x()
    assert after == pytest.approx(before + movement, abs=1), {"heading_before": before, "heading_after": after}
    assert heading.evaluate("el => getComputedStyle(el).color") == "rgb(102, 102, 102)"
    assert heading.evaluate("el => getComputedStyle(el).borderBottomWidth") == "1px"
    if frozen:
        # Recalculation on resize must not measure already-sticky positions.
        page.locator(".et-root").evaluate("el => el.style.maxWidth = '400px'")
        page.wait_for_timeout(100)
        assert scroller.evaluate("el => el.clientWidth") == 400
        scroller.evaluate("el => el.scrollLeft = el.scrollWidth")
        assert text_x() == pytest.approx(before, abs=1)
        assert detail.bounding_box()["x"] == pytest.approx(detail_before, abs=1)
    capture(page, f"frozen-group-headings-{frozen}.png")


@pytest.mark.parametrize("values", [False, True])
def test_nested_and_continued_headings_and_summaries_freeze_with_row_numbers(page, live_server, values):
    data = [
        {
            "region": "North",
            "category": "Hardware",
            "product": f"Item {i}",
            "sales": i,
            "description": "A wide descriptive column to require horizontal scrolling in this compact viewport",
        }
        for i in range(3)
    ]
    layout = (
        rows.group_by("region", "category")
        .section(values={"sales": "sum"} if values else None)
        .summary("Subtotal", values={"sales": "sum"})
        .grand_summary(values={"sales": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Nested headings",
                data,
                [col.text("product"), col.number("sales"), col.text("description")],
                {
                    "row_layout": layout,
                    "freeze_columns": 2,
                    "row_numbers": True,
                    "section_indent": 1,
                    "page_size": 2,
                    "width": 320,
                },
            )
        ],
    )
    scroller = page.locator(".et-scroller")

    def label_positions():
        return page.locator(".et-display-label").evaluate_all("els => els.map(el => el.getBoundingClientRect().x)")

    before = label_positions()
    detail_x = page.locator('tbody tr:not(.et-display-row) [data-column-index="1"]').first.bounding_box()["x"]
    scroller.evaluate("el => el.scrollLeft = 200")
    page.wait_for_timeout(100)
    assert label_positions() == pytest.approx(before, abs=1)
    assert page.locator('tbody tr:not(.et-display-row) [data-column-index="1"]').first.bounding_box()[
        "x"
    ] == pytest.approx(detail_x, abs=1)
    if values:
        expect(page.locator(".et-display-section .et-row-num.et-frozen")).to_have_count(2)
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(page.locator(".et-row-continuation")).to_have_count(2)
    scroller.evaluate("el => el.scrollLeft = 0")
    page.wait_for_timeout(100)
    continued = label_positions()
    # The nested heading keeps its depth indentation on both pages.
    assert continued[1] - continued[0] == pytest.approx(16, abs=1)
    scroller.evaluate("el => el.scrollLeft = 250")
    page.wait_for_timeout(100)
    assert label_positions() == pytest.approx(continued, abs=1)
    expect(page.locator(".et-display-summary .et-row-num.et-frozen")).to_have_count(2)
    expect(page.locator(".et-display-grand_summary .et-row-num.et-frozen")).to_have_count(1)
    expect(page.locator(".et-display-row .et-marks")).to_have_count(0)


def test_centered_heading_keeps_its_full_table_alignment(page, live_server):
    data = [{"region": "North", "product": "Item A", "description": "Wide description " * 10}]
    mount(
        page,
        live_server,
        [
            (
                "Centered heading",
                data,
                [col.text("product"), col.text("description")],
                {"row_layout": rows.group_by("region").section(align="center"), "freeze_columns": 1, "width": 320},
            )
        ],
    )
    heading = page.locator(".et-display-heading")
    assert heading.evaluate("el => getComputedStyle(el).textAlign") == "center"
    expect(heading.locator(".et-frozen-heading-label")).to_have_count(0)
    assert heading.get_attribute("colspan") == "2"
