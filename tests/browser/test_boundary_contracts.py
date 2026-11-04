"""Untrusted navigation and portable summaries cross the actual widget boundary."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import mount

from evidential import EvidentialTable, col, rows

pytestmark = pytest.mark.browser


def test_executable_navigation_never_creates_an_active_link(page, live_server):
    source = [{"name": "Untrusted record", "url": "javascript:window.boundaryProbe=1;void(0)"}]
    mount(
        page,
        live_server,
        [
            (
                "Navigation",
                source,
                [col.text("name").link("url")],
                {
                    "link": "url",
                    "info": "Details",
                    "info_link": source[0]["url"],
                    "title": "Safe navigation",
                },
            )
        ],
    )
    expect(page.locator("tbody a, .et-row-link, .et-info-link")).to_have_count(0)
    page.locator("tbody td").first.click()
    assert page.evaluate("window.boundaryProbe === undefined")


def test_date_summary_matches_python_and_recomputes_after_search(page, live_server):
    source = [
        {"group": "A", "name": "Earlier", "date": "2024-01-01"},
        {"group": "A", "name": "Later", "date": "2024-02-01"},
    ]
    table = EvidentialTable(
        source,
        search=True,
        columns=[col.text("name"), col.date("date")],
        row_layout=rows.group_by("group").section().summary(values={"date": "min"}),
    )
    mount(page, live_server, [("Date aggregation", table, [])])
    summary = page.locator(".et-display-summary .et-display-value")
    expect(summary).to_have_text("2024-01-01")
    page.get_by_role("searchbox").fill("Later")
    expect(summary).to_have_text("2024-02-01")
