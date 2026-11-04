"""Y-value gradients render through the public fluent API and actual notebook demo."""

import runpy
from base64 import b64encode
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col

pytestmark = pytest.mark.browser


def test_notebook_gradient_demo_renders_all_styles_and_matching_tooltip_colors(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks/40_sparklines_and_booleans.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["gradient_table"].widget
    mount(page, live_server, [("Gradient styles", table, [])])
    expect(page.locator("tbody .et-sparkline")).to_have_count(15)
    cells = page.locator("tbody tr").first.locator("td")
    bars = cells.nth(1).locator("rect")
    points = cells.nth(2).locator("circle")
    expect(bars).to_have_count(7)
    expect(points).to_have_count(7)
    for marks in (bars, points):
        expect(marks.first).to_have_attribute("fill", "#b2182b")
        expect(marks.nth(3)).to_have_attribute("fill", "#b8bcc2")
        expect(marks.last).to_have_attribute("fill", "#2166ac")
    expect(cells.nth(3).locator("polyline")).to_have_count(1)
    expect(cells.nth(4).locator("polygon")).to_have_count(1)
    assert cells.nth(3).locator("polyline").get_attribute("stroke").startswith("url(#et-sparkline-gradient-")
    # Explicit colors belong to individual observations, never outgoing intervals.
    override = page.locator("tbody tr").last.locator("td")
    for index in (1, 2, 5):
        selector = "circle" if index == 2 else "rect"
        expect(override.nth(index).locator(selector).nth(2)).to_have_attribute("fill", "#7c3aed")
    expect(override.nth(3).locator("circle").nth(2)).to_have_attribute("fill", "#7c3aed")
    expect(override.nth(3).locator("polyline")).to_have_count(2)
    expect(override.nth(4).locator("polygon")).to_have_count(2)
    points.last.hover(force=True)
    tip = page.locator(".et-tooltip")
    expect(tip).to_be_visible()
    expect(tip.locator(".et-tooltip-content > .et-tooltip-value")).to_have_text("10")
    expect(tip.locator(".et-tooltip-swatch")).to_have_css("background-color", "rgb(33, 102, 172)")
    capture(page, "sparkline-y-gradients.png")


def test_auto_gradient_ranges_cover_all_pages_and_recompute_on_search(page, live_server):
    data = [{"name": "Keep", "history": [0, 5]}, {"name": "Other", "history": [10, 20]}]
    mount(
        page,
        live_server,
        [
            (
                "Automatic gradient",
                data,
                [
                    col.text("name"),
                    col.sparkline("history", type="bar").color(scale=["red", "blue"]),
                ],
                {"page_size": 1, "search": True},
            )
        ],
    )
    marks = page.locator("tbody rect")
    expect(marks.first).to_have_attribute("fill", "#ff0000")
    initial = marks.last.get_attribute("fill")
    assert initial not in ("#ff0000", "#0000ff")
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(marks.last).to_have_attribute("fill", "#0000ff")
    page.get_by_role("button", name="Previous page", exact=True).click()
    expect(marks.last).to_have_attribute("fill", initial)
    page.get_by_role("searchbox").fill("Keep")
    expect(marks.last).to_have_attribute("fill", "#0000ff")


def _sample_svg(page, svg, samples):
    """Sample actual browser-painted SVG pixels at viewBox coordinates."""
    bounds = svg.bounding_box()
    png = b64encode(page.screenshot()).decode()
    return page.evaluate(
        """async ({png, bounds, samples}) => {
            const image = new Image(); image.src = 'data:image/png;base64,' + png;
            await image.decode();
            const canvas = document.createElement('canvas');
            canvas.width = image.width; canvas.height = image.height;
            const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
            return samples.map(([x, y]) => [...ctx.getImageData(
                Math.floor(bounds.x + x), Math.floor(bounds.y + y), 1, 1).data].slice(0, 3));
        }""",
        {"png": png, "bounds": bounds, "samples": samples},
    )


def test_vertical_fills_paint_thresholds_alpha_ramps_and_clamped_endpoints(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Vertical paints",
                [
                    {"threshold": [60, 60], "fade": [0, 60, 60], "anomaly": [3, 3]},
                    {"threshold": [60, 60], "fade": [0, 60, 60], "anomaly": [-3, -3]},
                ],
                [
                    col.sparkline("threshold", type="area", width=300, height=120, fill_opacity=1).color(
                        stops=[
                            {"value": 0, "color": "#00aa00"},
                            {"value": 40, "color": "#00aa00"},
                            {"value": 40.001, "color": "#ff0000"},
                            {"value": 60, "color": "#ff0000"},
                        ]
                    ),
                    col.sparkline("fade", type="area", width=300, height=120, color="#00aa00", fill_opacity=(0, 1)),
                    col.sparkline("anomaly", type="area", width=300, height=120).color(
                        stops=[
                            {"value": -1, "color": "#ff0000"},
                            {"value": 0, "color": "#ffffff00"},
                            {"value": 1, "color": "#0000ff"},
                        ]
                    ),
                ],
                {"border": False, "row_shading": False, "stretch": False, "width": 1100},
            )
        ],
    )
    # Enlarge just this fixture to sample fills away from antialiased edges.
    page.add_style_tag(content=".et-sparkline { width: 300px; height: 120px; }")
    page.locator("section").evaluate("node => node.style.width = '1100px'")
    rows = page.locator("tbody tr")
    first = rows.first.locator(".et-sparkline")
    # Horizontal plateau: both halves have the same color at each height.
    threshold = _sample_svg(page, first.nth(0), [(80, 20), (220, 20), (80, 80), (220, 80)])
    assert threshold == [[255, 0, 0], [255, 0, 0], [0, 170, 0], [0, 170, 0]]
    fade = _sample_svg(page, first.nth(1), [(240, 8), (240, 109)])
    assert fade[0][0] < 25 and fade[0][1] < 180  # opaque green near the edge
    assert all(channel > 230 for channel in fade[1])  # white shows through near zero
    assert _sample_svg(page, first.nth(2), [(150, 20)])[0] == [0, 0, 255]  # y > 1 clamps blue
    assert _sample_svg(page, rows.last.locator(".et-sparkline").nth(2), [(150, 100)])[0] == [255, 0, 0]
    ids = page.locator("linearGradient").evaluate_all("nodes => nodes.map(node => node.id)")
    assert len(ids) == len(set(ids))
    capture(page, "sparkline-vertical-paints.png")


