"""Display-only section folding keeps summaries, navigation and data separate."""

import runpy
from pathlib import Path

import pytest
from playwright.sync_api import expect
from test_spec_conformance import capture, mount

from evidential import col, rows

pytestmark = pytest.mark.browser

DATA = [
    {"region": "North", "category": "Hardware", "name": "Lamp", "value": 10},
    {"region": "North", "category": "Hardware", "name": "Chair", "value": 20},
    {"region": "North", "category": "Software", "name": "Editor", "value": 30},
    {"region": "South", "category": "Hardware", "name": "Desk", "value": 40},
]


@pytest.mark.parametrize("position", ["top", "bottom"])
@pytest.mark.parametrize("indent", [True, False])
def test_summary_labels_follow_detail_indent_with_explicit_override(page, live_server, position, indent):
    layout = (
        rows.group_by("region", "category")
        .section(collapsible=True)
        .summary("Subtotal", values={"value": "sum"}, position=position, indent=indent)
        .grand_summary("Grand total", values={"value": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Summary indentation",
                DATA,
                [col.text("name"), col.integer("value")],
                {"row_layout": layout, "section_indent": 1, "row_numbers": True, "freeze_columns": 2},
            )
        ],
    )
    detail = page.locator("tbody tr:not(.et-display-row)").filter(has_text="Lamp").locator("td").nth(1)
    summaries = page.locator(".et-display-summary").filter(has_text="30")
    # Hardware's summary uses the same inset as its details. North's summary
    # closes one level out. The row-number spacer and numeric total stay flush.
    inner = summaries.first if position == "bottom" else summaries.last
    outer = page.locator(".et-display-summary").filter(has_text="60").first

    def padding(cell):
        return cell.evaluate("el => parseFloat(getComputedStyle(el).paddingLeft)")

    inset = padding(detail)
    step = page.evaluate("parseFloat(getComputedStyle(document.documentElement).fontSize)")
    toggle = page.locator(".et-section-toggle").first
    gutter = toggle.locator(".et-section-chevron").evaluate("el => el.getBoundingClientRect().width") + toggle.evaluate(
        "el => parseFloat(getComputedStyle(el).columnGap)"
    )
    grand = page.locator(".et-display-grand_summary td").nth(1)
    assert padding(inner.locator("td").nth(1)) == pytest.approx(inset - (0 if indent else step + gutter), abs=0.02)
    assert padding(outer.locator("td").nth(1)) == pytest.approx(
        inset - step - gutter if indent else padding(grand), abs=0.02
    )
    # Two nested toggles each contribute their full width and gap in addition
    # to the configured rem inset. This remains true in frozen columns.
    assert inset == pytest.approx(step * 2 + step / 4 + gutter * 2, abs=0.03)
    assert padding(inner.locator("td").last) == padding(detail.locator("..").locator("td").last)
    assert padding(grand) < padding(detail)
    capture(page, f"summary-indent-{position}-{indent}.png")


@pytest.mark.parametrize("position", ["top", "bottom"])
@pytest.mark.parametrize("promote", [False, True])
def test_sections_hide_their_summaries_and_optionally_promote_values(page, live_server, position, promote):
    layout = (
        rows.group_by("region")
        .section(collapsible=True, collapsed_summary=promote)
        .summary("Subtotal", values={"value": "sum"}, position=position)
        .grand_summary("Grand total", values={"value": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Fold sections",
                DATA,
                [col.text("name"), col.integer("value")],
                {"row_layout": layout, "download": True, "search": True},
            )
        ],
    )
    details = page.locator("tbody tr:not(.et-display-row)")
    north = page.get_by_role("button", name="Toggle section North", exact=True)
    expect(north).to_have_attribute("aria-expanded", "true")
    expect(details).to_have_count(4)
    north.focus()
    north.press("Enter")
    expect(north).to_have_attribute("aria-expanded", "false")
    expect(north).to_be_focused()
    expect(details).to_have_count(1)
    expect(page.locator(".et-display-summary")).to_have_count(1)
    expect(page.locator(".et-display-grand_summary")).to_contain_text("100")
    heading = page.locator(".et-display-section").first
    expect(heading.locator(".et-display-value")).to_have_count(1 if promote else 0)
    if promote:
        expect(heading).to_contain_text("60")
    with page.expect_download() as event:
        page.get_by_role("button", name="Download CSV").click()
    csv = Path(event.value.path()).read_text()
    assert all(name in csv for name in ("Lamp", "Chair", "Editor", "Desk"))
    assert "Subtotal" not in csv

    def search(query):
        # Let the previous render restore its input caret before fill selects
        # the next query. Otherwise that frame can interrupt Playwright's clear.
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        page.locator(".et-search").fill(query)
        expect(page.locator(".et-search")).to_have_value(query)

    search("Lamp")
    expect(details).to_have_count(0)
    expect(page.locator(".et-empty-body")).to_have_count(0)
    expect(page.locator(".et-display-summary")).to_have_count(0)
    expect(page.locator(".et-display-grand_summary")).to_contain_text("10")
    if promote:
        expect(page.locator(".et-display-section .et-display-value")).to_have_text("10")
    search("no matching item")
    expect(page.locator(".et-display-row")).to_have_count(0)
    expect(page.locator(".et-empty-body")).to_have_count(1)
    search("")
    expect(north).to_have_attribute("aria-expanded", "false")
    north.press("Space")
    expect(details).to_have_count(4)
    expect(page.locator(".et-display-summary")).to_have_count(2)
    expect(page.locator(".et-display-section").first.locator(".et-display-value")).to_have_count(0)
    capture(page, f"collapsible-sections-{position}-{promote}.png")


