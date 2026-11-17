"""Display-only group headings follow frozen columns during horizontal scrolling."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, rows

pytestmark = pytest.mark.browser


@pytest.mark.parametrize("row_numbers", [False, True])
def test_blank_column_group_header_covers_frozen_columns_when_scrolled(page, live_server, row_numbers):
    data = [
        {
            "query_start": "Latest query",
            "latest_user_name": "alice",
            "user_count": 2,
            "statement_subtype": "SELECT",
            "dollars": 12,
            "dollars_per_query": 3,
            "scanned_bytes": 1024,
            "queries": 4,
            "cached": 1,
            "failed_share": 0,
            "mean_s": 2,
            "workgroups": "analytics",
            "first_submitted_at": "2026-11-01",
            "last_submitted_at": "2026-11-18",
            "latest_query_execution_id": "query-123",
        }
    ]
    mount(
        page,
        live_server,
        [
            (
                "Frozen blank column group",
                data,
                [
                    col.text("query_start", title="Query (latest run)"),
                    col.text("latest_user_name", title="Latest user"),
                    col.integer("user_count", title="Users"),
                    col.text("statement_subtype", title="Statement"),
                    col.group(
                        "Spend", [col.bar("dollars"), col.number("dollars_per_query"), col.number("scanned_bytes")]
                    ),
                    col.group(
                        "Runs",
                        [
                            col.number("queries"),
                            col.number("cached"),
                            col.percent("failed_share"),
                            col.number("mean_s"),
                        ],
                    ),
                    col.text("workgroups"),
                    col.datetime("first_submitted_at"),
                    col.datetime("last_submitted_at"),
                    col.text("latest_query_execution_id"),
                ],
                {"freeze_columns": 2 if row_numbers else 1, "row_numbers": row_numbers, "width": 320},
            )
        ],
    )
    offset = 1 if row_numbers else 0
    cell = page.locator(f'.et-header-groups .et-th-group-blank[data-column-start="{offset}"]')
    leaf = page.locator(f'.et-header-leaves .et-frozen[data-column-start="{offset}"]')
    expect(leaf).to_have_css("position", "sticky")
    scroller = page.locator(".et-scroller")
    assert scroller.evaluate("el => el.scrollWidth > el.clientWidth + 300")
    scroller.evaluate("el => el.scrollLeft = 300")
    expect(scroller).to_have_js_property("scrollLeft", 300)
    hit = cell.evaluate(
        """(cell, column) => {
            const leaf = cell.closest('thead').querySelector(
                `.et-header-leaves [data-column-start="${column}"]`).getBoundingClientRect();
            const bounds = cell.getBoundingClientRect();
            const x = leaf.x + leaf.width / 2, y = bounds.y + bounds.height / 2;
            let hit = document.elementFromPoint(x, y);
            // Follow the browser's hit through the widget's open shadow boundary.
            while (hit?.shadowRoot) {
                const inner = hit.shadowRoot.elementFromPoint(x, y);
                if (!inner || inner === hit) break;
                hit = inner;
            }
            return {covered: hit === cell || cell.contains(hit), group: hit?.closest('th')?.dataset.group};
        }""",
        offset,
    )
    assert hit["covered"], hit
    assert hit["group"] != "Spend"
    assert "et-frozen" in cell.get_attribute("class").split()
    expect(cell).to_have_css("position", "sticky")
    assert cell.get_attribute("colspan") == "1"


def assert_heading_boundary(heading, frozen_cell):
    label = heading.locator(".et-frozen-heading-label")
    expect(label).to_have_count(1)
    geometry = label.evaluate("""el => {
        const marker = getComputedStyle(el, '::before');
        const rect = el.getBoundingClientRect();
        return {right: rect.x + parseFloat(marker.left) + parseFloat(marker.width),
            height: parseFloat(marker.height), shadow: marker.boxShadow, events: marker.pointerEvents};
    }""")
    assert geometry["right"] == pytest.approx(
        frozen_cell.bounding_box()["x"] + frozen_cell.bounding_box()["width"], abs=1
    )
    assert geometry["height"] == pytest.approx(heading.bounding_box()["height"], abs=2)
    assert geometry["shadow"] == frozen_cell.evaluate("el => getComputedStyle(el).boxShadow")
    assert geometry["shadow"] != "none"
    assert geometry["events"] == "none"


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
    edge = page.locator("tbody tr:not(.et-display-row) .et-frozen-last").first
    if frozen:
        assert_heading_boundary(heading, edge)
    else:
        expect(heading.locator(".et-frozen-heading-label")).to_have_count(0)
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
        assert_heading_boundary(heading, edge)
        # Recalculation on resize must not measure already-sticky positions.
        page.locator(".et-root").evaluate("el => el.style.maxWidth = '400px'")
        page.wait_for_timeout(100)
        assert scroller.evaluate("el => el.clientWidth") == 400
        scroller.evaluate("el => el.scrollLeft = el.scrollWidth")
        assert text_x() == pytest.approx(before, abs=1)
        assert detail.bounding_box()["x"] == pytest.approx(detail_before, abs=1)
        assert_heading_boundary(heading, edge)
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
    # Continuation headings retain the original cells and nested indentation.
    assert continued[:2] == pytest.approx(before[:2], abs=1)
    scroller.evaluate("el => el.scrollLeft = 250")
    page.wait_for_timeout(100)
    assert label_positions() == pytest.approx(continued, abs=1)
    expect(page.locator(".et-display-summary .et-row-num.et-frozen")).to_have_count(2)
    expect(page.locator(".et-display-grand_summary .et-row-num.et-frozen")).to_have_count(1)
    expect(page.locator(".et-display-row .et-marks")).to_have_count(0)
    if not values:
        edge = page.locator(".et-display-summary .et-frozen-last").first
        for heading in page.locator(".et-display-heading").all():
            assert_heading_boundary(heading, edge)


def test_closed_group_heading_retains_the_frozen_boundary_without_detail_cells(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Closed heading",
                [{"region": "North", "name": "Item", "value": 1}],
                [col.text("name"), col.integer("value")],
                {"row_layout": rows.group_by("region").section(collapsible=True), "freeze_columns": 1},
            )
        ],
    )
    page.get_by_role("button", name="Toggle section North").click()
    expect(page.locator("tbody tr:not(.et-display-row)")).to_have_count(0)
    edge = page.locator("thead .et-frozen-last").last
    assert_heading_boundary(page.locator(".et-display-heading"), edge)


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