def test_vertical_area_demo_has_fades_bands_and_gaps(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks/40_sparklines_and_booleans.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    mount(
        page,
        live_server,
        [
            ("Vertical area demos", definitions["vertical_area_table"].widget, []),
            ("Fade then threshold", definitions["fade_threshold_table"].widget, []),
        ],
    )
    expect(page.locator("#case-0 tbody .et-sparkline")).to_have_count(12)
    expect(page.locator("#case-0 tbody tr").last.locator(".et-sparkline").first.locator("polyline")).to_have_count(2)
    expect(page.locator("#case-1 tbody .et-sparkline")).to_have_count(3)
    stops = page.locator("#case-1 tbody .et-sparkline").first.locator("linearGradient").last.locator("stop")
    expect(stops.first).to_have_attribute("stop-opacity", "0")
    expect(stops.last).to_have_attribute("stop-color", "#ed1c24")
    expect(stops.last).to_have_attribute("stop-opacity", "1")
    capture(page, "sparkline-vertical-area-demo.png")


def test_combined_alpha_threshold_and_sloping_line_paint_by_height(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Fade and threshold",
                [{"area": [60, 60], "line": [0, 60]}],
                [
                    col.sparkline("area", type="area", width=300, height=120).color(
                        stops=[
                            {"value": 0, "color": "#00aa0000"},
                            {"value": 40, "color": "#00aa00"},
                            {"value": 40.001, "color": "red"},
                            {"value": 60, "color": "red"},
                        ]
                    ),
                    col.sparkline("line", width=300, height=120).color(scale=["red", "blue"], min=0, max=60),
                ],
                {"border": False, "row_shading": False, "width": 800},
            )
        ],
    )
    page.add_style_tag(
        content="section { width: 800px !important; } .et-sparkline { width: 300px; height: 120px; } .et-sparkline polyline { stroke-width: 3px; }"
    )
    svg = page.locator("tbody .et-sparkline")
    red, green, transparent = _sample_svg(page, svg.first, [(150, 20), (150, 50), (150, 115)])
    assert red == [255, 0, 0]
    assert green[1] > green[0] + 100 and green[0] < 50
    assert all(channel > 240 for channel in transparent)
    low, high = _sample_svg(page, svg.last, [(25, 109), (275, 11)])
    capture(page, "sparkline-fade-threshold-and-line.png")
    assert low[0] > low[2] + 20
    assert high[2] > high[0] + 20
