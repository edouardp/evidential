"""Compact precision reaches ordinary cells, mark labels, axes and tooltips."""

import runpy
from pathlib import Path

import pytest
from test_spec_conformance import capture, mount

from evidential import EvidentialTable, col, label

pytestmark = pytest.mark.browser


def test_compact_precision_notebook_and_shared_formatting_surfaces(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks/08_column_options.py"
    _, definitions = runpy.run_path(str(notebook))["compact_formatting"].run()
    table = definitions["compact"].widget
    amounts = [1.14765e12, 877.1234e9]
    guides = EvidentialTable(
        [{"amount": value, "trend": amounts} for value in amounts],
        columns=[
            col.bar("amount", format="compact4", label=label.fmt("compact4").auto_position("outside end")).scale(
                domain=(1e9, amounts[0]), transform="log", axis=True
            ),
            col.sparkline("trend", markers=True, y_fmt="compact4", width=180),
        ],
        width=1100,
        column_stats=True,
        page_size=0,
        search=False,
    )
    mount(page, live_server, [("Compact notebook", table, []), ("Shared formatter", guides, [])])
    page.locator("section").evaluate_all("els => els.forEach(el => el.style.width = '1150px')")
    cells = page.locator("#case-0 tbody tr").first.locator("td")
    assert cells.nth(1).inner_text() == "1.1T"
    assert cells.nth(2).inner_text() == "1.148T"
    assert cells.nth(3).inner_text() == "1.14765T"
    assert cells.nth(4).locator(".et-mark-label-text").inner_text() == "1.148T"
    assert page.locator("#case-0 tbody tr").nth(1).locator("td").nth(2).inner_text() == "877.1B"
    assert page.locator("#case-0 tbody tr").nth(5).locator("td").nth(2).inner_text() == "0.0001235"
    assert page.locator("#case-0 tbody tr").last.locator("td").nth(2).inner_text() == "–"
    assert page.locator("#case-1 .et-mark-label-text").all_text_contents() == ["1.148T", "877.1B"]
    assert "1.012T" in page.locator("#case-1 .et-stats-value").all_text_contents()
    assert "1.148T" in page.locator("#case-1 .et-axis-tick").all_text_contents()
    assert page.locator("#case-1 .et-sparkline").first.locator("circle title").all_text_contents() == [
        "0: 1.148T",
        "1: 877.1B",
    ]
    capture(page, "compact-formatting.png")
