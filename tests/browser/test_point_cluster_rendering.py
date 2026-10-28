"""Segmented circles use bounded pixel clusters and preserve inspection data."""

import runpy
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import EvidentialTable, col
from scripts.api_screenshots import _capture, _server

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parents[2]


def test_dumbbell_overlap_examples_sectors_outlines_and_tooltips(page, live_server):
    _, definitions = runpy.run_path(str(ROOT / "notebooks/48_dumbbell_plots.py"))["app"].run()
    table = definitions["overlap_table"].widget
    transparent = definitions["transparent_table"].widget
    mount(page, live_server, [("Overlapping points", table, []), ("Translucent", transparent, [])])
    page.locator("section").first.evaluate("el => el.style.width='1100px'")
    rows = page.locator("#case-0 tbody tr")
    for index, count in enumerate([2, 3, 4, 4]):
        glyph = rows.nth(index).locator(".et-point-composite")
        expect(glyph).to_have_attribute("data-point-count", str(count))
        expect(glyph.locator("path[fill]:not([fill=none])")).to_have_count(count)
        assert rows.nth(index).locator(".et-mark-point").count() == count
    expect(rows.nth(4).locator(".et-point-composite")).to_have_count(2)
    expect(rows.nth(5).locator(".et-point-composite")).to_have_count(0)
    expect(page.locator("#case-1 .et-point-composite")).to_have_count(0)
    for index, names in [
        (0, ["Before:", "After:"]),
        (1, ["Before:", "After:", "Target:"]),
        (2, ["Before:", "After:", "Target:", "Forecast:"]),
    ]:
        rows.nth(index).locator(".et-point-composite").hover()
        expect(page.locator("#case-0 .et-tooltip-name")).to_have_text(names)
    cell = rows.nth(2).locator("td").last
    cell.focus()
    expect(cell.locator(".et-point-composite.et-tooltip-active")).to_have_count(1)
    expect(page.locator("#case-0 .et-tooltip-name")).to_have_count(4)
    capture(page, "point-clusters-dumbbell.png")
    # Existing equal dumbbell endpoints also preserve the two coloured outlines.
    signed = definitions["signed"].widget
    mount(page, live_server, [("Equal endpoints", signed, [])])
    glyph = page.locator("tbody tr").nth(2).locator(".et-point-composite")
    expect(glyph.locator("path[stroke]")).to_have_count(2)
    assert glyph.locator("path[stroke]").evaluate_all("nodes => nodes.map(el => el.getAttribute('stroke'))") == [
        "rgb(47, 95, 168)",
        "rgb(204, 17, 17)",
    ]


def test_resize_recomputes_one_pixel_clusters_without_chain_merging(page, live_server):
    fields = {f"v{i}": f"Series {i}" for i in range(21)}
    data = {"case": "A long chain", **{field: 20 + i * 0.2 for i, field in enumerate(fields)}}
    table = EvidentialTable(
        [data],
        columns=[col.text("case"), col.points(fields).scale(domain=(0, 100))],
        width="100%",
        search=False,
        page_size=0,
    )
    mount(page, live_server, [("A bounded sweep", table, [])])
    section = page.locator("section")
    section.evaluate("el => el.style.width='600px'")
    expect(page.locator(".et-point-composite").first).to_be_visible()
    sizes = page.locator(".et-point-composite").evaluate_all("nodes => nodes.map(el => Number(el.dataset.pointCount))")
    assert all(size < 21 for size in sizes)
    # This very wide screen-space range separates every point by more than 1px.
    section.evaluate("el => el.style.width='3000px'")
    expect(page.locator(".et-point-composite")).to_have_count(0)
    section.evaluate("el => el.style.width='600px'")
    expect(page.locator(".et-point-composite").first).to_be_visible()
    spans = page.locator(".et-marks").evaluate("""track => {
        const groups = new Map();
        for (const point of track.querySelectorAll('.et-point-combined-member')) {
            const x = point.getBoundingClientRect().left;
            // Inspect painted clusters in sorted order, using their source counts.
            groups.set(x, point);
        }
        const xs = [...groups.keys()].sort((a,b) => a-b);
        return {span: xs.at(-1) - xs[0], total: track.querySelectorAll('.et-mark-point').length};
    }""")
    assert spans["total"] == 21
    assert spans["span"] > 1


def test_readme_capture_shows_real_hovered_tooltip_and_segmented_circles(page, tmp_path):
    with _server(ROOT / "notebooks/50_graphics_gallery.py") as url:
        page.goto(url, wait_until="networkidle")
        root = page.locator('[data-cell-name="graphic_point_overlaps"] .et-root')
        root.locator(".et-point-composite").first.wait_for()
        path = _capture(page, "graphic_point_overlaps", tmp_path / "point-overlaps.png")
        assert path.stat().st_size > 10_000
        expect(root.locator(".et-tooltip")).to_be_visible()
        expect(root.locator(".et-tooltip-name")).to_have_text(["Before:", "After:"])
        expect(root.locator(".et-tooltip-value")).to_have_text(["51.234567", "51.234567"])
        bounds, tooltip = root.bounding_box(), root.locator(".et-tooltip").bounding_box()
        assert tooltip["x"] + tooltip["width"] <= bounds["x"] + bounds["width"]
        assert tooltip["y"] + tooltip["height"] <= bounds["y"] + bounds["height"]


def test_array_point_tooltips_sort_values_numerically_not_in_input_order(page, live_server):
    table = EvidentialTable(
        [{"samples": [25.3, 23.9, 24.7, 24.2]}],
        columns=[col.points("samples", color="#2563eb80", size=10, outline=False).scale(domain=(0, 60))],
        width=180,
        page_size=0,
        search=False,
    )
    mount(page, live_server, [("Sorted inspection", table, [])])
    page.locator(".et-mark-point").first.hover(force=True)
    values = page.locator(".et-tooltip-value").all_text_contents()
    assert len(values) == 4
    assert [float(value) for value in values] == [23.9, 24.2, 24.7, 25.3]


def test_segmented_point_outlines_at_scale_bounds_do_not_add_scrollbars(page, live_server):
    table = EvidentialTable(
        [{"a": 0, "b": 0}, {"a": 100, "b": 100}],
        columns=[
            col.point("a", color="blue", outline="navy", size=12)
            .point("b", color="red", outline="maroon", size=12)
            .scale(domain=(0, 100))
        ],
        width="100%",
        page_size=0,
        search=False,
    )
    mount(page, live_server, [("Boundary circles", table, [])])
    expect(page.locator(".et-point-composite")).to_have_count(2)
    geometry = page.locator(".et-scroller").evaluate("el => ({width:el.clientWidth, scroll:el.scrollWidth})")
    assert geometry["scroll"] <= geometry["width"]
