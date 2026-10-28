"""Mark legends occupy the title area's right side and wrap without clipping."""

import runpy
from pathlib import Path

import pytest
from test_spec_conformance import capture, mount

from evidential import EvidentialTable, col
from scripts.api_screenshots import _server

pytestmark = pytest.mark.browser
NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/54_legends.py"


def test_legend_notebook_renders_stacks_and_nine_population_points(page, live_server):
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    tables = [definitions[name].widget for name in ("single", "double", "age_structure")]
    mount(page, live_server, [("", table, []) for table in tables])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '1100px')")
    assert page.locator("#case-0 .et-legend-group").count() == 1
    assert page.locator("#case-0 .et-legend-column").count() == 0
    assert page.locator("#case-2 .et-legend-column").count() == 0
    assert page.locator("#case-1 .et-legend-group").count() == 2
    assert page.locator(".et-legend-title").count() == 0
    assert page.locator("#case-0 .et-legends-outlined").count() == 0
    assert page.locator("#case-1 .et-legends-outlined").count() == 1
    assert page.locator("#case-1 .et-legends").evaluate("el => getComputedStyle(el).borderTopWidth") == "1px"
    assert page.locator("#case-1 .et-legend-column").all_text_contents() == ["Monthly cost", "Traffic mix"]
    headings = page.locator("#case-1 .et-legend-column").evaluate_all(
        "nodes => nodes.map(el => ({y: el.getBoundingClientRect().y, colon: getComputedStyle(el, '::after').content}))"
    )
    assert headings[1]["y"] > headings[0]["y"]
    assert all(heading["colon"] == '":"' for heading in headings)
    assert page.locator("#case-1 .et-legend-label").all_text_contents() == [
        "Storage",
        "Requests",
        "Data transfer",
        "Other",
        "Web",
        "Mobile",
        "Batch jobs",
    ]
    for index in (0, 1, 2):
        title = page.locator(f"#case-{index} .et-title-text").bounding_box()
        legend = page.locator(f"#case-{index} .et-legends").bounding_box()
        assert legend["x"] >= title["x"] + title["width"]
        assert abs(title["y"] - legend["y"]) < 1
    for group, stack in zip(
        page.locator("#case-1 .et-legend-group").all(),
        page.locator("#case-1 tbody tr").first.locator(".et-mark-stack").all(),
        strict=True,
    ):
        assert group.locator(".et-legend-swatch").evaluate_all(
            "nodes => nodes.map(el => getComputedStyle(el).backgroundColor)"
        ) == stack.locator(".et-mark-stack-seg").evaluate_all(
            "nodes => nodes.map(el => getComputedStyle(el).backgroundColor)"
        )
    assert page.locator("#case-2 .et-legend-label").all_text_contents() == [
        "0–9",
        "10–19",
        "20–29",
        "30–39",
        "40–49",
        "50–59",
        "60–69",
        "70–79",
        "80+",
    ]
    assert page.locator("#case-2 tbody tr").count() == 12
    assert page.locator("#case-2 .et-mark-point").count() == 108
    assert page.locator("#case-2 .et-mark-range").count() == 12
    assert page.locator("#case-2 .et-legend-swatch-range").count() == 0
    assert page.locator("#case-2 .et-legend-swatch").evaluate_all(
        "nodes => nodes.map(el => getComputedStyle(el).backgroundColor)"
    ) == page.locator("#case-2 tbody tr").first.locator(".et-mark-point").evaluate_all(
        "nodes => nodes.map(el => getComputedStyle(el).backgroundColor)"
    )
    capture(page, "legends-wide.png")
    for width in (700, 420, 310, 280):
        page.locator("section").evaluate_all(
            "(nodes, width) => nodes.forEach(el => el.style.width = width + 'px')", width
        )
        for index in (0, 1, 2):
            geometry = page.locator(f"#case-{index} .et-titlebar").evaluate("""bar => {
                const bounds = bar.getBoundingClientRect();
                const title = bar.querySelector('.et-title-text').getBoundingClientRect();
                const key = bar.querySelector('.et-legends').getBoundingClientRect();
                return {width: bounds.width, scroll: bar.scrollWidth,
                    separate: key.left >= title.right - 1 || key.top >= title.bottom - 1,
                    inside: [...bar.querySelectorAll('.et-legend-item')].every(el => {
                        const r = el.getBoundingClientRect();
                        return r.left >= bounds.left - 1 && r.right <= bounds.right + 1;
                    }),
                    unbroken: [...bar.querySelectorAll('.et-legend-label')].every(el => {
                        const range = document.createRange();
                        range.selectNodeContents(el);
                        return range.getClientRects().length === 1;
                    })};
            }""")
            assert geometry["separate"]
            assert geometry["inside"]
            assert geometry["unbroken"]
            assert geometry["scroll"] <= geometry["width"] + 1
    positions = page.locator("#case-2 .et-legend-item").evaluate_all(
        "nodes => nodes.map(el => Math.round(el.getBoundingClientRect().top))"
    )
    assert len(set(positions)) > 1
    capture(page, "legends-narrow.png")


