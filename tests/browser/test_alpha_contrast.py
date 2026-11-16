"""Contrast follows painted alpha layers, host surfaces and live theme changes."""

import runpy
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, label

pytestmark = pytest.mark.browser
STOPS = [
    {"value": 0, "color": "rgba(255,255,255,0.1)"},
    {"value": 0.04, "color": "rgba(220,38,38,0.22)"},
    {"value": 0.5, "color": "#8b0000"},
]
BLACK, WHITE = "rgb(0, 0, 0)", "rgb(255, 255, 255)"


@pytest.mark.parametrize("surface,expected", [("white", BLACK), ("#111827", WHITE)])
def test_issue_8_translucent_cells_and_chips_use_light_or_dark_surfaces(page, live_server, surface, expected):
    rows = [
        {"name": name, "rate": value, "chip": value, "explicit": value, "explicit_chip": value}
        for name, value in [("Faint", 0.04), ("Clear", 0), ("Solid", 0.5)]
    ]
    columns = [
        col.text("name"),
        col.percent("rate").color(stops=STOPS),
        col.percent("chip").chip(stops=STOPS),
        col.percent("explicit").color(stops=STOPS).font_color("rebeccapurple"),
        col.percent("explicit_chip").chip(stops=STOPS).font_color("rebeccapurple"),
    ]
    mount(
        page,
        live_server,
        [
            (
                "Failure rates",
                rows,
                columns,
                {"row_shading": False, "theme": {"background": surface, "surface": surface}},
            )
        ],
    )
    cells = page.locator("tbody tr").first.locator("td")
    expect(cells.nth(1)).to_have_css("color", expected)
    expect(cells.nth(2).locator(".et-chip")).to_have_css("color", expected)
    expect(cells.nth(3)).to_have_css("color", "rgb(102, 51, 153)")
    expect(cells.nth(4).locator(".et-chip")).to_have_css("color", "rgb(102, 51, 153)")
    expect(page.locator("tbody tr").last.locator("td").nth(1)).to_have_css("color", WHITE)
    assert "0.2" in cells.nth(1).evaluate("el => el.style.getPropertyValue('--et-cell-fill')")


@pytest.mark.parametrize("frozen", [0, 2])
def test_stripes_hover_and_frozen_cells_use_the_same_painted_layers(page, live_server, frozen):
    rows = [{"name": name, "rate": 0.04, "chip": 0.04} for name in ["Plain", "Stripe"]]
    columns = [col.text("name"), col.percent("rate").color(stops=STOPS), col.percent("chip").chip(stops=STOPS)]
    mount(
        page,
        live_server,
        [
            (
                "Layered paint",
                rows,
                columns,
                {"freeze_columns": frozen, "theme": {"background": "white", "shading": "#111827", "hover": "#111827"}},
            )
        ],
    )
    plain = page.locator("tbody tr").first.locator("td")
    striped = page.locator("tbody tr").last.locator("td")
    page.mouse.move(0, 0)
    expect(plain.nth(1)).to_have_css("color", BLACK)
    expect(striped.nth(1)).to_have_css("color", WHITE)
    expect(striped.nth(2).locator(".et-chip")).to_have_css("color", WHITE)
    plain.nth(0).hover()
    expect(plain.nth(1)).to_have_css("color", WHITE)
    page.mouse.move(0, 0)
    expect(plain.nth(1)).to_have_css("color", BLACK)


@pytest.mark.parametrize("surface,expected", [("white", BLACK), ("#111827", WHITE)])
def test_translucent_row_colors_apply_to_values_and_row_numbers(page, live_server, surface, expected):
    mount(
        page,
        live_server,
        [
            (
                "Row colours",
                [{"name": "Faint", "fill": "#dc262638"}],
                [col.text("name")],
                {
                    "row_shading": False,
                    "row_numbers": True,
                    "row_conditional_colors": "fill",
                    "theme": {"background": surface},
                },
            )
        ],
    )
    for cell in page.locator("tbody td").all():
        expect(cell).to_have_css("color", expected)


