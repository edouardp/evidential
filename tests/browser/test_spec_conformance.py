"""Exercise the declarative API's geometry through the shipped browser bundle."""

from __future__ import annotations

import os
from base64 import b64encode
from pathlib import Path

import pytest

from evidential import EvidentialTable, col, grouped_records
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
    capture(page, "evidential-distribution-bands.png")
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
    capture(page, "evidential-distribution-bands.png")


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
