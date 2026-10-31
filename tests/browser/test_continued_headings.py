"""Continued headings use the ordinary renderer, changing only their label."""

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, rows, section_row

pytestmark = pytest.mark.browser


def heading_snapshot(heading):
    return heading.evaluate("""async row => {
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return [...row.cells].map(cell => {
        const style = getComputedStyle(cell);
        return {text: cell.textContent.replace(' (cont.)', ''), colspan: cell.colSpan,
          fontStyle: style.fontStyle, fontWeight: style.fontWeight, fontSize: style.fontSize,
          textAlign: style.textAlign, verticalAlign: style.verticalAlign,
          color: style.color, background: style.backgroundColor,
          borderTop: style.borderTop, borderBottom: style.borderBottom,
          padding: style.padding,
          expanded: cell.querySelector('button')?.getAttribute('aria-expanded') ?? null};
      });
    }""")


@pytest.mark.parametrize("variant", ["plain", "values", "centered"])
def test_display_continuations_preserve_every_heading_property_except_label(page, live_server, variant):
    data = [{"region": "North", "name": name, "value": value} for name, value in [("A", 10), ("B", 20), ("C", 30)]]
    layout = (
        rows.group_by("region")
        .section(
            align="center" if variant == "centered" else "left",
            values={"value": rows.aggregate("sum", format="usd0"), "name": rows.count(suffix=" products")}
            if variant == "values"
            else None,
            rule="both",
            style={"background": "#fef3c7", "color": "#334155"},
            collapsible=True,
        )
        .summary("Subtotal", values={"value": "sum"})
        .grand_summary("Grand total", values={"value": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Continued heading",
                data,
                [col.text("name"), col.integer("value")],
                {"row_layout": layout, "page_size": 1, "row_numbers": True, "row_shading": False, "freeze_columns": 2},
            )
        ],
    )
    heading = page.locator(".et-display-section")
    first = heading_snapshot(heading)
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(heading).to_contain_text("North (cont.)")
    assert heading_snapshot(heading) == first
    expect(page.locator(".et-display-summary")).to_have_count(0)
    expect(page.locator(".et-display-grand_summary")).to_have_count(0)
    page.get_by_role("button", name="Next page", exact=True).click()
    assert heading_snapshot(heading) == first
    expect(page.locator(".et-display-summary")).to_have_count(1)
    expect(page.locator(".et-display-grand_summary")).to_have_count(1)
    capture(page, f"continued-heading-{variant}.png")


@pytest.mark.parametrize("align", ["left", "center"])
def test_legacy_continuations_reuse_heading_alignment_and_rules(page, live_server, align):
    data = [section_row("North", align=align), *({"name": name, "value": i} for i, name in enumerate("ABC"))]
    mount(
        page,
        live_server,
        [
            (
                "Legacy continued heading",
                data,
                [col.text("name"), col.integer("value")],
                {"page_size": 2, "row_shading": False},
            )
        ],
    )
    heading = page.locator(".et-row-section")
    first = heading_snapshot(heading)
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(heading).to_contain_text("North (cont.)")
    assert heading_snapshot(heading) == first
