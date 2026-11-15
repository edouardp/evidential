"""The shared gradient API paints marks and their scale strips in the shipped bundle."""

import runpy
from pathlib import Path

import pytest
from paint_helpers import painted_colors
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parents[2]


def test_centerline_is_visible_over_an_opaque_gradient_bar_without_blocking_hover(page, live_server):
    column = (
        col.bar("x", center=True)
        .gradient(scale=["#ff0000", "#0000ff"], min=-10, max=10)
        .scale(domain=(-10, 10), gridlines=True)
        .reference_band(-8, -4, color="#ffff00")
    )
    mount(page, live_server, [("Visible centerline", [{"x": 8}], [column])])
    line = page.locator(".et-mark-reference").first
    visible = painted_colors(page, [line], center=True)[0]
    line.evaluate("el => el.style.visibility = 'hidden'")
    hidden = painted_colors(page, [line], center=True)[0]
    assert max(abs(a - b) for a, b in zip(visible, hidden, strict=True)) > 30
    line.evaluate("el => el.style.visibility = ''")
    line.hover(force=True)
    expect(page.locator(".et-tooltip")).to_be_visible()


@pytest.mark.parametrize("combined", [False, True])
def test_centerline_keeps_points_and_their_composites_above_it(page, live_server, combined):
    column = col.bar("x", center=True).gradient(scale="viridis").point("a", size=12, color="red", outline=False)
    if combined:
        column = column.point("b", size=12, color="blue", outline=False)
    mount(page, live_server, [("Point overlay", [{"x": 8, "a": 0, "b": 0}], [column.scale(domain=(-10, 10))])])
    if combined:
        expect(page.locator(".et-point-composite")).to_have_count(1)
    line = page.locator(".et-mark-centerline")
    visible = painted_colors(page, [line], center=True)
    line.evaluate("el => el.style.visibility = 'hidden'")
    assert painted_colors(page, [line], center=True) == visible


def test_review_notebook_has_gradient_marks_scale_strips_and_no_vertical_row_scroll(page, live_server):
    _, definitions = runpy.run_path(str(ROOT / "notebooks/63_visual_gradients.py"))["app"].run()
    names = ("scalar_table", "distribution_table", "miniature_table", "scales_table")
    mount(page, live_server, [(name, definitions[name].widget, []) for name in names])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width='960px')")
    expect(page.locator(".et-axis-gradient")).to_have_count(10)
    expect(page.locator("#case-0 tbody tr")).to_have_count(6)
    expect(page.locator("#case-0 .et-mark-bar")).to_have_count(5)
    expect(page.locator("#case-0 .et-mark-point")).to_have_count(5)
    expect(page.locator("#case-1 .et-box-iqr")).to_have_count(3)
    expect(page.locator("#case-1 .et-density-band-run")).to_have_count(3)
    for strip in page.locator(".et-axis-gradient").all():
        expect(strip).to_have_css("height", "3px")
        assert "linear-gradient" in strip.evaluate("el => getComputedStyle(el).backgroundImage")
        assert strip.locator("xpath=ancestor::tbody").count() == 0
    for selector in (
        "#case-0 .et-mark-bar",
        "#case-0 .et-mark-range",
        "#case-1 .et-box-iqr",
        "#case-1 .et-density-band-run",
    ):
        assert page.locator(selector).first.evaluate("el => !!el.style.backgroundImage")
    for wrapper in page.locator(".et-scroller").all():
        assert wrapper.evaluate("el => el.scrollHeight <= el.clientHeight + 1")
    capture(page, "shared-visual-gradients.png")


def test_axis_strip_matches_the_plot_coordinates_and_uses_the_last_gradient(page, live_server):
    colors = {"scale": ["#ff0000", "#0000ff"], "min": 0, "max": 100}
    column = col.bar("x").gradient(**colors).point("target", color="black")
    column = column.scale(domain=(0, 100), gradient=True, axis_position="bottom")
    mount(page, live_server, [("Gradient key", [{"x": 80, "target": 50}], [column])])
    stripe = page.locator(".et-axis-gradient")
    track = page.locator("tbody .et-marks")
    a, b = stripe.bounding_box(), track.bounding_box()
    assert a["x"] == pytest.approx(b["x"], abs=0.5)
    assert a["width"] == pytest.approx(b["width"], abs=0.5)
    before = stripe.evaluate("el => el.style.backgroundImage")
    assert "rgb(255, 0, 0)" in before and "rgb(0, 0, 255)" in before
    point = page.locator(".et-mark-point")
    expect(point).to_have_css("background-color", "rgb(0, 0, 0)")
    point.hover()
    expect(page.locator(".et-tooltip-swatch")).to_have_css("background-color", "rgb(0, 0, 0)")


def test_point_lookup_and_tooltip_swatches_agree_with_the_color_strip(page, live_server):
    column = (
        col.points("a", shape="star", size=11)
        .gradient(
            stops=[
                {"value": 0, "color": "#ff0000"},
                {"value": 5, "color": "#888888"},
                {"value": 10, "color": "#0000ff"},
            ]
        )
        .scale(domain=(0, 10), gradient=True)
    )
    mount(page, live_server, [("Samples", [{"a": [0, 5, 10]}], [column])])
    points = page.locator(".et-mark-point")
    for index, color in enumerate(("rgb(255, 0, 0)", "rgb(136, 136, 136)", "rgb(0, 0, 255)")):
        expect(points.nth(index)).to_have_css("color", color)
        points.nth(index).hover(force=True)
        expect(page.locator(".et-tooltip-swatch")).to_have_css("background-color", color)