@pytest.mark.parametrize("surface,expected", [("white", BLACK), ("#111827", WHITE)])
def test_inside_labels_include_bar_opacity_gradient_alpha_and_cell_fill(page, live_server, surface, expected):
    inside = label.position("inside end")
    columns = [
        col.bar("solid", color="#00000066", label=inside).scale(domain=(0, 10)),
        col.bar("gradient", label=inside)
        .gradient(
            stops=[
                {"value": 0, "color": "#00000000"},
                {"value": 10, "color": "#00000033"},
            ]
        )
        .scale(domain=(0, 10)),
        col.bar("cell", color="#ffffff33", label=inside).scale(domain=(0, 10)).cell_style(background="#111827"),
        col.bar("explicit", color="#00000033", label=inside.font_color("rebeccapurple")).scale(domain=(0, 10)),
    ]
    mount(
        page,
        live_server,
        [
            (
                "Bar labels",
                [dict.fromkeys(["solid", "gradient", "cell", "explicit"], 8)],
                columns,
                {"width": 1100, "row_shading": False, "theme": {"background": surface}},
            )
        ],
    )
    labels = page.locator(".et-mark-label")
    expect(labels.nth(0)).to_have_css("color", expected)
    expect(labels.nth(1)).to_have_css("color", expected)
    expect(labels.nth(2)).to_have_css("color", WHITE)
    expect(labels.nth(3)).to_have_css("color", "rgb(102, 51, 153)")


def test_transparent_host_changes_refresh_contrast_and_media_changes_switch_scheme(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Host background",
                [{"rate": 0.04}],
                [col.percent("rate").color(stops=STOPS)],
                {"row_shading": False, "theme": {"background": "transparent", "surface": "Canvas"}},
            )
        ],
    )
    cell = page.locator("tbody td")
    root = page.locator(".et-root")
    count = root.locator("..").get_attribute("data-render-count")
    expect(cell).to_have_css("color", BLACK)
    page.locator("#case-0").evaluate("el => el.style.backgroundColor = '#111827'")
    expect(cell).to_have_css("color", WHITE)
    page.locator("#case-0").evaluate("el => el.style.backgroundColor = ''")
    expect(cell).to_have_css("color", BLACK)
    assert root.locator("..").get_attribute("data-render-count") == count
    page.add_style_tag(
        content="@media (prefers-color-scheme: dark) { #case-0 {background:#111827; color-scheme:dark;} }"
    )
    page.emulate_media(color_scheme="dark")
    expect(cell).to_have_css("color", WHITE)
    page.emulate_media(color_scheme="light")
    expect(cell).to_have_css("color", BLACK)
    assert int(root.locator("..").get_attribute("data-render-count")) > int(count)


def test_frozen_surface_can_differ_from_the_ordinary_host_background(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Different surfaces",
                [{"name": "A", "rate": 0.04, "chip": 0.04}],
                [col.text("name"), col.percent("rate").color(stops=STOPS), col.percent("chip").chip(stops=STOPS)],
                {"freeze_columns": 2, "row_shading": False, "theme": {"surface": "#111827"}},
            )
        ],
    )
    cells = page.locator("tbody td")
    expect(cells.nth(1)).to_have_css("color", WHITE)
    expect(cells.nth(2).locator(".et-chip")).to_have_css("color", BLACK)


@pytest.mark.parametrize("surface,expected", [("white", BLACK), ("#111827", WHITE)])
def test_stack_labels_composite_each_segment_once(page, live_server, surface, expected):
    stack = col.stacked_bar("a", "b", colors=["#dc262638", "#2563eb26"], labels=True)
    mount(
        page,
        live_server,
        [
            (
                "Translucent stack",
                [{"a": 40, "b": 60}],
                [stack],
                {"row_shading": False, "theme": {"background": surface}},
            )
        ],
    )
    labels = page.locator(".et-mark-stack-label")
    for item in labels.all():
        expect(item).to_have_css("color", expected)


def test_colour_notebook_demonstrates_the_same_fills_on_both_surfaces(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks/12_color_scales.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    mount(page, live_server, [(name, definitions[name].widget, []) for name in ["contrast_light", "contrast_dark"]])
    for index, expected in enumerate([BLACK, WHITE]):
        expect(page.locator(f"#case-{index} .et-color-cell").first).to_have_css("color", expected)
        expect(page.locator(f"#case-{index} .et-chip").first).to_have_css("color", expected)
        expect(page.locator(f"#case-{index} .et-mark-label").first).to_have_css("color", expected)
    capture(page, "alpha-contrast-light-dark.png")
