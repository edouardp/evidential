"""Functional tests for the renderer, driven through a real browser.

Run with ``make test-browser`` (or ``uv run pytest -m browser tests/browser``).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser


def open_preview(page, live_server, fragment=""):
    page.goto(f"{live_server}/frontend/preview.html{fragment}", wait_until="networkidle")
    page.wait_for_selector(".evidential-widget .et-table")


def cell_text(page, scope, row, column):
    return page.locator(f"{scope} tbody tr").nth(row).locator("td").nth(column).inner_text()


def test_renders_and_sorts(page, live_server):
    open_preview(page, live_server)
    assert page.locator("#raw tbody tr").count() == 6

    trips_header = page.locator("#raw .et-th", has_text="Trips")
    trips_header.click()  # desc
    assert "London" in cell_text(page, "#raw", 0, 1)
    trips_header.click()  # asc
    assert "Chicago" in cell_text(page, "#raw", 0, 1)
    trips_header.click()  # cleared, original order
    assert "New York" in cell_text(page, "#raw", 0, 1)


def test_keyboard_sort_and_group_toggle(page, live_server):
    open_preview(page, live_server)
    header = page.locator("#raw .et-th", has_text="Trips")
    header.focus()
    page.keyboard.press("Enter")
    assert "London" in cell_text(page, "#raw", 0, 1)
    assert header.evaluate("el => el === document.activeElement")
    page.keyboard.press("Space")
    assert "Chicago" in cell_text(page, "#raw", 0, 1)
    button = page.locator("#grouped button.et-chevron").first
    initial = page.locator("#grouped tbody tr").count()
    button.focus()
    page.keyboard.press("Enter")
    assert page.locator("#grouped tbody tr").count() < initial
    assert button.get_attribute("aria-expanded") == "false"
    assert button.evaluate("el => el === document.activeElement")
    page.keyboard.press("Space")
    assert page.locator("#grouped tbody tr").count() == initial


def test_keyboard_selection_retains_focus_through_synced_updates(page, live_server):
    open_preview(page, live_server)
    page.evaluate("""async () => {
        const {default: widget} = await import('/src/evidential/static/table.js');
        const el = document.createElement('div');
        el.id = 'keyboard-table';
        document.body.append(el);
        const data = {rows: [{x: 1}], columns: [{name: 'x'}], options: {select: 'x'}, selected: null};
        const listeners = new Map();
        widget.render({el, model: {
            get: key => data[key],
            set: (key, value) => { data[key] = value; listeners.get('change:' + key)?.(); },
            save_changes: () => { el.dataset.saves = String(Number(el.dataset.saves || 0) + 1); },
            on: (event, callback) => listeners.set(event, callback),
            off: event => listeners.delete(event),
        }});
    }""")
    row = page.locator("#keyboard-table tbody tr")
    row.focus()
    page.keyboard.press("Enter")
    page.wait_for_function("document.querySelector('#keyboard-table tbody tr') === document.activeElement")
    assert row.get_attribute("aria-selected") == "true"
    page.keyboard.press("Space")
    assert row.get_attribute("aria-selected") == "false"
    assert page.locator("#keyboard-table").get_attribute("data-saves") == "2"


def test_search_filters_rows(page, live_server):
    open_preview(page, live_server)
    search = page.locator("#raw .et-search")
    search.fill("London")
    page.wait_for_timeout(150)
    assert page.locator("#raw tbody tr").count() == 1
    assert "London" in page.locator("#raw tbody tr").first.inner_text()


def test_pagination(page, live_server):
    open_preview(page, live_server, "#pages")
    page.wait_for_selector("#paged tbody tr")
    assert page.locator("#paged tbody tr").count() == 8
    page.locator("#paged .et-page-controls button").nth(1).click()
    page.wait_for_timeout(150)
    assert page.locator("#paged tbody tr").count() == 8
    assert "2/" in page.locator("#paged .et-page-current").inner_text()


def test_actions_sit_below_the_table_with_no_pager_or_notes(page, live_server):
    # The #features table has page_size=0 and no caption/footnotes, so the actions
    # must not float — that would drop them onto the last row.
    open_preview(page, live_server, "#features")
    page.wait_for_selector("#features .et-table")
    page.hover("#features .et-root")
    page.wait_for_timeout(300)
    floats = page.locator("#features .et-root").evaluate("e => e.classList.contains('et-float-actions')")
    assert floats is False
    scroller = page.locator("#features .et-scroller").bounding_box()
    actions = page.locator("#features .et-table-actions").bounding_box()
    assert actions["y"] >= scroller["y"] + scroller["height"] - 1, "actions overlap the table"


def test_collapsing_a_group_lets_the_table_shrink_back(page, live_server):
    # Regression: the "never shrink" baseline held the expanded height after a
    # group was collapsed (most visible with a max_height).
    open_preview(page, live_server, "#grouped")
    page.wait_for_selector("#grouped .et-row-subtotal")
    scroller = page.locator("#grouped .et-scroller")
    expanded = scroller.bounding_box()["height"]
    page.locator("#grouped button.et-chevron").first.click()
    page.wait_for_timeout(250)
    collapsed = scroller.bounding_box()["height"]
    assert collapsed < expanded, f"table did not shrink back ({expanded} -> {collapsed})"


def test_fullscreen_round_trip(page, live_server):
    open_preview(page, live_server, "#pages")
    dialog = page.locator("#paged dialog.et-dialog")
    page.locator("#paged .et-expand-btn").click()
    page.wait_for_timeout(300)
    assert dialog.evaluate("d => d.open") is True
    assert dialog.locator(".et-root.et-expanded").count() == 1

    dialog.locator(".et-close-btn").click()
    page.wait_for_timeout(300)
    assert dialog.evaluate("d => d.open") is False
    assert page.locator("#paged .et-root .et-table").count() == 1


def test_sparklines_render(page, live_server):
    open_preview(page, live_server)
    assert page.locator("#raw svg.et-sparkline").count() >= 6


def test_bar_fills_row_without_growing_it(page, live_server):
    open_preview(page, live_server)
    bar_cell = page.locator("#raw .et-bar-cell").first
    # the bar cell must not grow the row: it matches the padded content height
    # of a normal cell in the same row (the td's own bounding box adds borders)
    data_client = page.locator("#raw tbody tr").first.locator("td").first.evaluate("el => el.clientHeight")
    assert bar_cell.bounding_box()["height"] == pytest.approx(data_client, abs=1)
    # the bar fills the row, leaving ~2px to the separators
    bar_box = bar_cell.locator(".et-bar").first.bounding_box()
    assert bar_box["height"] == pytest.approx(bar_cell.bounding_box()["height"] - 4, abs=1.5)


def test_accordion_indents_child_rows(page, live_server):
    open_preview(page, live_server)
    subtotal = page.locator("#grouped tbody tr.et-row-subtotal").first
    detail = page.locator("#grouped tbody tr.et-row:not(.et-row-subtotal):not(.et-row-total)").first

    def pad(cell):
        return cell.evaluate("el => parseFloat(getComputedStyle(el).paddingLeft)")

    # the parent (region) dimension is indented on detail rows...
    parent_pad = pad(detail.locator("td").first)
    # ...but the leaf dimension (city) and the subtotal label are not
    leaf_pad = pad(detail.locator("td").nth(1))
    subtotal_pad = pad(subtotal.locator("td").first)
    assert parent_pad >= leaf_pad + 24  # ~2rem indent
    assert leaf_pad <= 8  # base cell padding only
    assert subtotal_pad <= 8


def test_frozen_columns_have_an_opaque_backdrop(page, live_server):
    """Scrolled content must not show through frozen cells (shaded or not)."""
    open_preview(page, live_server)
    # Scroll horizontally so non-frozen cells slide underneath the frozen ones.
    page.eval_on_selector("#raw .et-scroller", "el => { el.scrollLeft = 300; }")
    page.wait_for_timeout(200)

    alphas = page.eval_on_selector_all(
        "#raw tbody .et-frozen",
        """cells => cells.map((cell) => {
            const value = getComputedStyle(cell).backgroundColor;
            const match = value.match(/rgba?\\(([^)]+)\\)/);
            if (!match) return 1;
            const parts = match[1].split(',').map((part) => parseFloat(part));
            return parts.length === 4 ? parts[3] : 1;
        })""",
    )
    assert alphas, "expected frozen cells in the preview table"
    assert min(alphas) == 1, f"a frozen cell is translucent: {alphas}"


def test_column_info_tooltip_is_on_the_header_cell(page, live_server):
    open_preview(page, live_server, "#features")
    headers = page.locator("#features th.et-th:has(.et-th-info)")
    assert headers.count() == 1
    header = headers.first
    # The native tooltip is on the whole cell, so it no longer lives on the icon.
    assert header.get_attribute("title") == "The city name"
    icon = header.locator(".et-th-info")
    assert icon.get_attribute("title") is None
    assert icon.evaluate("el => getComputedStyle(el).cursor") == "help"


def test_delta_indicator_follows_the_value(page, live_server):
    open_preview(page, live_server, "#features")
    text = page.locator("#features .et-delta").first.inner_text().strip()
    assert text[0].isdigit()  # value first...
    assert text.endswith("▲") or text.endswith("▼")  # ...indicator last


def test_delta_indicator_width_is_constant(page, live_server):
    open_preview(page, live_server)
    widths = page.eval_on_selector_all(
        "#raw .et-delta-indicator",
        "nodes => nodes.map((node) => Math.round(node.getBoundingClientRect().width * 100) / 100)",
    )
    assert widths, "expected delta indicators"
    assert len(set(widths)) == 1, f"indicator widths differ: {widths}"
    indicators = page.eval_on_selector_all("#raw .et-delta-indicator", "nodes => nodes.map((node) => node.textContent)")
    # the preview mixes increases, decreases and neutral values
    assert "▲" in indicators and "▼" in indicators and "–" in indicators, indicators


def test_header_styling(page, live_server):
    open_preview(page, live_server, "#hierarchy")
    page.wait_for_selector("#hier .et-th-group:not(.et-th-group-blank)")

    # column headers are bold
    weight = page.eval_on_selector("#hier .et-th:not(.et-th-group)", "el => getComputedStyle(el).fontWeight")
    assert int(weight) >= 600, weight

    # column groups are centred, with a bold rule inset 3px on each side
    group = page.eval_on_selector(
        "#hier .et-th-group:not(.et-th-group-blank)",
        """el => {
            const style = getComputedStyle(el);
            const rule = getComputedStyle(el, '::after');
            return {
                align: style.textAlign,
                borderRight: style.borderRightWidth,
                left: rule.left,
                right: rule.right,
                height: rule.height,
                width: rule.width,
            };
        }""",
    )
    assert group["align"] == "center", group
    assert group["borderRight"] == "0px", group  # no vertical bars between groups
    assert group["left"] == "3px", group
    assert group["right"] == "3px", group
    assert group["height"] == "2px", group
    assert group["width"] != "0px", group

    # an ungrouped column's blank spanner cell draws no rule
    blank = page.eval_on_selector("#hier .et-th-group-blank", "el => getComputedStyle(el, '::after').display")
    assert blank == "none", blank


def test_sparklines_fit_the_row(page, live_server):
    open_preview(page, live_server)
    data = page.eval_on_selector(
        "#raw tbody tr",
        """row => {
            const content = (td) => {
                const s = getComputedStyle(td);
                return td.clientHeight - parseFloat(s.paddingTop) - parseFloat(s.paddingBottom);
            };
            const cells = [...row.children];
            const spark = cells.find((td) => td.querySelector('.et-sparkline'));
            const plain = cells.find(
                (td) => !td.querySelector('.et-sparkline') && !td.classList.contains('et-frozen')
            );
            return {
                svg: spark.querySelector('svg.et-sparkline').getBoundingClientRect().height,
                spark: content(spark),
                plain: content(plain),
            };
        }""",
    )
    assert data["svg"] <= data["spark"] + 0.5, data  # the SVG fits the cell
    assert data["spark"] <= data["plain"] + 0.5, data  # the cell is not taller than its peers


def test_display_features(page, live_server):
    open_preview(page, live_server, "#features")
    page.wait_for_selector("#features tbody tr")

    # default_sort asc by trips -> Chicago first
    assert "Chicago" in cell_text(page, "#features", 0, 1)
    # row numbers (header + 3 rows)
    assert page.locator("#features .et-row-num").count() == 4
    # compact density + column info icon
    assert page.locator("#features .et-root.et-compact").count() == 1
    assert page.locator("#features .et-th-info").count() == 1
    # delta chip
    assert page.locator("#features .et-delta-chip").count() >= 1
    # row conditional colour on the New York row (last after asc sort)
    background = (
        page.locator("#features tbody tr")
        .nth(2)
        .locator("td")
        .first.evaluate("el => getComputedStyle(el).backgroundColor")
    )
    assert background == "rgb(254, 249, 195)"


def render_subcolumns(page, live_server):
    open_preview(page, live_server)
    page.evaluate("""async () => {
        const {default: widget} = await import('/src/evidential/static/table.js');
        const el = document.createElement('div');
        el.id = 'subcolumns';
        el.className = 'evidential-widget';
        document.body.append(el);
        const data = {
            rows: [
                {country: 'A', value: 2, period: 'Q3', status: 'Steady'},
                {country: 'B', value: 12.34, period: 'November', status: 'Expanding'},
            ],
            columns: [
                {name: 'country'},
                {name: 'value', type: 'number', fmt: 'num1', align: 'right', subcolumn_group: 'Latest', column_group: ['Economy', 'GDP']},
                {name: 'period', align: 'left', subcolumn_group: 'Latest', column_group: ['Economy', 'GDP']},
                {name: 'status', viz: 'chip', align: 'center', subcolumn_group: 'Latest', column_group: ['Economy', 'GDP']},
            ],
            options: {stretch: false, freeze_columns: 4, row_shading: true},
        };
        widget.render({el, model: {get: key => data[key], on: () => {}, off: () => {}}});
        el.scrollIntoView();
    }""")
    page.wait_for_function("document.querySelector('#subcolumns .et-th-subcolumns').classList.contains('et-frozen')")


def test_subcolumns_alignment_shared_header_and_keyboard_sort(page, live_server):
    render_subcolumns(page, live_server)
    header = page.locator("#subcolumns .et-th-subcolumns")
    assert header.get_attribute("colspan") == "3"
    assert header.inner_text() == "Latest"
    cells = page.locator("#subcolumns tbody tr").first.locator("td")
    assert [cells.nth(i).evaluate("el => getComputedStyle(el).textAlign") for i in (1, 2, 3)] == [
        "right",
        "left",
        "center",
    ]
    assert cells.nth(1).inner_text() == "2.0"
    assert cells.nth(3).locator(".et-chip").count() == 1
    measurements = page.locator("#subcolumns tbody tr").evaluate_all("""rows => rows.map(row => {
        const value = row.children[1];
        const text = value.querySelector('.et-cell-value') || value;
        const walker = document.createTreeWalker(text, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
            const dot = node.textContent.indexOf('.');
            if (dot < 0) continue;
            const range = document.createRange();
            range.setStart(node, dot);
            range.setEnd(node, dot + 1);
            return {decimal: range.getBoundingClientRect().x,
                gap: parseFloat(getComputedStyle(value).paddingRight) + parseFloat(getComputedStyle(row.children[2]).paddingLeft)};
        }
    })""")
    assert abs(measurements[0]["decimal"] - measurements[1]["decimal"]) < 0.5
    assert measurements[0]["gap"] < 6
    header.focus()
    page.keyboard.press("Enter")
    assert cell_text(page, "#subcolumns", 0, 0) == "B"
    assert header.evaluate("el => el === document.activeElement")


def test_subcolumns_frozen_edges_and_sticky_header_levels(page, live_server):
    render_subcolumns(page, live_server)
    geometry = page.locator("#subcolumns .et-table").evaluate("""table => {
        const cells = [...table.querySelector('tbody tr').children];
        const shared = table.querySelector('.et-th-subcolumns');
        const rows = [...table.querySelectorAll('thead tr')];
        return {
            lefts: cells.map(el => parseFloat(el.style.left)),
            widths: cells.map(el => el.getBoundingClientRect().width),
            sharedLeft: parseFloat(shared.style.left),
            tops: rows.map(row => parseFloat(row.children[0].style.top)),
            heights: rows.map(row => row.getBoundingClientRect().height),
        };
    }""")
    assert geometry["sharedLeft"] == pytest.approx(geometry["widths"][0], abs=0.5)
    assert geometry["lefts"][3] == pytest.approx(sum(geometry["widths"][:3]), abs=0.5)
    assert geometry["tops"][1] == pytest.approx(geometry["heights"][0], abs=0.5)
    assert geometry["tops"][2] == pytest.approx(sum(geometry["heights"][:2]), abs=0.5)


def test_economist_notebook_recreation_renders_transcribed_data(page, live_server, tmp_path):
    import runpy
    from pathlib import Path

    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "30_subcolumns.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["economist"].widget
    open_preview(page, live_server)
    page.evaluate(
        """async ({rows, columns, options, css}) => {
        const {default: widget} = await import('/src/evidential/static/table.js');
        document.body.innerHTML = css + '<div class="economist-recreation"><div id="economist" class="evidential-widget"></div></div>';
        const el = document.querySelector('#economist');
        const data = {rows, columns, options};
        widget.render({el, model: {get: key => data[key], on: () => {}, off: () => {}}});
    }""",
        {"rows": table.rows, "columns": table.columns, "options": table.options, "css": definitions["economist_css"]},
    )
    assert page.locator("#economist tbody tr").count() == 43
    assert page.locator("#economist .et-th-subcolumns").count() == 3
    assert cell_text(page, "#economist", 0, 1) == "2.9"
    assert cell_text(page, "#economist", 0, 2) == "Q3"
    assert (
        page.locator("#economist tbody tr").first.locator("td").nth(2).evaluate("el => getComputedStyle(el).color")
        == "rgb(128, 128, 128)"
    )
    assert cell_text(page, "#economist", 0, 3) == "4.9"
    assert cell_text(page, "#economist", 41, 2) == "2022"
    assert cell_text(page, "#economist", 33, 5) == "161"
    assert cell_text(page, "#economist", 5, 1) == "nil"
    assert page.locator("#economist .et-th-group").nth(1).locator("br").count() == 1
    assert (
        page.locator("#economist tbody tr")
        .nth(9)
        .locator("td")
        .nth(1)
        .evaluate("el => getComputedStyle(el).backgroundColor")
        == "rgb(255, 193, 174)"
    )
    assert (
        page.locator("#economist tbody tr")
        .first.locator("td")
        .first.evaluate("el => getComputedStyle(el).backgroundColor")
        == "rgb(213, 231, 239)"
    )
    screenshot = tmp_path / "economist-subcolumns.png"
    page.locator(".economist-recreation").screenshot(path=str(screenshot))
    print(f"Economist demo screenshot: {screenshot}")


def test_statistics_demo_cycles_small_centered_dots_without_moving_rows(page, live_server):
    import runpy
    from pathlib import Path

    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "25_column_stats.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    table = definitions["subcolumn_stats"].widget
    open_preview(page, live_server)
    page.evaluate(
        """async ({rows, columns, options}) => {
        const {default: widget} = await import('/src/evidential/static/table.js');
        const el = document.createElement('div');
        el.id = 'mixed-stats';
        el.className = 'evidential-widget';
        document.body.append(el);
        const data = {rows, columns, options};
        widget.render({el, model: {get: key => data[key], on: () => {}, off: () => {}}});
        el.scrollIntoView();
    }""",
        {"rows": table.rows, "columns": table.columns, "options": table.options},
    )
    cells = page.locator("#mixed-stats .et-stats-cell")
    assert cells.count() == 5
    assert [cells.nth(index).get_attribute("colspan") for index in range(5)] == ["1", "2", "3", "1", "1"]
    controls = page.locator("#mixed-stats .et-stats-cycle")
    assert [controls.nth(index).inner_text() for index in range(2)] == ["●○", "●○○"]
    assert page.locator("#mixed-stats .et-stats-footer").count() == 5
    for index in (0, 3, 4):
        assert cells.nth(index).locator(".et-stats-footer").inner_text() == ""
        assert cells.nth(index).locator("button").count() == 0
    geometry = controls.first.evaluate("""button => {
        const control = button.getBoundingClientRect();
        const footer = button.parentElement.getBoundingClientRect();
        return {center: control.x + control.width / 2, footerCenter: footer.x + footer.width / 2,
            fontSize: parseFloat(getComputedStyle(button).fontSize),
            statsFontSize: parseFloat(getComputedStyle(button.closest('td')).fontSize)};
    }""")
    assert geometry["center"] == pytest.approx(geometry["footerCenter"], abs=0.5)
    assert geometry["fontSize"] < geometry["statsFontSize"]
    initial_footers = page.locator("#mixed-stats .et-stats-footer").evaluate_all(
        "elements => elements.map(el => el.getBoundingClientRect().y)"
    )
    assert max(initial_footers) - min(initial_footers) < 0.5
    row = page.locator("#mixed-stats tbody tr").nth(1)
    initial_y = row.bounding_box()["y"]
    controls.nth(1).click()
    assert controls.nth(1).inner_text() == "○●○"
    assert "distinct: 3" in cells.nth(2).inner_text()
    assert row.bounding_box()["y"] == pytest.approx(initial_y, abs=0.5)
    controls.nth(1).press("Enter")
    assert controls.nth(1).inner_text() == "○○●"
    assert "distinct: 2" in cells.nth(2).inner_text()
    assert controls.nth(1).evaluate("el => el === document.activeElement")
    controls.nth(1).press("Space")
    assert controls.nth(1).inner_text() == "●○○"
    assert cells.nth(2).get_attribute("data-stats-column") == "fare"
    assert row.bounding_box()["y"] == pytest.approx(initial_y, abs=0.5)
    controls.first.click()
    page.locator("#mixed-stats .et-page-controls button").nth(1).click()
    assert controls.first.inner_text() == "○●"
    assert cells.nth(1).get_attribute("data-stats-column") == "trip_unit"
