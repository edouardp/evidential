"""Exercise the declarative API's geometry through the shipped browser bundle."""

from __future__ import annotations

import os
import runpy
from base64 import b64encode
from math import log10
from pathlib import Path

import pytest

from evidential import EvidentialTable, col, domain, grouped_records, label
from evidential import rows as row_builder

pytestmark = pytest.mark.browser


def mount(page, live_server, cases):
    page.goto(f"{live_server}/frontend/preview.html", wait_until="networkidle")
    payload = []
    for case in cases:
        title, rows, columns, *overrides = case
        options = {
            "search": False,
            "page_size": 0,
            "stretch": True,
            "width": 520,
            "row_shading": True,
            "row_lines": False,
            "border": False,
            "font_size": "14px",
            "theme": {"border": "#555555", "header_border": "#555555"},
        }
        options.update(overrides[0] if overrides else {})
        table = rows if isinstance(rows, EvidentialTable) else EvidentialTable(rows, columns=columns, **options)
        payload.append(
            {
                "title": title,
                "rows": table.rows,
                "columns": table.columns,
                "options": table.options,
                "row_layout": table.row_layout,
            }
        )
    page.evaluate(
        """async cases => {
        const {default: widget} = await import('/src/evidential/static/table.js');
        document.body.replaceChildren();
        document.body.style.cssText = 'margin:24px;background:white;color:#222;font-family:Arial';
        for (const [index, data] of cases.entries()) {
            const section = document.createElement('section');
            section.style.cssText = 'width:520px;display:inline-block;vertical-align:top;margin:0 32px 32px 0';
            const heading = document.createElement('h3');
            heading.textContent = data.title;
            const el = document.createElement('div');
            el.id = 'case-' + index;
            el.className = 'evidential-widget';
            section.append(heading, el);
            document.body.append(section);
            widget.render({el, model: {get: key => data[key], on() {}, off() {}}});
        }
    }""",
        payload,
    )
    page.evaluate("window.scrollTo(0, 0)")


def capture(page, name):
    if path := os.environ.get("EVIDENTIAL_REVIEW_SCREENSHOT"):
        page.screenshot(path=str(Path(path).with_name(name)), full_page=True)


def test_chart_columns_receive_space_after_content_columns(page, live_server):
    data = [
        {"question": "Ease of use", "count": 1234, "down": 13, "neutral": 12, "up": 75},
        {"question": "Value for money", "count": 27, "down": 29, "neutral": 20, "up": 51},
    ]
    stack = col.stacked_bar(
        "down", "neutral", "up", title="Response", labels="percent", diverge_at="neutral", normalize="percent"
    )
    mount(
        page,
        live_server,
        [
            ("Diverging stack", data, [col.text("question"), stack], {"width": "100%"}),
            ("Mixed measures", data, [col.text("question"), col.integer("count"), col.bar("up", label=True)]),
            ("Two charts", data, [col.text("question"), col.bar("down"), col.bar("up")]),
            ("Intrinsic stack", data, [col.text("question"), stack], {"stretch": False}),
        ],
    )
    widths = page.locator("tbody tr:first-child").evaluate_all(
        "rows => rows.map(row => [...row.cells].map(cell => cell.getBoundingClientRect().width))"
    )
    assert widths[0][1] > widths[0][0] * 2
    assert widths[1][0] < 160
    assert widths[1][1] < 90
    assert widths[1][2] > sum(widths[1][:2])
    assert abs(widths[2][1] - widths[2][2]) < 2
    assert widths[2][1] > widths[2][0]
    assert widths[3][1] >= 280
    assert widths[3][1] > widths[3][0]
    page.locator("section").first.evaluate("el => el.style.width = '900px'")
    expanded = page.locator("#case-0 tbody tr").first.evaluate(
        "row => [...row.cells].map(cell => cell.getBoundingClientRect().width)"
    )
    assert abs(expanded[0] - widths[0][0]) < 2
    assert expanded[1] > widths[0][1] + 350
    capture(page, "column-sizing.png")


def test_stacked_bar_notebook_allocates_width_to_response_charts(page, live_server):
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "42_stacked_bars.py"
    outputs, _ = runpy.run_path(str(notebook))["app"].run()
    tables = [output.widget for output in outputs if hasattr(output, "widget")]
    assert len(tables) == 3
    mount(page, live_server, [(table.options["title"], table, []) for table in tables])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '600px')")
    for index in range(3):
        widths = page.locator(f"#case-{index} tbody tr").first.evaluate(
            "row => [...row.cells].map(cell => cell.getBoundingClientRect().width)"
        )
        assert widths[1] > widths[0] * 2
    assert page.locator("#case-2 .et-marks").first.bounding_box()["width"] > 400
    capture(page, "stacked-bars-column-sizing.png")