def test_legends_without_titles_and_theme_colors(page, live_server):
    table = EvidentialTable(
        [{"actual": 8, "target": 10, "form": ["W", "D", "L"]}],
        columns=[
            col.bar("actual").point("target", color="white").title("Performance").legend(),
            col.strip("form", colors={"W": "#4ade80", "D": "#9ca3af", "L": "#f87171"}).legend(
                {"W": "Win", "D": "Draw", "L": "Loss"}
            ),
        ],
        theme={"background": "#111827", "text": "#f9fafb", "muted": "#cbd5e1", "accent": "#a78bfa"},
        width="100%",
        page_size=0,
    )
    mount(page, live_server, [("", table, [])])
    assert page.locator(".et-title-text").count() == 0
    assert page.locator(".et-legend-column").all_text_contents() == ["Performance", "Form"]
    assert page.locator(".et-legend-label").all_text_contents() == ["Actual", "Target", "Win", "Draw", "Loss"]
    assert page.locator(".et-legend-swatch-bar").evaluate("el => getComputedStyle(el).backgroundColor") == page.locator(
        ".et-mark-bar"
    ).evaluate("el => getComputedStyle(el).backgroundColor")
    assert page.locator(".et-legend-label").first.evaluate("el => getComputedStyle(el).color") != "rgb(249, 250, 251)"
    assert page.locator(".et-legends").get_attribute("aria-label") == "Legend"
    assert page.locator(".et-legends [aria-hidden=true]").count() == 5  # Five decorative swatches.
    capture(page, "legends-dark.png")


def test_marimo_legend_has_square_spaced_chips_and_respects_the_right_edge(page):
    with _server(NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        root = page.locator('[data-cell-name="two_legends"] .et-root')
        root.locator(".et-legend-label").last.wait_for()
        population = page.locator('[data-cell-name="population_points"] .et-root')
        population.locator(".et-mark-point").last.wait_for()
        assert population.locator(".et-mark-point").count() == 108
        assert population.locator(".et-point-connector").count() == 12
        assert population.locator(".et-legend-label").count() == 9
        population.locator(".et-mark-point").first.hover()
        assert population.locator(".et-tooltip-name").inner_text() == "0–9:"
        assert population.locator(".et-tooltip-value").inner_text().startswith("33.")
        assert population.locator(".et-mark-point").first.get_attribute("title") is None
        strips = page.locator('[data-cell-name="football_form"] .et-root')
        strips.locator(".et-strip-seg").last.wait_for()
        assert strips.locator(".et-strip-seg").count() == 48
        targets = page.locator('[data-cell-name="target_points"] .et-root')
        targets.locator(".et-mark-point").last.wait_for()
        assert targets.locator(".et-mark-bar").count() == 4
        assert targets.locator(".et-mark-point").count() == 4
        dumbbells = page.locator('[data-cell-name="dumbbell_legend"] .et-root')
        dumbbells.locator(".et-mark-point").last.wait_for()
        assert dumbbells.locator(".et-mark-point").count() == 8
        for width in (1100, 700, 420, 360, 310, 280):
            root.evaluate("(el, width) => el.style.width = width + 'px'", width)
            geometry = root.evaluate("""root => {
                const legend = root.querySelector('.et-legends');
                const bounds = legend.getBoundingClientRect();
                const style = getComputedStyle(legend);
                const table = root.querySelector('.et-scroller').getBoundingClientRect();
                return {keyRight: bounds.right - parseFloat(style.paddingRight) - parseFloat(style.borderRightWidth),
                    tableRight: table.right,
                    labels: [...legend.querySelectorAll('.et-legend-label')].map(el => {
                        const range = document.createRange(); range.selectNodeContents(el);
                        return {right: range.getBoundingClientRect().right, lines: range.getClientRects().length,
                            color: getComputedStyle(el).color};
                    }),
                    swatches: [...legend.querySelectorAll('.et-legend-swatch')].map(el => {
                        const r = el.getBoundingClientRect(); return {width: r.width, height: r.height};
                    }),
                    separated: [...legend.querySelectorAll('.et-legend-items')].every(list => {
                        const keys = [...list.children].map(el => el.getBoundingClientRect());
                        return keys.every((key, i) => !i || key.y !== keys[i-1].y || key.left - keys[i-1].right >= 8);
                    })};
            }""")
            assert geometry["keyRight"] <= geometry["tableRight"]
            assert geometry["separated"]
            for swatch in geometry["swatches"]:
                assert swatch["width"] == pytest.approx(swatch["height"], abs=0.1)
            for name in geometry["labels"]:
                assert name["right"] < geometry["keyRight"]
                assert name["lines"] == 1
                assert "/ 0.72" in name["color"]
        capture(page, "legends-marimo.png")


def test_strips_targets_and_dumbbells_have_matching_color_and_shape_keys(page, live_server):
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    tables = [definitions[name].widget for name in ("form_table", "target_table", "dumbbell_table")]
    mount(page, live_server, [("", table, []) for table in tables])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '950px')")
    assert page.locator("#case-0 .et-legend-label").all_text_contents() == ["Win", "Draw", "Loss"]
    assert page.locator("#case-0 .et-strip-seg").count() == 48
    assert page.locator("#case-1 .et-legend-label").all_text_contents() == ["Completion", "Target"]
    assert page.locator("#case-1 .et-legend-column").all_text_contents() == ["Completion vs target"]
    assert page.locator("#case-1 .et-legend-swatch-bar").count() == 1
    assert page.locator("#case-1 .et-legend-swatch-point").count() == 1
    assert page.locator("#case-1 .et-mark-label-text").all_text_contents() == ["82%", "67%", "94%", "76%"]
    assert page.locator("#case-2 .et-legend-label").all_text_contents() == [
        "Change",
        "Change (negative)",
        "Before",
        "After",
    ]
    assert page.locator("#case-2 .et-legend-swatch-range").count() == 2
    assert page.locator("#case-2 .et-legend-swatch-points").count() == 2
    assert page.locator("#case-2 .et-range-direction").count() == 3
    negative = page.locator("#case-2 tbody tr").nth(1).locator(".et-mark-range")
    swatch = page.locator("#case-2 .et-legend-swatch-range").nth(1)
    assert negative.evaluate("el => getComputedStyle(el).backgroundColor") == swatch.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    capture(page, "legends-more-graphics.png")
