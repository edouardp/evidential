"""Theme isolation, live switching and consistent paints through the built bundle."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import mount

from evidential import EvidentialTable, col, color, label

pytestmark = pytest.mark.browser
LIGHT, DARK = "rgb(255, 255, 255)", "rgb(23, 27, 36)"


def themed_table(scheme, **options):
    return EvidentialTable(
        [
            {
                "team": f"Team {i:02}",
                "a": i + 1,
                "b": 20 - i,
                "delta": i - 10,
                "fill": "#14385a",
                "history": [{"value": 2, "color": "#14385a"}, 8, 5],
            }
            for i in range(20)
        ],
        columns=[
            col.text("team", info="Team name"),
            col.bar("a", color="@fill", label=label.position("inside end")).scale(domain=(0, 20), axis=True),
            col.stacked_bar("a", "b", colors=["#14385a", color.fixed("#dc2626")], labels=True).legend(),
            col.point("delta", size=10, outline=False)
            .gradient(scale=["red", color.theme("neutral", alpha=0.8), "blue"], min=-10, max=10, midpoint=0)
            .scale(domain=(-10, 10), gradient=True),
            col.sparkline("history", type="bar"),
        ],
        color_scheme=scheme,
        adapt_colors=True,
        title="Shared colours",
        subtitle="One definition",
        row_shading=True,
        freeze_columns=1,
        search=True,
        page_size=5,
        width=900,
        **options,
    )


def test_explicit_modes_isolate_widgets_and_keep_marks_legends_tooltips_consistent(page, live_server):
    mount(page, live_server, [(scheme, themed_table(scheme), []) for scheme in ["light", "dark"]])
    roots = page.locator(".et-root")
    for index, background in enumerate([LIGHT, DARK]):
        root = roots.nth(index)
        expect(root).to_have_css("background-color", background)
        expect(root.locator(".et-frozen").first).to_have_css("background-color", background)
        bar = root.locator(".et-mark-bar").first
        segment = root.locator(".et-mark-stack-seg").first
        chip = root.locator(".et-legend-swatch").first
        expected = segment.evaluate("el => getComputedStyle(el).backgroundColor")
        expect(bar).to_have_css("background-color", expected)
        expect(chip).to_have_css("background-color", expected)
        expect(root.locator(".et-mark-stack-seg").nth(1)).to_have_css("background-color", "rgb(220, 38, 38)")
        segment.hover()
        tooltip = root.locator(".et-tooltip")
        expect(tooltip).to_be_visible()
        expect(tooltip).to_have_css("background-color", background)
        expect(tooltip.locator(".et-tooltip-swatch").first).to_have_css("background-color", expected)
    assert roots.nth(0).locator(".et-mark-bar").first.get_attribute("style") != roots.nth(1).locator(
        ".et-mark-bar"
    ).first.get_attribute("style")
    expect(roots.nth(1).locator(".et-axis-tick").first).to_have_css("color", "rgb(229, 231, 235)")
    page.mouse.move(0, 0)
    page.screenshot(path="/tmp/evidential-light-dark-tables.png", full_page=True)


def test_auto_respects_host_before_os_preserving_search_sort_page_and_expanded_page(page, live_server):
    page.emulate_media(color_scheme="dark")
    mount(page, live_server, [("Automatic", themed_table("auto"), [])])
    root = page.locator(".et-root")
    expect(root).to_have_attribute("data-color-scheme", "dark")
    page.locator("body").evaluate("el => el.classList.add('light')")
    expect(root).to_have_attribute("data-color-scheme", "light")
    root.locator("thead [data-column='a']").first.click()
    root.get_by_role("button", name="Next page", exact=True).click()
    values = root.locator("tbody tr td:first-child").all_text_contents()
    search = root.get_by_role("searchbox")
    search.focus()
    page.locator("body").evaluate("el => {el.classList.remove('light'); el.dataset.theme='dark';}")
    expect(root).to_have_attribute("data-color-scheme", "dark")
    assert root.locator("tbody tr td:first-child").all_text_contents() == values
    expect(search).to_be_focused()
    search.fill("Team 1")
    filtered = root.locator("tbody tr td:first-child").all_text_contents()
    page.locator("body").evaluate("el => el.dataset.theme='light'")
    expect(root).to_have_attribute("data-color-scheme", "light")
    expect(search).to_have_value("Team 1")
    assert root.locator("tbody tr td:first-child").all_text_contents() == filtered
    search.fill("")
    page.set_viewport_size({"width": 1100, "height": 360})
    root.get_by_role("button", name="Expand table", exact=True).click()
    root.get_by_role("button", name="Next page", exact=True).click()
    values = root.locator("tbody tr td:first-child").all_text_contents()
    page.locator("body").evaluate("el => el.dataset.theme='dark'")
    expect(root).to_have_attribute("data-color-scheme", "dark")
    assert root.locator("tbody tr td:first-child").all_text_contents() == values
    expect(page.locator("dialog")).to_have_css("color-scheme", "dark")
    page.keyboard.press("Escape")
    expect(page.locator("dialog")).not_to_be_visible()


def test_print_temporarily_uses_light_and_restores_explicit_dark(page, live_server):
    mount(page, live_server, [("Print", themed_table("dark"), [])])
    root = page.locator(".et-root")
    page.evaluate("dispatchEvent(new Event('beforeprint'))")
    expect(root).to_have_css("background-color", LIGHT)
    page.evaluate("dispatchEvent(new Event('afterprint'))")
    expect(root).to_have_css("background-color", DARK)


def test_builtin_scales_and_literal_opt_out(page, live_server):
    columns = [col.number("x").color(scale="blue"), col.bar("y", color="#123456")]
    mount(
        page,
        live_server,
        [
            (scheme, [{"x": 0, "y": 5}, {"x": 10, "y": 5}], columns, {"color_scheme": scheme})
            for scheme in ["light", "dark"]
        ],
    )
    fills = []
    for root in page.locator(".et-root").all():
        expect(root.locator(".et-mark-bar").first).to_have_css("background-color", "rgb(18, 52, 86)")
        fills.append(
            root.locator(".et-color-cell").first.evaluate(
                "el => getComputedStyle(el).getPropertyValue('--et-cell-fill')"
            )
        )
    assert fills[0] != fills[1]


def test_css_surface_tokens_and_highlight_contrast_follow_host_changes(page, live_server):
    columns = [
        col.text("name").highlight("white"),
        col.point("x", size=12, outline=False).gradient(
            scale=["red", color.theme("neutral"), "blue"], min=-1, max=1, midpoint=0
        ),
    ]
    mount(
        page,
        live_server,
        [
            (
                "CSS surfaces",
                [{"name": "Visible", "x": 0}],
                columns,
                {"color_scheme": "dark", "theme": {"surface": "var(--surface, #171b24)"}},
            )
        ],
    )
    expect(page.locator("tbody td").first).to_have_css("color", "rgb(0, 0, 0)")
    expect(page.locator("thead th").first).to_have_css("color", "rgb(0, 0, 0)")
    dot = page.locator(".et-mark-point")
    expect(dot).to_have_css("background-color", DARK)
    page.locator("body").evaluate("el => el.style.setProperty('--surface', '#123456')")
    expect(dot).to_have_css("background-color", "rgb(18, 52, 86)")


def test_notebook_mode_selector_updates_existing_widgets(page):
    from pathlib import Path

    from paint_helpers import painted_colors

    from scripts.api_screenshots import ROOT, _capture, _server

    with _server(ROOT / "notebooks/64_light_dark.py") as url:
        page.goto(url)
        table = page.locator('[data-cell-name="interactive_tables"] .et-root')
        grid = page.locator('[data-cell-name="interactive_tables"] .edg-root')
        table.wait_for(timeout=60_000)
        table.get_by_role("button", name="Next page", exact=True).click()
        values = table.locator("tbody tr td:first-child").all_text_contents()
        page.get_by_role("combobox").select_option("dark")
        expect(table).to_have_attribute("data-color-scheme", "dark")
        expect(grid).to_have_attribute("data-color-scheme", "dark")
        assert table.locator("tbody tr td:first-child").all_text_contents() == values
        screenshot = Path("/tmp/evidential-dark-demo.png")
        _capture(page, "theme_dark", screenshot)
        root = page.locator('[data-cell-name="theme_dark"] .et-root')
        assert painted_colors(page, [root]) == [[23, 27, 36]]