def test_nested_sections_preserve_child_state_and_all_closed_is_not_empty(page, live_server):
    layout = rows.group_by("region", "category").section().collapsible().summary(values={"value": "sum"})
    mount(
        page,
        live_server,
        [
            (
                "Nested folding",
                DATA,
                [col.text("name"), col.integer("value")],
                {"row_layout": layout, "page_size": 0, "freeze_columns": 1, "row_numbers": True},
            )
        ],
    )
    hardware = page.get_by_role("button", name="Toggle section Hardware", exact=True).first
    hardware.click()
    expect(page.locator("tbody tr:not(.et-display-row)")).to_have_count(2)
    page.get_by_role("button", name="Toggle section North", exact=True).click()
    expect(page.locator("tbody tr:not(.et-display-row)")).to_have_count(1)
    page.get_by_role("button", name="Toggle section North", exact=True).click()
    expect(hardware).to_have_attribute("aria-expanded", "false")
    expect(page.locator("tbody tr:not(.et-display-row)")).to_have_count(2)
    page.get_by_role("button", name="Toggle section North", exact=True).click()
    page.get_by_role("button", name="Toggle section South", exact=True).click()
    expect(page.locator("tbody tr")).to_have_count(2)
    expect(page.locator(".et-empty-body")).to_have_count(0)
    expect(page.locator(".et-page-info")).to_contain_text("2 items · 4 matching records")
    page.wait_for_timeout(100)
    expect(page.locator('thead [data-column-start="0"]')).to_have_class("et-th et-row-num et-frozen et-frozen-last")
    page.get_by_role("button", name="Toggle section North", exact=True).click()
    expect(page.locator("tbody tr:not(.et-display-row)")).to_have_count(1)


def test_continuation_heading_can_fold_and_unfold_without_losing_navigation(page, live_server):
    layout = rows.group_by("region").section(collapsible=True).summary(values={"value": "sum"}).grand_summary()
    mount(
        page,
        live_server,
        [("Paged folding", DATA, [col.text("name"), col.integer("value")], {"row_layout": layout, "page_size": 1})],
    )
    page.get_by_role("button", name="Next page", exact=True).click()
    continued = page.get_by_role("button", name="Toggle section North (cont.)", exact=True)
    continued.click()
    north = page.get_by_role("button", name="Toggle section North", exact=True)
    expect(north).to_have_attribute("aria-expanded", "false")
    expect(north).to_be_focused()
    expect(page.locator(".et-page-current")).to_have_text("1/2")
    page.get_by_role("button", name="Next page", exact=True).click()
    expect(page.locator("tbody tr:not(.et-display-row)")).to_contain_text("Desk")
    expect(page.locator(".et-display-grand_summary")).to_contain_text("100")
    page.get_by_role("button", name="Previous page", exact=True).click()
    north.click()
    expect(page.locator(".et-page-current")).to_have_text("1/4")
    expect(page.locator("tbody tr:not(.et-display-row)")).to_contain_text("Lamp")


def test_centered_sections_and_fullscreen_fit_when_folded(page, live_server):
    data = [{"region": f"Group {i // 3}", "name": f"Item {i}", "value": i} for i in range(60)]
    layout = rows.group_by("region").section(align="center", collapsible=True).summary(values={"value": "sum"})
    mount(
        page,
        live_server,
        [("Centered folding", data, [col.text("name"), col.bar("value")], {"row_layout": layout, "page_size": 5})],
    )
    page.get_by_role("button", name="Expand table", exact=True).click()
    dialog = page.get_by_role("dialog", name="Expanded data table")
    button = dialog.get_by_role("button", name="Toggle section Group 0", exact=True)
    button.click()
    expect(button).to_have_attribute("aria-expanded", "false")
    heading = dialog.locator(".et-display-heading").first
    assert heading.evaluate("el => getComputedStyle(el).textAlign") == "center"
    assert heading.get_attribute("colspan") == "2"
    page.wait_for_timeout(200)
    assert dialog.locator(".et-scroller").evaluate("el => el.scrollHeight <= el.clientHeight")
    assert dialog.locator(".et-root").evaluate("el => el.scrollHeight <= el.clientHeight")
    dialog.get_by_role("button", name="Next page", exact=True).click()
    page.wait_for_timeout(100)
    assert dialog.locator(".et-scroller").evaluate("el => el.scrollHeight <= el.clientHeight")


def test_synthetic_rows_notebook_has_working_collapsible_demos(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "39_synthetic_rows.py"
    outputs, _ = runpy.run_path(str(notebook))["app"].run()
    tables = [output.widget for output in outputs if hasattr(output, "widget")]
    folding = [table for table in tables if table.row_layout["groups"][0]["section"]["collapsible"]]
    assert len(folding) == 3
    mount(page, live_server, [(table.options["title"], table, []) for table in folding])
    for index in range(3):
        section = page.locator(f"#case-{index}")
        button = section.locator(".et-section-toggle").first
        button.click()
        expect(button).to_have_attribute("aria-expanded", "false")
    capture(page, "synthetic-row-folding-demos.png")
