"""Column groups and display-only row headings stay aligned with frozen columns."""

import re
from base64 import b64encode

import pytest
from paint_helpers import assert_colors
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, rows

pytestmark = pytest.mark.browser


def mount_column_groups(
    page, live_server, leading_columns, *, frozen=1, row_numbers=False, top_axis=False, column_stats=False
):
    data = [
        {
            "query": f"Query {number:02}",
            "query_number": number,
            "owner": f"Owner {25 - number:02}",
            "user": "Latest user",
            "estimate": number * 1.5,
            "actual": number * 2,
            "budget": number * 3,
            "comment": "A wide scrolling column that extends past the edge of the compact table viewport",
        }
        for number in range(24, 0, -1)
    ]
    estimate = col.bar("estimate").group(["Spend", "Daily"])
    if top_axis:
        estimate = estimate.scale(axis=True)
    mount(
        page,
        live_server,
        [
            (
                "Frozen column groups",
                data,
                [
                    *leading_columns,
                    estimate,
                    col.number("actual").group(["Spend", "Daily"]),
                    col.number("budget").group(["Spend", "Budget"]),
                    col.text("comment"),
                ],
                {
                    "freeze_columns": frozen + int(row_numbers),
                    "row_numbers": row_numbers,
                    "column_stats": column_stats,
                    "width": 340,
                    "max_height": 280,
                },
            )
        ],
    )
    scroller = page.locator(".et-scroller")
    expect(scroller.locator(".et-header-leaves .et-frozen-last")).to_have_count(1)
    return scroller


def scroll_column_groups(scroller):
    assert scroller.evaluate("el => el.scrollWidth > el.clientWidth + 300 && el.scrollHeight > el.clientHeight + 100")
    scroller.evaluate("el => el.scrollTo(240, 100)")
    expect(scroller).to_have_js_property("scrollLeft", 240)
    expect(scroller).to_have_js_property("scrollTop", 100)


def assert_blank_header_paint(page, blank_cells, leaves):
    # Match paint near each join to the interior of the blank spanner, at
    # the center of every leaf the spanner covers.
    points = []
    for blank in blank_cells:
        bounds = blank.bounding_box()
        bottom = round(bounds["y"] + bounds["height"])
        for leaf in leaves:
            leaf_bounds = leaf.bounding_box()
            x = int(leaf_bounds["x"] + leaf_bounds["width"] / 2)
            points.extend([[x, bottom + dy] for dy in (-6, -2, -1, 0, 1)])
    samples = page.evaluate(
        """async ({png, points}) => {
            const image = new Image();
            image.src = 'data:image/png;base64,' + png;
            await image.decode();
            const canvas = document.createElement('canvas');
            canvas.width = image.width;
            canvas.height = image.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(image, 0, 0);
            return points.map(([x, y]) => [...ctx.getImageData(x, y, 1, 1).data].slice(0, 3));
        }""",
        {"png": b64encode(page.screenshot(scale="css")).decode(), "points": points},
    )
    for index in range(0, len(samples), 5):
        reference, *boundary = samples[index : index + 5]
        assert_colors(boundary, [reference] * len(boundary))


def assert_blank_spanners_cover_leaves(blank_cells, leaves, *, span):
    for blank in blank_cells:
        expect(blank).to_have_attribute("colspan", str(span))
        expect(blank).to_have_css("position", "sticky")
        expect(blank).to_have_class(re.compile(r"\bet-frozen\b"))
        for leaf in leaves:
            x = leaf.evaluate("el => el.getBoundingClientRect().left + el.getBoundingClientRect().width / 2")
            assert blank.evaluate(
                """(cell, x) => {
                    const bounds = cell.getBoundingClientRect();
                    const y = bounds.y + bounds.height / 2;
                    let hit = document.elementFromPoint(x, y);
                    while (hit?.shadowRoot) {
                        const inner = hit.shadowRoot.elementFromPoint(x, y);
                        if (!inner || inner === hit) break;
                        hit = inner;
                    }
                    return cell.contains(hit);
                }""",
                x,
            )


@pytest.mark.parametrize("row_numbers", [False, True])
def test_blank_column_group_header_covers_frozen_columns_when_scrolled(page, live_server, row_numbers):
    scroller = mount_column_groups(
        page,
        live_server,
        [col.text("query", title="Query"), col.text("user")],
        row_numbers=row_numbers,
    )
    offset = int(row_numbers)
    blank = scroller.locator(f'.et-header-groups .et-th-group-blank[data-column-start="{offset}"]')
    leaf = scroller.locator(f'.et-header-leaves .et-frozen[data-column-start="{offset}"]')
    expect(blank).to_have_count(2)
    expect(leaf).to_have_css("position", "sticky")
    assert_blank_header_paint(page, blank.all(), [leaf])
    scroll_column_groups(scroller)
    assert_blank_spanners_cover_leaves(blank.all(), [leaf], span=1)
    assert_blank_header_paint(page, blank.all(), [leaf])


