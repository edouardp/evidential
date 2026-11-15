"""Marker geometry, outlines, legends, overlap sectors and rating glyphs in real browsers."""

import math
import runpy
from base64 import b64encode
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
        "bar_overlap_table",
    )
    mount(page, live_server, [(name, definitions[name].widget, []) for name in names])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width='960px')")
    page.locator("section").nth(5).evaluate("el => el.style.width='1100px'")
    page.locator("section").nth(7).evaluate("el => el.style.width='1100px'")
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
    expect(overlaps.first.locator(".et-point-composite")).to_have_count(5)
    expect(overlaps.nth(1).locator(".et-point-composite")).to_have_count(5)
    expect(overlaps.last.locator(".et-point-composite")).to_have_count(0)
    star = overlaps.first.locator("td").nth(4).locator(".et-point-composite")
    expect(star.locator("clipPath")).to_have_count(3)
    expect(star.locator("path[stroke]")).to_have_count(2)
    star.hover()
    expect(page.locator("#case-5 .et-tooltip-name")).to_have_text(["Star Before:", "Star After:"])
    assert page.locator("#case-6 .et-marker-svg").count() == 14
    bars = page.locator("#case-7 tbody tr")
    expect(bars.first.locator(".et-point-composite")).to_have_count(5)
    expect(bars.nth(1).locator(".et-point-composite")).to_have_count(5)
    expect(bars.last.locator(".et-point-composite")).to_have_count(0)
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


@pytest.mark.parametrize("count,angle", [(2, 0), (3, 0), (4, 0), (3, 90), (3, 45), (2, 180)])
def test_bar_composites_paint_equal_bands_and_keep_all_tooltip_values(page, live_server, count, angle):
    colors = ["#ff0000", "#008000", "#0000ff", "#ffd700"][:count]
    column = col.point("a", shape="bar", angle=angle, size=30, color=colors[0], outline="black")
    for index, color in enumerate(colors[1:], start=1):
        column = column.point(chr(97 + index), shape="bar", angle=angle, size=30, color=color, outline="black")
    mount(page, live_server, [("Bar bands", [dict.fromkeys("abcd", 50)], [column.scale(domain=(0, 100))])])
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
    composite = page.locator(".et-point-composite")
    expect(composite).to_have_count(1)
    expect(composite.locator('path[stroke="rgb(0, 0, 0)"]')).to_have_count(count)
    bounds = composite.bounding_box()
    points = []
    for index in range(count):
        distance = 30 * ((index + 0.5) / count - 0.5)
        points.append(
            {
                "x": int(bounds["x"] + bounds["width"] / 2 - math.sin(math.radians(angle)) * distance),
                "y": int(bounds["y"] + bounds["height"] / 2 + math.cos(math.radians(angle)) * distance),
            }
        )
    png = b64encode(page.screenshot()).decode()
    actual = page.evaluate(
        """async ({png, points}) => {
            const image = new Image(); image.src = 'data:image/png;base64,' + png; await image.decode();
            const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
            const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
            return points.map(({x, y}) => [...ctx.getImageData(x, y, 1, 1).data].slice(0, 3));
        }""",
        {"png": png, "points": points},
    )
    assert_colors(actual, [[255, 0, 0], [0, 128, 0], [0, 0, 255], [255, 215, 0]][:count])
    composite.hover()
    expect(page.locator(".et-tooltip-name")).to_have_count(count)
