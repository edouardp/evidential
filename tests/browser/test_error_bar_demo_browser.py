"""Render the notebook's signed bars and supplied uncertainty intervals together."""

import runpy
from pathlib import Path

import marimo as mo
import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import EvidentialTable, col

pytestmark = pytest.mark.browser


def test_notebook_error_bars_share_the_signed_bar_scale(page, live_server):
    notebook = runpy.run_path(str(Path(__file__).resolve().parents[2] / "notebooks/37_encoding_marks.py"))
    _, values = notebook["error_bar_values"].run()
    _, result = notebook["error_bar_example"].run(EvidentialTable=EvidentialTable, col=col, mo=mo, **values)
    table = result["error_bar_table"]
    mount(page, live_server, [(table.options["title"], table, [])])
    page.locator("section").evaluate("el => el.style.width = '1050px'")
    expect(page.locator(".et-mark-bar")).to_have_count(len(table.rows))
    expect(page.locator(".et-mark-cap")).to_have_count(2 * len(table.rows))
    geometry = page.locator(".et-marks").evaluate_all("""tracks => tracks.map(track => {
        const bounds = track.getBoundingClientRect();
        const bar = track.querySelector('.et-mark-bar');
        const range = track.querySelector('.et-mark-range');
        const b = bar.getBoundingClientRect();
        const r = range.getBoundingClientRect();
        const start = range.querySelector('.et-mark-cap-start').getBoundingClientRect();
        const end = range.querySelector('.et-mark-cap-end').getBoundingClientRect();
        const marks = [...track.children];
        return {left: bounds.left, width: bounds.width,
            barLeft: b.left, barRight: b.right, rangeLeft: r.left, rangeRight: r.right,
            start: start.x + start.width / 2, end: end.x + end.width / 2,
            barCenter: b.y + b.height / 2, rangeCenter: r.y + r.height / 2,
            overlaid: marks.indexOf(range) > marks.indexOf(bar)};
    })""")
    lower, upper = table.columns[1]["scale"]["domain"]

    def project(value, marks):
        return marks["left"] + (value - lower) / (upper - lower) * marks["width"]

    for row, marks in zip(table.rows, geometry, strict=True):
        zero, estimate = project(0, marks), project(row["estimate"], marks)
        assert marks["barLeft"] == pytest.approx(min(zero, estimate), abs=1)
        assert marks["barRight"] == pytest.approx(max(zero, estimate), abs=1)
        assert marks["rangeLeft"] == pytest.approx(project(row["low"], marks), abs=1)
        assert marks["rangeRight"] == pytest.approx(project(row["high"], marks), abs=1)
        assert marks["start"] == pytest.approx(marks["rangeLeft"], abs=1)
        assert marks["end"] == pytest.approx(marks["rangeRight"], abs=1)
        assert marks["barCenter"] == pytest.approx(marks["rangeCenter"], abs=1)
        assert marks["overlaid"]
    capture(page, "error-bars-demo.png")