def test_two_frozen_ungrouped_leaves_share_blank_spanners(page, live_server):
    scroller = mount_column_groups(
        page, live_server, [col.text("query"), col.text("owner"), col.text("user")], frozen=2
    )
    blank = scroller.locator('.et-header-groups .et-th-group-blank[data-column-start="0"]')
    query = scroller.locator('.et-header-leaves [data-column="query"]')
    owner = scroller.locator('.et-header-leaves [data-column="owner"]')
    leaves = [query, owner]
    expect(blank).to_have_count(2)
    scroll_column_groups(scroller)
    assert_blank_spanners_cover_leaves(blank.all(), leaves, span=2)
    assert_blank_header_paint(page, blank.all(), leaves)

    blank.last.click()
    for leaf in leaves:
        expect(leaf).to_have_attribute("aria-sort", "none")
    edge = owner.evaluate("""cell => {
        const strip = getComputedStyle(cell, '::before');
        return { width: strip.width, right: strip.right, events: strip.pointerEvents };
    }""")
    assert edge == {"width": "4px", "right": "-4px", "events": "none"}
    owner.hover()
    assert owner.evaluate("cell => cell.matches(':hover')")
    owner.click()
    expect(owner).to_have_attribute("aria-sort", "descending")
    owner.press("Enter")
    expect(owner).to_have_attribute("aria-sort", "ascending")
    expect(owner).to_be_focused()
    query.click()
    expect(query).to_have_attribute("aria-sort", "descending")
    expect(owner).to_have_attribute("aria-sort", "none")


def assert_named_group_rule(group):
    assert group.evaluate("""cell => {
        const rule = getComputedStyle(cell, '::after');
        return rule.display !== 'none' && rule.height === '2px';
    }""")


def test_frozen_named_group_keeps_its_heading_rules(page, live_server):
    scroller = mount_column_groups(page, live_server, [col.text("query").group(["Fixed", "Queries"])])
    groups = scroller.locator('.et-header-groups .et-frozen[data-column-start="0"]')
    expect(groups).to_have_count(2)
    scroll_column_groups(scroller)
    expect(groups).to_have_text(["Fixed", "Queries"])
    for group in groups.all():
        expect(group).to_have_attribute("colspan", "1")
        expect(group).to_have_css("position", "sticky")
        assert group.evaluate("cell => getComputedStyle(cell).boxShadow") != "none"
        assert_named_group_rule(group)


def test_only_the_trailing_blank_blends_into_a_frozen_leaf(page, live_server):
    scroller = mount_column_groups(page, live_server, [col.text("query").group("Fixed")])
    group = scroller.locator('.et-header-groups [data-group="Fixed"]')
    leaf = scroller.locator('.et-header-leaves [data-column="query"]')
    blank = scroller.locator('.et-header-groups .et-th-group-blank[data-column-start="0"]')
    expect(blank).to_have_count(1)
    scroll_column_groups(scroller)
    expect(group).to_have_class(re.compile(r"\bet-frozen-last\b"))
    assert_named_group_rule(group)
    assert_blank_spanners_cover_leaves([blank], [leaf], span=1)
    assert_blank_header_paint(page, [blank], [leaf])


def test_named_groups_keep_their_full_span_across_the_freeze_boundary(page, live_server):
    scroller = mount_column_groups(page, live_server, [col.text("query").group(["Spend", "Daily"])])
    spend = scroller.locator('.et-header-groups [data-group="Spend"]')
    daily = scroller.locator('.et-header-groups [data-group="Daily"]')
    leaf = scroller.locator('.et-header-leaves [data-column="query"]')
    groups = [spend, daily]
    initial = [cell.bounding_box()["x"] for cell in [*groups, leaf]]
    scroll_column_groups(scroller)
    for group, span, x in zip(groups, [4, 3], initial[:2], strict=True):
        expect(group).to_have_attribute("colspan", str(span))
        expect(group).not_to_have_class(re.compile(r"\bet-frozen\b"))
        assert group.bounding_box()["x"] == pytest.approx(x - 240, abs=1)
        assert_named_group_rule(group)
    assert leaf.bounding_box()["x"] == pytest.approx(initial[-1], abs=1)


@pytest.mark.parametrize("column_stats", [False, True])
@pytest.mark.parametrize("frozen_axis", [False, True])
def test_frozen_blank_groups_keep_top_axis_and_stats_slots(page, live_server, column_stats, frozen_axis):
    query = col.bar("query_number", title="Query").scale(axis=True) if frozen_axis else col.text("query")
    scroller = mount_column_groups(
        page, live_server, [query, col.text("user")], top_axis=True, column_stats=column_stats
    )
    blank = scroller.locator('.et-header-groups .et-th-group-blank[data-column-start="0"]')
    leaf = scroller.locator('.et-header-leaves [data-column-start="0"]')
    axis = scroller.locator(".et-axis-row-top")
    axis_slot = axis.locator('[data-column-index="0"]')
    estimate_axis = axis.locator('[data-column-index="2"]')
    stats = scroller.locator('.et-stats-row [data-column-start="0"]')
    scroll_column_groups(scroller)
    assert_blank_header_paint(page, blank.all(), [leaf])
    axis_covered = not column_stats and not frozen_axis
    expect(leaf).to_have_js_property("rowSpan", 2 if axis_covered else 1)
    expect(axis_slot).to_have_count(0 if axis_covered else 1)
    expect(stats).to_have_count(int(column_stats))
    expect(estimate_axis.locator(".et-axis-label").first).to_be_visible()

    bounds = leaf.bounding_box()
    for slot in [*stats.all(), *axis_slot.all()]:
        assert slot.bounding_box()["x"] == pytest.approx(bounds["x"], abs=1)
        assert slot.evaluate("cell => getComputedStyle(cell).boxShadow") != "none"
    if column_stats:
        stats_bounds = stats.bounding_box()
        assert stats_bounds["y"] == pytest.approx(bounds["y"] + bounds["height"], abs=1)
        bounds = stats_bounds
    if frozen_axis:
        expect(axis_slot.locator(".et-axis-label").first).to_be_visible()
    axis_bounds = estimate_axis.bounding_box()
    assert axis_bounds["y"] + (axis_bounds["height"] if axis_covered else 0) == pytest.approx(
        bounds["y"] + bounds["height"], abs=1
    )


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