def test_wdi_ranking_does_not_scroll_for_omitted_outside_labels(page, live_server):
    import duckdb

    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "23_wdi.py"
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE country AS SELECT * FROM (VALUES
                ('JPN', 'Japan', 'East Asia & Pacific', 'High income'),
                ('GBR', 'United Kingdom', 'Europe & Central Asia', 'High income'),
                ('USA', 'United States', 'North America', 'High income')
            ) AS t("Country Code", "Short Name", Region, "Income Group");
            CREATE TABLE observations AS SELECT * FROM (VALUES
                ('JPN', 'SP.DYN.LE00.IN', 2023, 84.04),
                ('GBR', 'SP.DYN.LE00.IN', 2023, 81.30),
                ('USA', 'SP.DYN.LE00.IN', 2023, 78.40)
            ) AS t(country_code, indicator_code, year, value)
        """)
        _, definitions = runpy.run_path(str(notebook))["live_ranking"].run(connection=connection)
        ranking = definitions["ranking"]
        ranking.set_controls(indicator="SP.DYN.LE00.IN", year=2023, region="All regions")
        mount(page, live_server, [("WDI live ranking", ranking, [])])
        first_label = page.locator(".et-mark-label").first
        for width in (900, 1400, 1000):
            page.set_viewport_size({"width": width + 80, "height": 900})
            page.locator("section").evaluate("(el, width) => el.style.width = width + 'px'", width)
            # Fixed outside labels on the maximum bar cannot fit at any width.
            page.wait_for_function("getComputedStyle(document.querySelector('.et-mark-label')).visibility === 'hidden'")
            geometry = page.locator(".et-scroller").evaluate("""el => ({
                available: el.clientWidth, scroll: el.scrollWidth,
                table: el.querySelector('table').getBoundingClientRect().width,
            })""")
            assert geometry["table"] <= geometry["available"] + 1, geometry
            assert geometry["scroll"] <= geometry["available"] + 1, geometry
            assert first_label.get_attribute("title")
        capture(page, "wdi-ranking-no-scrollbar.png")


def test_automatic_bar_label_preferences_signed_bars_and_resize(page, live_server):
    positions = ["outside_end", "inside_end", "outside_start", "inside_start"]
    data = [{"x": value} for value in (95, 60, 3, 0, None)]
    cases = [
        (
            position,
            data,
            [
                col.bar("x", color="#111111", format="usd0")
                .label(True, position=position, auto=True, prefix="Revenue: ")
                .scale(domain=(0, 100))
            ],
            {"width": "100%"},
        )
        for position in positions
    ]
    cases.extend(
        [
            (
                "Signed",
                [{"x": value} for value in (-95, -60, -3, 0, 3, 60, 95)],
                [
                    col.bar("x", color="#111111", format="usd0")
                    .label(True, position="outside_end", auto=True)
                    .scale(domain=(-100, 100))
                ],
                {"width": "100%"},
            ),
            (
                "Mirrored",
                data,
                [
                    col.bar("x", direction="left", color="#111111", format="usd0")
                    .label(True, position="outside_end", auto=True)
                    .scale(domain=(0, 100))
                ],
                {"width": "100%"},
            ),
        ]
    )
    mount(page, live_server, cases)
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '240px')")
    page.wait_for_function("document.querySelector('#case-0 .et-mark-label').dataset.labelPosition === 'inside_end'")
    for index, preferred in enumerate(positions):
        labels = page.locator(f"#case-{index} .et-mark-label")
        assert labels.count() == 4
        assert labels.first.get_attribute("data-label-position") == preferred.replace("outside", "inside")
        if preferred.endswith("end"):
            assert labels.nth(1).get_attribute("data-label-position") == preferred
            assert labels.nth(2).get_attribute("data-label-position") == "outside_end"
            assert labels.nth(3).get_attribute("data-label-position") == "outside_end"
        else:
            assert labels.nth(2).get_attribute("hidden") is not None
            assert labels.nth(3).get_attribute("hidden") is not None
    signed = page.locator("#case-4 .et-mark-label")
    assert signed.first.get_attribute("data-label-position") == "inside_end"
    assert "et-mark-label-align-begin" in signed.first.get_attribute("class")
    assert "et-mark-label-align-end" in signed.last.get_attribute("class")
    assert page.locator("#case-5 .et-mark-label").first.get_attribute("data-label-position") == "inside_end"
    assert signed.first.evaluate("el => getComputedStyle(el).color") == "rgb(255, 255, 255)"
    capture(page, "automatic-bar-labels.png")
    # Bypass the chart minimum to test a track too narrow for either position.
    page.locator("#case-0 .et-marks").evaluate_all("nodes => nodes.forEach(el => el.style.minWidth = '0')")
    page.locator("section").first.evaluate("el => el.style.width = '24px'")
    first = page.locator("#case-0 .et-mark-label").first
    page.wait_for_function("document.querySelector('#case-0 .et-mark-label').hidden")
    assert first.get_attribute("title") == "Revenue: $95"
    assert first.evaluate("el => getComputedStyle(el).display") == "none"
    page.locator("#case-0 .et-marks").evaluate_all("nodes => nodes.forEach(el => el.style.minWidth = '')")
    page.locator("section").first.evaluate("el => el.style.width = '2000px'")
    page.wait_for_function("document.querySelector('#case-0 .et-mark-label').dataset.labelPosition === 'outside_end'")
    assert first.get_attribute("hidden") is None
    assert first.evaluate("el => getComputedStyle(el).color") != "rgb(255, 255, 255)"


def test_fluent_label_typography_and_placement_in_the_browser(page, live_server):
    annotation = label.fmt("num0").bold().auto_position("inside end").colour("black")
    typography = label.font("monospace").italic().figure_style("proportional").colour("purple")
    mount(
        page,
        live_server,
        [
            (
                "Fluent labels",
                [{"x": 95, "y": 50}, {"x": 3, "y": 20}],
                [
                    col.bar("x", title="Automatic", color="#a5d9e0", label=annotation).scale(domain=(0, 100)),
                    col.point("y", title="Point", label=typography.position("above").bold()).scale(domain=(0, 100)),
                    col.stacked_bar("x", "y", title="Stack", labels=typography.bold(), colors=["#a5d9e0", "#d4c4e4"]),
                ],
                {"width": "100%"},
            )
        ],
    )
    labels = page.locator("#case-0 td:first-child .et-mark-label")
    assert labels.first.inner_text() == "95"
    assert labels.first.get_attribute("data-label-position") == "inside_end"
    assert labels.nth(1).get_attribute("data-label-position") == "outside_end"
    for node in page.locator("#case-0 [data-mark-label]").all():
        assert node.evaluate("el => getComputedStyle(el).fontWeight") == "600"
    for selector in ("td:nth-child(2) .et-mark-label", "td:nth-child(3) .et-mark-stack-label"):
        node = page.locator(f"#case-0 {selector}").first
        assert node.is_visible()
        assert node.evaluate("el => getComputedStyle(el).fontFamily") == "monospace"
        assert node.evaluate("el => getComputedStyle(el).fontStyle") == "italic"
        assert node.evaluate("el => getComputedStyle(el).fontVariantNumeric") == "lining-nums proportional-nums"
        assert node.evaluate("el => getComputedStyle(el).color") == "rgb(128, 0, 128)"
    capture(page, "fluent-labels.png")


def test_shared_domains_match_bar_geometry_color_axes_and_pagination(page, live_server):
    payments = domain.numeric("payments").include_zero().palette("Blues")
    columns = [
        col.text("name"),
        col.bar("a", title="Card").domain(payments).scale(axis=True),
        col.bar("b", title="Cash").domain("payments").scale(axis=True),
        col.number("c").color().domain(payments),
        col.number("d").color().domain("payments"),
    ]
    mount(
        page,
        live_server,
        [
            (
                "Shared payments",
                [
                    {"name": "North", "a": 20, "b": 20, "c": 20, "d": 20},
                    {"name": "South", "a": 100, "b": 50, "c": 150, "d": 200},
                ],
                columns,
                {"page_size": 1, "search": True},
            )
        ],
    )
    bars = page.locator(".et-mark-bar")
    assert bars.count() == 2
    assert bars.first.evaluate("el => el.style.width") == "10%"
    assert bars.last.evaluate("el => el.style.width") == "10%"
    assert page.locator(".et-axis").first.inner_text() == page.locator(".et-axis").last.inner_text()
    colors = page.locator("tbody tr td:nth-last-child(-n+2)")
    assert colors.nth(0).evaluate("el => getComputedStyle(el).backgroundColor") == colors.nth(1).evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    page.get_by_role("button", name="Next page", exact=True).click()
    assert bars.first.evaluate("el => el.style.width") == "50%"
    page.get_by_role("searchbox").fill("North")
    assert bars.first.evaluate("el => el.style.width") == "100%"


def test_shared_domain_demo_renders_cross_encoding_colors(page, live_server):
    path = Path(__file__).resolve().parents[2] / "notebooks/47_shared_domains.py"
    _, definitions = runpy.run_path(str(path))["app"].run()
    mount(
        page,
        live_server,
        [
            ("Shared counts", definitions["counts"].widget, []),
            ("Shared change", definitions["change_table"].widget, []),
        ],
    )
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '950px')")
    heat = page.locator("#case-1 tbody tr").first.locator("td:nth-child(3)")
    rect = page.locator("#case-1 .et-sparkline-change rect").nth(3)
    assert heat.evaluate("el => getComputedStyle(el).backgroundColor") == rect.evaluate(
        "el => getComputedStyle(el).fill"
    )
    capture(page, "shared-domains.png")


def test_change_sparklines_geometry_color_anchors_and_pagination(page, live_server):
    data = [{"name": "A", "changes": [-1, 0, 1, None]}, {"name": "B", "changes": [-4, 0, 1, 8]}]
    mount(
        page,
        live_server,
        [
            (
                "Change states and shared gradient",
                data,
                [
                    col.text("name"),
                    col.sparkline("changes", title="State", type="change", width=100),
                    col.sparkline(
                        "changes",
                        title="Gradient",
                        type="change",
                        width=100,
                        color_scale=["#ff0000", "#808080", "#0000ff"],
                    ),
                ],
                {"page_size": 1},
            )
        ],
    )
    state = page.locator("td:nth-child(2) .et-sparkline-change rect")
    gradient = page.locator("td:nth-child(3) .et-sparkline-change rect")
    assert state.count() == gradient.count() == 3
    assert [node.get_attribute("data-state") for node in state.all()] == ["down", "steady", "up"]
    geometry = state.evaluate_all(
        "nodes => nodes.map(el => ({y: +el.getAttribute('y'), h: +el.getAttribute('height'), x: +el.getAttribute('x'), w: +el.getAttribute('width')}))"
    )
    assert geometry[0]["h"] == geometry[1]["h"] == geometry[2]["h"]
    assert geometry[0]["y"] - geometry[1]["y"] == geometry[1]["y"] - geometry[2]["y"] == geometry[0]["h"] / 2
    assert gradient.nth(1).get_attribute("fill") == "#808080"
    one_color = gradient.nth(2).get_attribute("fill")
    assert one_color != "#0000ff"  # The unseen next page contains +8.
    assert gradient.nth(2).locator("title").text_content().endswith("(up)")
    assert page.locator(".et-sparkline-change").first.get_attribute("aria-label").endswith("1 missing")
    scroller = page.locator(".et-scroller")
    assert scroller.evaluate("el => el.scrollHeight <= el.clientHeight")
    page.get_by_role("button", name="Next page", exact=True).click()
    assert gradient.count() == 4
    assert gradient.nth(2).get_attribute("fill") == one_color
    assert gradient.last.get_attribute("fill") == "#0000ff"
    assert gradient.first.get_attribute("fill") == "#ff0000"


def test_change_sparkline_football_demo_renders_aggregate_and_match_details(page, live_server, monkeypatch, tmp_path):
    monkeypatch.setenv("FOOTBALL_PARQUET", str(tmp_path / "missing.parquet"))
    path = Path(__file__).resolve().parents[2] / "notebooks" / "46_change_sparklines.py"
    _, definitions = runpy.run_path(str(path))["app"].run(defs={"selected_team": "Arsenal FC (England)"})
    tables = [definitions["teams"].widget, definitions["match_details"].widget]
    mount(page, live_server, [("Teams", tables[0], []), ("Match details", tables[1], [])])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '1000px')")
    assert page.locator("#case-0 .et-sparkline-change").count() == 12
    assert page.locator("#case-1 .et-sparkline-change").count() == 0
    assert page.locator("#case-1 tbody tr").count() == 15
    assert page.locator("#case-1").get_by_role("columnheader", name="Competition", exact=True).is_visible()
    assert page.locator("#case-0 rect[data-state=steady]").count() > 5
    for svg in page.locator(".et-sparkline-change").all():
        assert svg.is_visible()
        assert svg.evaluate("el => el.getBoundingClientRect().height") < 25
    capture(page, "change-sparklines.png")


@pytest.mark.parametrize(
    ("notebook", "definition"),
    [
        ("09_pivots.py", "by_channel"),
        ("11_comparisons.py", "qoq"),
        ("35_negatives.py", "change_table"),
        ("43_cell_presentations.py", "presentations"),
    ],
)
def test_migrated_scalar_bar_demos_render_marks_and_value_labels(page, live_server, notebook, definition):
    path = Path(__file__).resolve().parents[2] / "notebooks" / notebook
    _, definitions = runpy.run_path(str(path))["app"].run()
    table = definitions[definition].widget
    mount(page, live_server, [(definition, table, [])])
    assert page.locator(".et-mark-bar").count() > 0
    assert page.locator(".et-mark-label").count() > 0
    assert page.locator(".et-bar-wrap").count() == 0
    for column in table.columns:
        for encoding in column.get("encodings", []):
            if encoding["kind"] == "bar":
                assert encoding.get("label")
                assert any(row.get(encoding["source"]) is not None for row in table.rows)
    capture(page, f"bar-migration-{notebook.removesuffix('.py')}.png")


def test_consistent_api_formats_colors_and_mark_annotations(page, live_server):
    from evidential.rules import cells_body, tab_format

    cases = [
        (
            "Cell formatting",
            EvidentialTable(
                [{"x": 1.25}, {"x": -1}, {"x": None}],
                columns=[
                    col.point("x", format="num0", label={"value": True, "overflow": "show"})
                    .null_text("missing")
                    .neg(bracket=True)
                    .scale(domain=(-5, 5))
                ],
                rules=[tab_format(cells_body("x"), format="usd2")],
            ),
            [],
        ),
        (
            "Mirrored bar and axis",
            [{"x": 15, "ink": "#112233"}],
            [
                col.bar(
                    "x",
                    height=0.6,
                    direction="left",
                    fit_to_data=True,
                    reference=12,
                    reference_label="target",
                    color="@ink",
                    label=True,
                ).scale(domain=(10, 20), axis=True)
            ],
        ),
        (
            "Observation labels",
            [{"samples": [2, 4]}],
            [
                col.points(
                    "samples", format="num1", label={"value": True, "position": "above", "overflow": "show"}
                ).scale(domain=(0, 6))
            ],
        ),
        (
            "Summary annotation",
            [{"lo": 0, "q1": 1, "median": 2, "q3": 3, "hi": 4, "ink": "#112233"}],
            [
                col.boxplot("lo", "q1", "median", "q3", "hi", color="@ink", format="num1")
                .label(True, position="above", overflow="show")
                .scale(domain=(0, 4))
            ],
        ),
        (
            "Band annotation",
            [
                {
                    "curve": [
                        {"position": 0, "density": 0},
                        {"position": 2, "density": 1},
                        {"position": 4, "density": 0},
                    ],
                    "caption": "Estimate",
                }
            ],
            [col.distribution("curve").label(source="@caption", position="above", overflow="show")],
        ),
    ]
    mount(page, live_server, cases)
    assert page.locator("#case-0 tbody td").all_text_contents() == ["$1.25", "($1.00)", "missing"]
    bar = page.locator("#case-1 .et-mark-bar")
    assert bar.evaluate("el => el.style.left") == "50%"
    assert bar.evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(17, 34, 51)"
    ticks = page.locator("#case-1 .et-axis-tick")
    assert ticks.first.evaluate("el => parseFloat(el.style.left)") > ticks.last.evaluate(
        "el => parseFloat(el.style.left)"
    )
    assert page.locator("#case-1 .et-mark-reference-label").inner_text() == "target"
    assert page.locator("#case-2 .et-mark-label").all_text_contents() == ["2.0", "4.0"]
    assert page.locator("#case-3 .et-mark-label").inner_text() == "2.0"
    assert page.locator("#case-4 .et-mark-label").inner_text() == "Estimate"
    capture(page, "api-consistency-render.png")


def test_centered_bar_notebook_renders_mark_labels_and_mirrored_bars(page, live_server):
    page.set_viewport_size({"width": 1600, "height": 1000})
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "34_centered_bars.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    names = ("league_table", "variants", "back_to_back", "diverging")
    mount(page, live_server, [(name, definitions[name].widget, []) for name in names])
    page.locator("section").evaluate_all("nodes => nodes.forEach(el => el.style.width = '1500px')")
    page.wait_for_timeout(100)
    capture(page, "centered-bars-marks.png")
    for index in range(len(names)):
        case = page.locator(f"#case-{index}")
        assert case.locator(".et-bar-wrap").count() == 0
        assert case.locator(".et-mark-bar").count() > 0
        while True:
            labels = case.locator(".et-mark-label")
            assert case.locator("tbody tr").count() > 0
            if not labels.count():
                assert case.locator(".et-mark-bar").count() == 0
            hidden = labels.evaluate_all("""nodes => nodes
                .filter(el => getComputedStyle(el).visibility === 'hidden')
                .map(el => ({text: el.textContent, width: el.closest('td').getBoundingClientRect().width}))""")
            assert not hidden, hidden
            next_page = case.get_by_role("button", name="Next page")
            if not next_page.count() or next_page.is_disabled():
                break
            next_page.click()
        previous_page = case.get_by_role("button", name="Previous page")
        while previous_page.count() and previous_page.is_enabled():
            previous_page.click()
    assert "(1)" in page.locator("#case-0 tbody tr").first.locator("td").first.inner_text()
    for index, column in ((2, 0), (3, 1)):
        first_cell = page.locator(f"#case-{index} tbody tr").first.locator("td").nth(column)
        bar = first_cell.locator(".et-mark-bar")
        label = first_cell.locator(".et-mark-label")
        assert bar.evaluate("el => parseFloat(el.style.left) > 0")
        assert label.get_attribute("class").find("et-mark-label-left") >= 0
        assert "-" not in label.inner_text()
    assert (
        page.locator("#case-0 .et-table").bounding_box()["width"]
        < page.locator("section").first.bounding_box()["width"]
    )
    for index in (0, 1):
        labels = page.locator(f"#case-{index} .et-mark-label-outside_start")
        assert labels.count() > 0
        for label in labels.all():
            geometry = label.evaluate("""el => {
                const rect = el.getBoundingClientRect();
                const track = el.closest('.et-marks').getBoundingClientRect();
                return {left: rect.left, right: rect.right, zero: track.x + track.width / 2,
                        negative: el.textContent.startsWith('-')};
            }""")
            if geometry["negative"]:
                assert geometry["left"] > geometry["zero"]
            else:
                assert geometry["right"] < geometry["zero"]
    capture(page, "centered-bars-marks.png")


def test_uncertainty_band_paints_density_as_intensity_and_stays_in_its_row(page, live_server):
    data = [
        {
            "name": "Symmetric",
            "median": 50,
            "curve": [{"x": x, "pdf": y} for x, y in [(0, 0), (25, 0.5), (50, 1), (75, 0.5), (100, 0)]],
            "ink": "#4169a0",
        },
        {
            "name": "Gapped",
            "median": 70,
            "curve": [{"x": 0, "pdf": 0}, {"x": 20, "pdf": 1}, None, {"x": 60, "pdf": 1}, {"x": 100, "pdf": 0}],
            "ink": "#ad3038",
        },
        {"name": "Missing band", "median": 30, "curve": None, "ink": "#4169a0"},
    ]
    band = col.distribution("curve", x="x", y="pdf", color="@ink").point("median", color="#111111", outline=False)
    mount(
        page,
        live_server,
        [
            (
                "Uncertainty bands",
                data,
                [col.text("name"), band.scale(domain=(0, 100), axis=True)],
                {"row_shading": False},
            ),
            (
                "Compact — same band",
                data[:2],
                [col.text("name"), band.scale(domain=(0, 100))],
                {"width": 210, "row_shading": False, "font_size": "11px"},
            ),
        ],
    )
    if path := os.environ.get("EVIDENTIAL_REVIEW_SCREENSHOT"):
        page.locator("#case-0").screenshot(path=str(Path(path).with_name("evidential-distribution-bands.png")))
        page.locator("#case-1").screenshot(path=str(Path(path).with_name("evidential-distribution-compact.png")))
    assert page.locator(".et-mark-distribution svg, .et-mark-distribution polygon").count() == 0
    for node in page.locator(".et-mark-distribution").all():
        box = node.bounding_box()
        cell = node.locator("xpath=ancestor::td").bounding_box()
        assert box["height"] > 3
        assert box["y"] >= cell["y"]
        assert box["y"] + box["height"] <= cell["y"] + cell["height"]
        assert node.evaluate("el => getComputedStyle(el).height") != "auto"
    missing = page.locator("#case-0 tbody tr", has_text="Missing band")
    assert missing.locator(".et-mark-distribution").count() == 0
    assert missing.locator(".et-mark-point").count() == 1
    first = page.locator("#case-0 .et-mark-distribution").first.bounding_box()
    second = page.locator("#case-0 .et-mark-distribution").nth(1).bounding_box()
    sample_points = [[first["x"] + first["width"] * x, first["y"] + first["height"] / 2] for x in (0.1, 0.53, 0.9)]
    sample_points.append([second["x"] + second["width"] * 0.4, second["y"] + second["height"] / 2])
    pixels = page.evaluate(
        """async ({png, points}) => {
        const image = new Image();
        image.src = 'data:image/png;base64,' + png;
        await image.decode();
        const canvas = document.createElement('canvas');
        canvas.width = image.width; canvas.height = image.height;
        const context = canvas.getContext('2d');
        context.drawImage(image, 0, 0);
        return points.map(([x,y]) => [...context.getImageData(Math.floor(x), Math.floor(y), 1, 1).data]);
    }""",
        {"png": b64encode(page.screenshot()).decode(), "points": sample_points},
    )
    assert pixels[0][0] > pixels[1][0] + 80
    assert pixels[2][0] > pixels[1][0] + 80
    assert pixels[3][:3] == [255, 255, 255]


def test_distribution_clipping_height_and_log_scale_share_point_coordinates(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Log density",
                [
                    {
                        "curve": [
                            {"position": 1, "density": 0},
                            {"position": 10, "density": 1},
                            {"position": 100, "density": 0},
                        ],
                        "median": 10,
                    }
                ],
                [
                    col.distribution("curve", height=0.4, density_max=2)
                    .point("median", outline=False)
                    .scale(domain=(1, 100), transform="log", axis=True)
                ],
            )
        ],
    )
    track = page.locator(".et-marks").bounding_box()
    band = page.locator(".et-mark-distribution").bounding_box()
    assert band["height"] == pytest.approx(track["height"] * 0.4, abs=1)
    point = page.locator(".et-mark-point").bounding_box()
    assert point["x"] + point["width"] / 2 == pytest.approx(track["x"] + track["width"] / 2, abs=1)
    assert "0.5) 50%" in page.locator(".et-density-band-run").evaluate("el => el.style.maskImage")


def test_unlabelled_strips_have_height_and_joined_runs_have_no_gap(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Unlabelled strips",
                [{"states": ["W", "W", "L"]}],
                [
                    col.strip("states", colors={"W": "green", "L": "red"}),  # noqa: B005 — mark factory
                    col.strip("states", colors={"W": "green", "L": "red"}, segmented=False),  # noqa: B005
                ],
            )
        ],
    )
    strips = page.locator(".et-mark-strip")
    assert strips.nth(0).bounding_box()["height"] > 5
    assert strips.nth(0).evaluate("el => getComputedStyle(el).gap") == "1px"
    assert strips.nth(1).evaluate("el => getComputedStyle(el).gap") == "0px"


def test_fixed_domain_stack_stays_inside_plot(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Clipped stack",
                [{"name": "A", "a": 50, "b": 50}],
                [
                    col.text("name"),
                    col.stacked_bar("a", "b").scale(domain=(20, 80), axis=True),
                ],
            )
        ],
    )
    track = page.locator(".et-marks").bounding_box()
    for segment in page.locator(".et-mark-stack-seg").all():
        box = segment.bounding_box()
        assert box["x"] >= track["x"] - 1
        assert box["x"] + box["width"] <= track["x"] + track["width"] + 1


def test_point_outlines_can_be_hidden_or_recolored_without_changing_fill(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Point outlines",
                [{"value": 4, "samples": [3, 6]}],
                [
                    col.point("value", color="#2563eb"),
                    col.point("value", color="#2563eb", outline=False),
                    col.point("value", color="#2563eb", outline="#111111"),
                    col.points("samples", color="#2563eb", outline=False),
                    col.points("samples", color="#2563eb", outline="#111111"),
                ],
            )
        ],
    )
    points = page.locator(".et-mark-point")
    assert points.count() == 7
    assert points.nth(0).evaluate("el => getComputedStyle(el).boxShadow") != "none"
    for index in (1, 3, 4):
        assert points.nth(index).evaluate("el => getComputedStyle(el).boxShadow") == "none"
    for index in (2, 5, 6):
        shadow = points.nth(index).evaluate("el => getComputedStyle(el).boxShadow")
        assert "rgb(17, 17, 17)" in shadow and "1px" in shadow
    for point in points.all():
        assert point.evaluate("el => getComputedStyle(el).backgroundColor") == "rgb(37, 99, 235)"


def test_log_minor_ticks_are_unlabeled_log_spaced_and_touch_the_body_boundary(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                f"Log axis {position}",
                [{"value": 1}],
                [col.point("value").scale(domain=(0.1, 10), transform="log", axis=True, axis_position=position)],
            )
            for position in ("top", "bottom")
        ],
    )
    for index, position in enumerate(("top", "bottom")):
        case = page.locator(f"#case-{index}")
        majors = case.locator(".et-axis-tick:not(.et-axis-tick-minor)")
        minors = case.locator(".et-axis-tick-minor")
        assert [float(label) for label in majors.all_text_contents()] == [0.1, 1, 10]
        assert minors.count() == 16
        assert all(text == "" for text in minors.all_text_contents())
        axis = case.locator(".et-axis").bounding_box()
        ticks = case.locator(".et-axis-tick")
        values = [multiple * decade for decade in (0.1, 1) for multiple in range(1, 10)] + [10]
        for tick, value in zip(ticks.all(), values, strict=True):
            geometry = tick.evaluate("""el => {
                const rect = el.getBoundingClientRect();
                const stem = getComputedStyle(el, '::after');
                return {x: rect.x + rect.width / 2, color: stem.borderLeftColor};
            }""")
            # Uniform steps in the original values must bunch up toward each decade's end.
            expected = axis["x"] + axis["width"] * (log10(value) + 1) / 2
            assert geometry["x"] == pytest.approx(expected, abs=0.1)
            assert geometry["color"] == "rgb(0, 0, 0)"
        xs = minors.evaluate_all("nodes => nodes.slice(0, 3).map(el => el.getBoundingClientRect().x)")
        assert xs[1] - xs[0] > xs[2] - xs[1] > 0
        minor = minors.first
        metrics = minor.evaluate("""el => { const rect = el.getBoundingClientRect();
            const style = getComputedStyle(el, '::after');
            return {y: rect.y, top: parseFloat(style.top), height: parseFloat(style.height)}; }""")
        major_height = majors.first.evaluate("el => parseFloat(getComputedStyle(el, '::after').height)")
        assert 0 < metrics["height"] < major_height
        row = case.locator("tbody tr").bounding_box()
        edge = metrics["y"] + metrics["top"] + (metrics["height"] if position == "top" else 0)
        boundary = row["y"] if position == "top" else row["y"] + row["height"]
        assert edge == pytest.approx(boundary, abs=1)
    capture(page, "log-axis-minor-ticks.png")


def test_scale_gallery(page, live_server):
    rows = [
        {"country": "Finland", "before": 29, "after": 94},
        {"country": "Sweden", "before": 76, "after": 41},
        {"country": "Norway", "before": 27, "after": 47},
        {"country": "Denmark", "before": 15, "after": 19},
        {"country": "Iceland", "before": 10, "after": 20},
    ]
    base = (
        col.range("before", "after", color="#222", size=2)
        .point("before", color="#6699ee", size=12)
        .point("after", color="#ef4444", size=12)
        .title("Weekly Sales")
        .align("center")
    )
    cases = []
    for title, options in [
        ("Bottom scale", {"axis": True, "axis_position": "bottom"}),
        ("Top scale", {"axis": True}),
        ("Top scale and gridlines", {"axis": True, "gridlines": True}),
        ("Reference at 50", {"axis": True}),
    ]:
        column = base.scale(domain=(0, 100), **options)
        if title.startswith("Reference"):
            column = column.reference_line(50, color="#ef4444")
        cases.append((title, rows, [col.text("country"), column]))
    cases.append(
        (
            "Fixed domain 10–20; missing marks",
            [
                {"country": "Present", "v": 15, "target": 18, "lo": 12, "hi": 19},
                {"country": "Missing", "v": None, "target": 18, "lo": None, "hi": 19},
            ],
            [
                col.text("country"),
                col.bar("v", size=0.5)
                .range("lo", "hi", fill=True)
                .point("target")
                .scale(domain=(10, 20), axis=True, gridlines=True),
            ],
        )
    )
    mount(page, live_server, cases)
    if path := os.environ.get("EVIDENTIAL_REVIEW_SCREENSHOT"):
        page.screenshot(path=path, full_page=True)
    # Fixed bounds must not silently expand to include zero.
    assert page.locator("#case-4 .et-axis-tick").first.inner_text() == "10"
    missing = page.locator("#case-4 tbody tr:not(.et-axis-row)").nth(1)
    assert missing.locator(".et-mark-bar, .et-mark-range-fill").count() == 0
    assert missing.locator(".et-mark-point").count() == 1
    # Tick centres must share the exact coordinate system of marks/gridlines.
    for index in [1, 2, 3]:
        track = page.locator(f"#case-{index} .et-marks").first.bounding_box()
        axis = page.locator(f"#case-{index} .et-axis").bounding_box()
        assert axis["x"] == pytest.approx(track["x"], abs=1)
        assert axis["width"] == pytest.approx(track["width"], abs=1)
        first_tick = page.locator(f"#case-{index} .et-axis-tick").first.bounding_box()
        assert first_tick["x"] + first_tick["width"] / 2 == pytest.approx(track["x"], abs=1)
    last_cell = page.locator("#case-2 tbody tr:last-child td").first
    assert last_cell.evaluate("el => getComputedStyle(el).borderBottomWidth") == "1px"
    grid = page.locator("#case-2 .et-mark-gridline").first.bounding_box()
    data_row = page.locator("#case-2 tbody tr:not(.et-axis-row)").first.bounding_box()
    assert grid["height"] >= data_row["height"] - 1


def test_mixed_axis_positions_are_per_column(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Independent axes",
                [{"a": 5, "b": 8}],
                [
                    col.point("a").scale(domain=(0, 10), axis=True),
                    col.point("b").scale(domain=(0, 10), axis=True, axis_position="bottom"),
                ],
            )
        ],
    )
    assert page.locator(".et-axis-row-top td").nth(0).locator(".et-axis").count() == 1
    assert page.locator(".et-axis-row-top td").nth(1).locator(".et-axis").count() == 0
    assert page.locator(".et-axis-row-bottom td").nth(0).locator(".et-axis").count() == 0
    assert page.locator(".et-axis-row-bottom td").nth(1).locator(".et-axis").count() == 1


def test_axes_touch_the_first_and_last_horizontal_lines_from_outside_the_rows(page, live_server):
    for font in ("11px", "24px"):
        mount(
            page,
            live_server,
            [
                (
                    "Axes outside the row area",
                    [
                        {"country": "Canada", "top": 30, "bottom": 60},
                        {"country": "Mexico", "top": 70, "bottom": 40},
                    ],
                    [
                        col.text("country"),
                        col.point("top").scale(domain=(0, 100), axis=True),
                        col.point("bottom").scale(domain=(0, 100), axis=True, axis_position="bottom"),
                    ],
                    {"font_size": font},
                )
            ],
        )
        assert page.locator("tbody tr").count() == 2
        assert page.locator("tbody .et-axis").count() == 0
        top = page.locator("thead .et-axis").bounding_box()
        bottom = page.locator("tfoot .et-axis").bounding_box()
        first = page.locator("tbody tr").first.bounding_box()
        last = page.locator("tbody tr").last.bounding_box()
        assert top["y"] + top["height"] == pytest.approx(first["y"], abs=1)
        assert bottom["y"] == pytest.approx(last["y"] + last["height"], abs=1)
        country = page.locator('th[data-column="country"] .et-th-title').bounding_box()
        raised = page.locator('th[data-column="top"] .et-th-title').bounding_box()
        assert country["y"] - raised["y"] >= top["height"] - 1
        for position, boundary in (("top", first["y"]), ("bottom", last["y"] + last["height"])):
            tick = page.locator(f".et-axis-row-{position} .et-axis-tick").first
            box = tick.bounding_box()
            pseudo = tick.evaluate("""el => { const style = getComputedStyle(el, '::after');
                return {top: parseFloat(style.top), height: parseFloat(style.height)}; }""")
            edge = box["y"] + pseudo["top"] + (pseudo["height"] if position == "top" else 0)
            assert edge == pytest.approx(boundary, abs=1)
        for selector, property_name in (
            ("tbody tr:first-child", "borderTopWidth"),
            ("tbody tr:last-child", "borderBottomWidth"),
        ):
            # The boundary belongs to a real row, not an axis metadata row.
            assert (
                page.locator(selector)
                .locator("td")
                .first.evaluate("(el, property) => getComputedStyle(el)[property]", property_name)
                == "1px"
            )
        capture(page, "evidential-axis-boundaries.png")


def test_statistics_and_axes_stay_outside_paginated_details(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Header metadata",
                [{"x": 1}, {"x": 2}],
                [col.point("x").scale(axis=True)],
                {"column_stats": True, "page_size": 1, "row_numbers": True},
            )
        ],
    )
    assert page.locator("thead .et-stats-row").count() == 1
    assert page.locator("thead .et-axis-row").count() == 1
    assert page.locator("tbody tr").count() == 1
    first = page.locator("tbody tr").bounding_box()
    axis = page.locator(".et-axis").bounding_box()
    assert axis["y"] + axis["height"] == pytest.approx(first["y"], abs=1)
    assert page.locator(".et-page-current").inner_text() == "1/2"


@pytest.mark.parametrize(
    "options",
    [{"font_size": "14px"}, {"font_size": "13px"}, {"compact": True}, {"row_lines": True}, {"font_size": "24px"}],
)
def test_gridlines_do_not_add_scroll_overflow_to_the_row_area(page, live_server, options):
    mount(
        page,
        live_server,
        [
            (
                "Gridline bounds",
                [{"country": "Canada", "value": 30}, {"country": "Mexico", "value": 70}],
                [col.text("country"), col.point("value").scale(domain=(0, 100), gridlines=True)],
                {"row_lines": False, "border": False, **options},
            )
        ],
    )
    scroller = page.locator(".et-scroller")
    sizes = scroller.evaluate(
        "el => ({height: el.clientHeight, scrollHeight: el.scrollHeight, width: el.clientWidth, scrollWidth: el.scrollWidth})"
    )
    assert sizes["scrollHeight"] == sizes["height"], sizes
    assert sizes["scrollWidth"] == sizes["width"], sizes
    for line in page.locator(".et-mark-gridline").all():
        box = line.bounding_box()
        parent = line.locator("xpath=ancestor::td")
        cell = parent.bounding_box()
        assert box["y"] >= cell["y"]
        assert box["y"] + box["height"] <= cell["y"] + cell["height"]
        guides = parent.locator(".et-cell-guide-track").bounding_box()
        marks = parent.locator(".et-marks").bounding_box()
        assert guides["x"] == pytest.approx(marks["x"], abs=0.1)
        assert guides["width"] == pytest.approx(marks["width"], abs=0.1)


def test_axes_align_inside_nested_headers_and_subcolumns(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Nested groups",
                [{"name": "A", "a": 5, "b": 8, "source": 13}],
                [
                    col.text("name"),
                    col.group(
                        "Performance",
                        [
                            col.subcolumns(
                                "Weekly",
                                [
                                    col.point("a").scale(domain=(0, 10), axis=True),
                                    col.point("b").scale(domain=(0, 10), axis=True),
                                ],
                            )
                        ],
                    ),
                    col.integer("source").hide(),
                ],
            )
        ],
    )
    assert page.locator("thead").inner_text().count("Performance") == 1
    assert "Source" not in page.locator("thead").inner_text()
    for index in range(2):
        axis = page.locator(".et-axis").nth(index).bounding_box()
        track = page.locator(".et-marks").nth(index).bounding_box()
        assert axis["x"] == pytest.approx(track["x"], abs=1)
        assert axis["width"] == pytest.approx(track["width"], abs=1)


def test_labels_hide_completely_when_the_segment_is_tiny(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Segment labels",
                [{"name": "Mix", "a": 1, "b": 99}],
                [
                    col.text("name"),
                    col.stacked_bar("a", "b", labels=True, colors=["#2563eb", "#bfdbfe"]),
                ],
            )
        ],
    )
    labels = page.locator(".et-mark-stack-label")
    page.wait_for_function("getComputedStyle(document.querySelector('.et-mark-stack-label')).visibility === 'hidden'")
    assert labels.nth(1).is_visible()
    assert "a: 1" in page.locator(".et-marks").get_attribute("aria-label")
    capture(page, "evidential-labels.png")


def test_label_contrast_follows_fill_and_preserves_explicit_colors(page, live_server):
    mount(
        page,
        live_server,
        [
            (
                "Readable labels",
                [{"a": 50, "b": 50}],
                [
                    col.stacked_bar("a", "b", labels=True, colors=["#14532d", "#dcfce7"]),
                    col.bar("a", color="#111111", label=True).label(position="inside_end", color="yellow"),
                    col.bar("b", label=True).label(position="inside_end"),
                ],
                {"theme": {"accent": "#111111"}},
            )
        ],
    )
    labels = page.locator("[data-mark-label]")
    page.wait_for_function(
        "getComputedStyle(document.querySelectorAll('[data-mark-label]')[3]).color === 'rgb(255, 255, 255)'"
    )
    assert labels.nth(0).evaluate("el => getComputedStyle(el).color") == "rgb(255, 255, 255)"
    assert labels.nth(1).evaluate("el => getComputedStyle(el).color") == "rgb(0, 0, 0)"
    assert labels.nth(2).evaluate("el => getComputedStyle(el).color") == "rgb(255, 255, 0)"
    # The neighboring bar also binds 'a'; it must not replace the stack's domain.
    track = page.locator(".et-marks").first.bounding_box()
    segments = page.locator(".et-mark-stack-seg")
    assert segments.nth(0).bounding_box()["width"] == pytest.approx(track["width"] / 2, abs=1)
    assert (
        segments.nth(1).bounding_box()["x"] + segments.nth(1).bounding_box()["width"] <= track["x"] + track["width"] + 1
    )
    capture(page, "evidential-contrast.png")


def test_builder_sections_keep_values_search_sort_and_pagination(page, live_server):
    detail = [
        {"region": "North", "country": "Canada", "arr": 210},
        {"region": "North", "country": "Mexico", "arr": 135},
        {"region": "South", "country": "Brazil", "arr": 100},
    ]
    layout = (
        row_builder.group_by("region")
        .section(values={"country": row_builder.count(suffix=" products"), "arr": "sum"})
        .summary("Subtotal", values={"arr": "sum"})
        .grand_summary(values={"arr": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Display groups",
                detail,
                [col.text("country"), col.integer("arr")],
                {
                    "row_layout": layout,
                    "search": True,
                    "page_size": 1,
                    "row_numbers": True,
                    "section_indent": 1,
                    "stub": "country",
                },
            )
        ],
    )
    assert "North" in page.locator("tbody tr").first.inner_text()
    assert "2 products" in page.locator("tbody tr").first.inner_text()
    assert "345" in page.locator("tbody tr").first.inner_text()
    assert page.locator(".et-page-current").inner_text() == "1/3"
    assert page.locator(".et-display-summary, .et-display-grand_summary").count() == 0
    pad = (
        page.locator("tbody tr")
        .nth(1)
        .locator("td")
        .nth(1)
        .evaluate("el => parseFloat(getComputedStyle(el).paddingLeft)")
    )
    assert pad > 12
    assert "et-row-shaded" in page.locator("tbody tr").nth(1).get_attribute("class")
    page.locator("th", has_text="Arr").click()
    assert "Canada" in page.locator("tbody tr").nth(1).inner_text()
    page.locator(".et-page-controls button").nth(1).click()
    assert "North (cont.)" in page.locator("tbody tr").first.inner_text()
    assert "Mexico" in page.locator("tbody tr").nth(1).inner_text()
    assert "Subtotal" in page.locator("tbody tr").nth(2).inner_text()
    assert "345" in page.locator(".et-display-summary").inner_text()
    assert page.locator(".et-display-grand_summary").count() == 0
    capture(page, "evidential-sections.png")
    page.locator(".et-page-controls button").nth(1).click()
    assert "South" in page.locator("tbody tr").first.inner_text()
    assert "445" in page.locator(".et-display-grand_summary").inner_text()
    page.locator(".et-search").fill("Mexico")
    assert "1 products" in page.locator("tbody tr").first.inner_text()
    assert "135" in page.locator(".et-display-summary").inner_text()
    assert "135" in page.locator(".et-display-grand_summary").inner_text()
    assert "South" not in page.locator("tbody").inner_text()


def test_display_annotations_keep_their_own_style_and_skip_mark_bindings(page, live_server):
    detail = [
        {"region": "North", "country": "Canada", "arr": 210},
        {"region": "North", "country": "Mexico", "arr": 135},
    ]
    layout = (
        row_builder.group_by("region")
        .section(align="center", rule="below", style={"color": "#666666", "font_weight": "normal"})
        .summary(values={"arr": "27 products"}, style={"background": "#eeeeee"})
        .grand_summary(values={"arr": "sum"})
    )
    mount(
        page,
        live_server,
        [
            (
                "Independent display rows",
                detail,
                [col.text("country"), col.bar("arr").point(lambda row: row["arr"])],
                {"row_layout": layout},
            )
        ],
    )
    heading = page.locator(".et-display-section td")
    assert heading.evaluate("el => getComputedStyle(el).textAlign") == "center"
    assert heading.evaluate("el => getComputedStyle(el).color") == "rgb(102, 102, 102)"
    assert heading.evaluate("el => getComputedStyle(el).fontWeight") == "400"
    assert heading.evaluate("el => getComputedStyle(el).borderBottomWidth") == "1px"
    assert heading.evaluate("el => getComputedStyle(el).borderTopWidth") == "1px"
    assert page.locator(".et-display-row .et-marks").count() == 0
    assert page.locator(".et-marks").count() == 2
    assert "27 products" in page.locator(".et-display-summary").inner_text()
    assert (
        page.locator(".et-display-summary td").first.evaluate("el => getComputedStyle(el).backgroundColor")
        == "rgb(238, 238, 238)"
    )
    assert (
        page.locator(".et-display-grand_summary td").first.evaluate("el => getComputedStyle(el).borderBottomWidth")
        == "1px"
    )
    capture(page, "evidential-display-layout.png")


def test_legacy_grouped_widget_keeps_annotations_separate_and_collapses(page, live_server):
    table = grouped_records(
        [
            {"region": "North", "country": "Canada", "arr": 210},
            {"region": "North", "country": "Mexico", "arr": 135},
            {"region": "South", "country": "Brazil", "arr": 100},
        ],
        group_by=["region", "country"],
        measures=["arr"],
        search=True,
        collapsed=False,
    )
    assert len(table.rows) == 3
    mount(page, live_server, [("Legacy adapter", table, [])])
    assert "Canada" in page.locator("tbody").inner_text()
    page.locator("button.et-chevron").first.click()
    assert "Canada" not in page.locator("tbody").inner_text()
    assert "Brazil" in page.locator("tbody").inner_text()
    page.locator(".et-search").fill("Mexico")
    assert "Brazil" not in page.locator("tbody").inner_text()


def test_interval_caps_stay_at_endpoints_independently_of_cell_alignment(page, live_server):
    data = [
        {"lo": -0.4, "estimate": 0.6, "hi": 1.9},
        {"lo": 0.1, "estimate": 1.2, "hi": 2.4},
        {"lo": -1.8, "estimate": -0.5, "hi": 0.7},
    ]
    mount(
        page,
        live_server,
        [
            (
                f"{cap} caps · {align}",
                data,
                [col.range("lo", "hi", cap=cap, align=align).point("estimate").scale(domain=(-2, 3))],
                {"width": "100%"},
            )
            for cap in ("line", "dot")
            for align in ("left", "center", "right")
        ],
    )
    for width in (520, 800):
        page.locator("section").evaluate_all(
            "(nodes, width) => nodes.forEach(el => el.style.width = width + 'px')", width
        )
        endpoints = page.locator(".et-mark-range").evaluate_all("""lines => lines.map(line => {
            const bounds = line.getBoundingClientRect();
            const center = selector => {
                const cap = line.querySelector(selector).getBoundingClientRect();
                return cap.x + cap.width / 2;
            };
            return {left: bounds.left, right: bounds.right,
                start: center('.et-mark-cap-start'), end: center('.et-mark-cap-end')};
        })""")
        assert len(endpoints) == 18
        for endpoint in endpoints:
            assert abs(endpoint["start"] - endpoint["left"]) < 1, endpoint
            assert abs(endpoint["end"] - endpoint["right"]) < 1, endpoint
    capture(page, "interval-cap-endpoints.png")


def test_public_api_acceptance_marks(page, live_server):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    cases = [
        (
            "Independent categorical labels",
            [{"votes": 70, "candidate": "Alpha", "old": 50, "target": 80}],
            [
                col.bar("votes", color="#93c5fd", label="@candidate").label(position="inside_end"),
                col.bar("votes", size=0.3, valign="top").bar("old", size=0.3, valign="bottom").point("target"),
            ],
        ),
        (
            "Interval overflow and dot caps",
            [{"name": "Study A", "lo": -5, "hi": 15, "estimate": 4}],
            [
                col.text("name"),
                col.range("lo", "hi", cap="dot", overflow="arrow").point("estimate").scale(domain=(0, 10), axis=True),
            ],
        ),
        (
            "Two-sided survey",
            [{"name": "Survey", "wrong": 30, "right": 70}],
            [
                col.text("name"),
                col.bar("wrong", side="left", color="salmon").bar("right", side="right", color="teal").scale(axis=True),
            ],
        ),
        (
            "Neutral-centred Likert",
            [{"name": "Survey", "a": 15, "b": 20, "n": 10, "c": 25, "d": 30}],
            [
                col.text("name"),
                col.stacked_bar(
                    "a",
                    "b",
                    "n",
                    "c",
                    "d",
                    diverge_at="n",
                    labels=True,
                    colors=["#b91c1c", "#fca5a5", "#ddd", "#86efac", "#16a34a"],
                ).scale(axis=True),
            ],
        ),
        (
            "Percentage stack and tiny labels",
            [{"name": "Mix", "a": 1, "b": 24, "c": 25, "d": 30, "e": 20}],
            [
                col.text("name"),
                col.stacked_bar(
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    normalize="percent",
                    labels="percent",
                    colors=["#172554", "#1d4ed8", "#60a5fa", "#93c5fd", "#bfdbfe"],
                ).scale(axis=True),
            ],
        ),
        (
            "Categorical and positioned strips",
            [
                {
                    "form": ["W", "D", "L"],
                    "time": [
                        {"start": 0, "end": 2, "category": "W"},
                        {"start": 2, "end": 10, "category": "L"},
                    ],
                }
            ],
            [
                col.strip("form", colors={"W": "green", "D": "grey", "L": "red"}, labels=True),
                col.strip("time", colors={"W": "green", "L": "red"}).scale(domain=(0, 10), axis=True),
            ],
        ),
        (
            "Structured sparkline with a gap",
            [
                {
                    "name": "Series",
                    "trend": [
                        {"x": 0, "y": 2},
                        {"x": 1, "y": 5},
                        {"x": 2, "y": None},
                        {"x": 8, "y": 4},
                        {"x": 10, "y": 8},
                    ],
                }
            ],
            [col.text("name"), col.sparkline("trend", x="x", y="y", markers=True, width=240)],
        ),
        (
            "Precomputed boxplot and outliers",
            [{"name": "Sample", "min": 1, "q1": 2, "med": 4, "q3": 7, "max": 9, "out": [12]}],
            [
                col.text("name"),
                col.boxplot("min", "q1", "med", "q3", "max", outliers="out").scale(axis=True),
            ],
        ),
        (
            "Log forest with reference at one",
            [{"name": "Study B", "lo": 0.5, "hi": 2, "est": 1.4}],
            [
                col.text("name"),
                col.range("lo", "hi", cap="line")
                .point("est")
                .scale(domain=(0.1, 10), transform="log", axis=True, gridlines=True)
                .reference_line(1, color="red"),
            ],
        ),
    ]
    mount(page, live_server, cases)
    page.wait_for_function("document.querySelectorAll('.et-table').length === 9")
    assert page.locator("#case-0 .et-mark-label").inner_text() == "Alpha"
    assert page.locator("#case-1 .et-mark-arrow").count() == 2
    assert (
        page.locator("#case-1 .et-mark-arrow").first.evaluate("el => getComputedStyle(el).borderTopColor")
        == "rgba(0, 0, 0, 0)"
    )
    assert page.locator("#case-6 svg polyline").count() == 2
    assert page.locator("#case-7 .et-box-outlier").count() == 1
    assert not errors
    capture(page, "evidential-acceptance.png")
