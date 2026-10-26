"""The documented layout calls render the intended tables in marimo."""

import pytest

from scripts.api_screenshots import LAYOUT_NOTEBOOK, LAYOUTS, _server, _wait_for_tables

pytestmark = pytest.mark.browser


def test_layout_notebook_renders_notes_shading_summaries_and_nested_headers(page):
    with _server(LAYOUT_NOTEBOOK) as url:
        page.goto(url, wait_until="networkidle")
        _wait_for_tables(page, LAYOUTS)

        def table(name):
            return page.locator(f'[data-cell-name="layout_{name}"] .et-root')

        assert table("titles").locator(".et-title").inner_text() == "Products by region"
        assert "Six products" in table("titles").inner_text()
        assert "Source: illustrative product sales" in table("titles").inner_text()
        assert "Includes the October launch order." in table("footnotes").inner_text()
        assert "Stock was limited" in table("footnotes").inner_text()
        assert table("footnotes").locator("tbody sup").count() == 2
        for name, pattern in (
            ("off", [False] * 6),
            ("one", [False, True, False, True, False, True]),
            ("three", [False, False, False, True, True, True]),
        ):
            assert (
                table(f"shading_{name}")
                .locator("tbody tr")
                .evaluate_all("els => els.map(el => el.classList.contains('et-row-shaded'))")
                == pattern
            )
        combined = table("combined_totals")
        assert combined.locator("tbody tr.et-row-section").count() == 2
        assert combined.locator("tbody tr.et-row-subtotal").count() == 2
        assert combined.locator("tbody tr.et-row-total").count() == 1
        assert "$10,500" in combined.locator("tbody tr.et-row-total").inner_text()
        assert table("summary_top").locator("tbody tr").first.evaluate("el => el.classList.contains('et-row-subtotal')")
        for name in ("headings", "heading_values", "summary_top", "summary_bottom", "combined_totals"):
            root = table(name)
            assert root.locator("tbody tr:not(.et-display-row) td:first-child").evaluate_all(
                "els => els.every(el => parseFloat(getComputedStyle(el).paddingLeft) > 10)"
            )
            assert root.locator("tbody tr.et-display-row td:first-child").evaluate_all(
                "els => els.every(el => parseFloat(getComputedStyle(el).paddingLeft) < 10)"
            )
        assert (
            table("headings_centered")
            .locator(".et-display-heading")
            .evaluate_all(
                "els => els.length === 2 && els.every(el => getComputedStyle(el).textAlign === 'center' && el.colSpan === 3)"
            )
        )
        assert table("headings_column").locator("tbody tr td:first-child").all_text_contents() == [
            "North",
            "",
            "",
            "South",
            "",
            "",
        ]
        assert (
            table("headings_column")
            .locator("tbody tr td:first-child")
            .evaluate_all("els => els.every(el => Number(getComputedStyle(el).fontWeight) >= 600)")
        )
        one = table("groups_one").locator("thead .et-header-groups")
        nested = table("groups_two").locator("thead .et-header-groups")
        assert one.count() == 1
        assert nested.count() == 2
        assert nested.nth(0).locator("th[colspan='4']").inner_text() == "Operations"
        assert nested.nth(1).locator("th[colspan='2']").all_text_contents() == ["Volume", "Money"]
