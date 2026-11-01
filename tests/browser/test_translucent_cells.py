"""Verify painted pixels, not just RGBA strings, over striped row backgrounds."""

import pytest
from paint_helpers import assert_colors, painted_colors
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col

pytestmark = pytest.mark.browser


def test_translucent_fills_reveal_stripes_and_keep_selection_and_frozen_backdrops(page, live_server):
    data = [
        {"id": name, "soft": 0, "direct": 0, "solid": 0, "clear": 0, "wide": "Scrolled content"}
        for name in ["Unshaded", "Shaded"]
    ]
    columns = [
        col.text("id"),
        col.number("soft").color(scale=["red", "#ffffffcc", "blue"], min=-1, max=1, midpoint=0),
        col.number("direct").cell_style(background="rgba(255,255,255,0.8)"),
        col.number("solid").color(scale=["red", "white", "blue"], min=-1, max=1, midpoint=0),
        col.number("clear").color(scale=["red", "#ffffff00", "blue"], min=-1, max=1, midpoint=0),
        col.text("wide").cell_style(background="red"),
    ]
    mount(
        page,
        live_server,
        [
            (
                "Layered backgrounds",
                data,
                columns,
                {
                    "freeze_columns": 2,
                    "theme": {"background": "white", "shading": "#808080", "hover": "black", "accent": "blue"},
                },
            )
        ],
    )
    root = page.locator("#case-0")
    rows = root.locator("tbody tr")
    rows.evaluate_all("""rows => rows.forEach(row => [...row.cells].forEach((cell, index) => {
        cell.style.minWidth = [120, 70, 70, 70, 70, 600][index] + 'px';
    }))""")
    plain, striped = rows.nth(0).locator("td"), rows.nth(1).locator("td")
    expect(striped.nth(1)).to_have_css("position", "sticky")
    page.mouse.move(0, 0)
    assert_colors(
        painted_colors(page, [plain.nth(1), striped.nth(1), striped.nth(2), striped.nth(3), striped.nth(4)]),
        [
            [255, 255, 255],
            [230, 230, 230],
            [230, 230, 230],
            [255, 255, 255],
            [128, 128, 128],
        ],
    )
    assert striped.nth(1).evaluate("cell => getComputedStyle(cell).opacity") == "1"
    striped.nth(0).hover()
    assert_colors(painted_colors(page, [striped.nth(1), striped.nth(2)]), [[204, 204, 204], [204, 204, 204]])
    page.mouse.move(0, 0)
    rows.nth(1).evaluate("row => row.classList.add('et-row-selected')")
    assert_colors(painted_colors(page, [striped.nth(1), striped.nth(2)]), [[214, 214, 255], [214, 214, 255]])
    rows.nth(1).evaluate("row => row.classList.remove('et-row-selected')")
    root.locator(".et-scroller").evaluate("el => el.scrollLeft = 400")
    assert_colors(painted_colors(page, [striped.nth(1)]), [[230, 230, 230]])
    capture(page, "translucent-frozen-backgrounds.png")


def test_row_colors_highlights_and_style_rules_share_the_translucent_layer(page, live_server):
    data = [{"label": label, "a": 0, "b": 0, "c": 0, "tint": "#ffffffcc"} for label in ["Plain", "Stripe"]]
    mount(
        page,
        live_server,
        [
            (
                "All cell color paths",
                data,
                [
                    col.text("label"),
                    col.number("a").color(scale="@tint"),
                    col.number("b").highlight("#ffffffcc"),
                    col.number("c"),
                ],
                {
                    "row_numbers": True,
                    "row_conditional_colors": "tint",
                    "theme": {"background": "white", "shading": "#808080"},
                    "rules": [{"columns": ["c"], "style": {"background-color": "#ffffffcc"}}],
                },
            )
        ],
    )
    page.mouse.move(0, 0)
    cells = page.locator("#case-0 tbody tr").nth(1).locator("td")
    assert_colors(painted_colors(page, cells.all()), [[230, 230, 230]] * 5)
