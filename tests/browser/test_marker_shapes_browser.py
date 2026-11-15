"""Marker geometry, outlines, legends, overlap sectors and rating glyphs in real browsers."""

import runpy
from pathlib import Path

import pytest
from paint_helpers import assert_colors, painted_colors
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parents[2]


def test_marker_notebook_shapes_legends_rotation_and_segmented_stars(page, live_server):
    _, definitions = runpy.run_path(str(ROOT / "notebooks/62_marker_shapes.py"))["app"].run()
    names = (
        "small_shapes",
        "large_shapes",
        "rotation_table",
        "shape_series",
        "repeated_table",
        "overlap_table",
        "sparkline_table",
    )
    mount(page, live_server, [(name, definitions[name].widget, []) for name in names])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width='960px')")
    expect(page.locator("#case-0 .et-mark-point")).to_have_count(8)
    expect(page.locator("#case-1 .et-mark-point")).to_have_count(8)
    for shape in definitions["marker_shapes"]:
        marker = page.locator(f'#case-1 .et-mark-point[data-shape="{shape}"]')
        if shape == "circle":
            assert "1px" in marker.evaluate("el => getComputedStyle(el).boxShadow")
        else:
            path = marker.locator("path")
            expect(path).to_have_css("stroke", "rgb(23, 37, 84)")
            expect(path).to_have_css("stroke-width", "1px")
    expect(page.locator('#case-2 .et-mark-point[data-shape="triangle"][data-angle="270"]')).to_have_count(1)
    expect(page.locator('#case-2 .et-mark-point[data-shape="cross"][data-angle="45"]')).to_have_count(1)
    keys = page.locator("#case-3 .et-legend-swatch")
    assert keys.evaluate_all("nodes => nodes.map(n => n.dataset.shape)") == ["square", "triangle", "star", "star"]
    expect(page.locator('#case-3 .et-legend-swatch[data-shape="triangle"] path')).to_have_css("stroke", "none")
    medals = page.locator("#case-4 tbody tr").first.locator("td").nth(1)
    assert medals.locator(".et-symbol-box").first.bounding_box()["width"] == pytest.approx(
        float(medals.evaluate("el => parseFloat(getComputedStyle(el).fontSize)")) * 0.8, abs=0.1
    )
    expect(page.locator('#case-4 [data-hollow="true"] path[fill="none"]')).to_have_count(4)
    overlaps = page.locator("#case-5 tbody tr")
    expect(overlaps.first.locator(".et-point-composite")).to_have_count(4)
    expect(overlaps.nth(1).locator(".et-point-composite")).to_have_count(4)
    expect(overlaps.last.locator(".et-point-composite")).to_have_count(0)
    star = overlaps.first.locator("td").last.locator(".et-point-composite")
    expect(star.locator("clipPath")).to_have_count(3)
    expect(star.locator("path[stroke]")).to_have_count(2)
    star.hover()
    expect(page.locator("#case-5 .et-tooltip-name")).to_have_text(["Star Before:", "Star After:"])
    assert page.locator("#case-6 .et-marker-svg").count() == 14
    capture(page, "marker-shapes.png")


def test_sparkline_hover_finds_shaped_endpoints_and_invisible_middle_observations(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Marker inspection",
                [{"series": [10, 20, 30]}],
                [
                    col.sparkline("series", markers="ends", shape="star", outline="black"),
                ],
            )
        ],
    )
    targets = page.locator('[data-sparkline-observation="true"]')
    expect(targets).to_have_count(3)
    for index, value in enumerate((10, 20, 30)):
        targets.nth(index).hover(force=True)
        expect(page.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text(str(value))


def test_different_shapes_and_angles_do_not_merge_and_opaque_matching_shapes_do(page, live_server):
    columns = [
        col.point("a", shape="square", color="red").point("b", shape="triangle", color="blue").title("Mixed"),
        col.point("c", shape="triangle", color="red")
        .point("d", shape="triangle", angle=90, color="blue")
        .title("Angles"),
        col.point("e", shape="cross", angle=45, color="red", outline="black")
        .point("f", shape="cross", angle=45, color="blue", outline="black")
        .title("Matching"),
        col.point("g", color="red", size=12)
        .point("h", color="blue", size=12)
        .point("i", color="green", shape="square", size=12)
        .title("Paint order"),
    ]
    columns = [column.scale(domain=(0, 100)) for column in columns]
    mount(page, live_server, [("Compatible clusters", [dict.fromkeys("abcdefghi", 50)], columns, {"width": 960})])
    page.locator("section").evaluate("el => el.style.width='960px'")
    cells = page.locator("tbody td")
    expect(cells.nth(0).locator(".et-point-composite")).to_have_count(0)
    expect(cells.nth(1).locator(".et-point-composite")).to_have_count(0)
    expect(cells.nth(2).locator(".et-point-composite")).to_have_count(1)
    expect(cells.nth(2).locator(".et-point-composite clipPath").first.locator("path")).to_have_attribute(
        "transform", "rotate(45)"
    )
    square = cells.nth(3).locator('.et-mark-point[data-shape="square"]')
    assert_colors(painted_colors(page, [square], center=True), [[0, 128, 0]])
