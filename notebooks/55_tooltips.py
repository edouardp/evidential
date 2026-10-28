# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Inspect full values, overlapping marks and metadata without changing labels."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():

    import json
    from pathlib import Path

    import marimo as mo

    from evidential import EvidentialTable, col, label, settings

    return EvidentialTable, Path, col, json, label, mo, settings


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Tooltips: inspect the data behind the marks

    Hover numbers or marks to see named values. Abbreviated and rounded labels
    keep the table compact; tooltips expand the underlying values with commas,
    keeping their units and available precision. Tooltips use plain text and
    support **newlines**. All figures below are illustrative except the matches.

    **Keyboard:** Tab to a graphic cell; Left/Right moves through its marks,
    Home/End jumps to the first/last, and Escape dismisses the tooltip. There is
    one Tab stop per graphic cell, rather than one per dot. Touch a mark to
    inspect it; row selection still works.
    """)
    return


@app.cell
def frame(settings):
    tooltip_frame = settings(border=False, row_lines=False, row_shading=True, page_size=0, width="100%")
    return (tooltip_frame,)


@app.cell(hide_code=True)
def precision_doc(mo):
    mo.md("""
    ## Full values behind compact labels

    Hover **1.3T**, the rounded percentage, or the currency. The tooltip shows
    `1,253,224,564,123.12`, `12.3456%`, and `$1,253,224,564.12`, respectively.
    Tiny scientific values also expand without disappearing into a rounded zero.
    """)
    return


@app.cell
def full_values(EvidentialTable, col, mo, tooltip_frame):
    precision_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {
                    "measure": "Example",
                    "amount": 1_253_224_564_123.12,
                    "share": 0.123456,
                    "revenue": 1_253_224_564.12,
                    "tiny": 1.23456e-7,
                }
            ],
            columns=[
                col.text("measure"),
                col.number("amount", format="compact"),
                col.percent("share", decimals=0),
                col.currency("revenue", format="usd0"),
                col.number("tiny", format="sci"),
            ],
            settings=tooltip_frame,
            title="Compact on the page, full values on inspection",
        )
    )
    precision_table
    return


@app.cell(hide_code=True)
def overlap_doc(mo):
    mo.md("""
    ## Overlapping dots

    Hover the dot at **20%**: Younger and Middle have exactly the same value.
    The next row puts them close together. Both appear in a multiline tooltip
    whenever their enlarged hit areas contain the pointer. Older is farther
    away and has its own tooltip. The visible dots keep their original size.
    """)
    return


@app.cell
def overlapping_points(EvidentialTable, col, mo, tooltip_frame):
    overlap_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {"case": "Coincident", "younger": 0.2, "middle": 0.2, "older": 0.08},
                {"case": "Nearby", "younger": 0.2, "middle": 0.202, "older": 0.081234},
            ],
            columns=[
                col.text("case"),
                col.points(
                    {"younger": "Younger", "middle": "Middle", "older": "Older"},
                    connect=True,
                    title="Population share",
                    format="pct0",
                )
                .scale(domain=(0, 0.3), axis=True, axis_position="bottom")
                .legend(),
            ],
            settings=tooltip_frame,
            title="Two values under one pointer",
        )
    )
    overlap_table
    return


@app.cell(hide_code=True)
def stacks_doc(mo):
    mo.md("""
    ## Named stack segments, including hidden labels

    Hover a segment or its label: **Storage: 61%**, its full dollar value and
    the row total remain available. The tiny Other segment has the same tooltip
    even though its label will not fit. Label formatting does not change the
    tooltip's dollar formatting. Both halves of Neutral in the diverging stack
    describe the **whole** category, not a misleading half-value.
    """)
    return


@app.cell
def stacked_values(EvidentialTable, col, label, mo, tooltip_frame):
    stack_table = mo.ui.anywidget(
        EvidentialTable(
            [{"plan": "Standard", "storage": 1235, "requests": 782, "other": 1}],
            columns=[
                col.text("plan"),
                col.stacked_bar(
                    "storage",
                    "requests",
                    "other",
                    title="Monthly cost",
                    colors=["#2563eb", "#f59e0b", "#94a3b8"],
                    format="usd0",
                    labels=label.share().fmt("pct0"),
                    normalize="percent",
                ).legend(),
            ],
            settings=tooltip_frame,
            title="Share labels, full dollar amounts",
        )
    )
    neutral_table = mo.ui.anywidget(
        EvidentialTable(
            [{"question": "Would recommend", "disagree": 20, "neutral": 30, "agree": 50}],
            columns=[
                col.text("question"),
                col.stacked_bar(
                    "disagree",
                    "neutral",
                    "agree",
                    diverge_at="neutral",
                    title="Response",
                    colors=["#dc2626", "#a1a1aa", "#2563eb"],
                    format="num0",
                    normalize="percent",
                ).legend(),
            ],
            settings=tooltip_frame,
            title="A split neutral category retains its full value",
        )
    )
    mo.vstack([stack_table, neutral_table])
    return


@app.cell(hide_code=True)
def match_doc(mo):
    mo.md("""
    ## Real match metadata

    Each segment is one of Arsenal FC's last twelve recorded domestic league
    matches in calendar 2024. Hover for result, date, opponent, score, venue and
    competition. The extra fields travel with each observation; no row lookup
    or query runs on hover. Source: the committed football-data /
    worldclubratings.com snapshot used in notebook 46; ODC-By 1.0.
    """)
    return


@app.cell
def match_data(Path, json):
    snapshot = json.loads((Path(__file__).parent / "data/46_football_england_2024.json").read_text())
    matches = sorted(
        [
            game
            for game in snapshot["matches"]
            if game["team"] == "Arsenal FC" and game["competition"] == "england" and game["level"] == "national"
        ],
        key=lambda game: (game["match_date"], game["opponent"], game["venue"]),
    )[-12:]
    form = [
        {
            "category": game["result"],
            "date": game["date"],
            "opponent": game["opponent"],
            "score": game["score"],
            "venue": game["venue"],
            "competition": game["competition"],
        }
        for game in matches
    ]
    return (form,)


@app.cell
def football_matches(EvidentialTable, col, form, mo, tooltip_frame):
    match_table = mo.ui.anywidget(
        EvidentialTable(
            [{"club": "Arsenal FC", "form": form}],
            columns=[
                col.text("club"),
                col.strip("form", colors={"Win": "#2166ac", "Draw": "#b8bcc2", "Loss": "#b2182b"})
                .title("Recent league form")
                .legend(),
            ],
            settings=tooltip_frame,
            title="Football: more than a colour",
        )
    )
    match_table
    return


@app.cell(hide_code=True)
def ranges_doc(mo):
    mo.md("""
    ## Ranges and five-number summaries

    Hover the dumbbell's line for Before, After and the absolute change; its
    endpoint dots have their own named values. A box plot reports minimum,
    lower quartile, median, upper quartile and maximum. Hover an outlier for its
    value. These tooltips work whether or not labels are drawn.
    """)
    return


@app.cell
def ranges_and_boxes(EvidentialTable, col, mo, tooltip_frame):
    range_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {
                    "region": "North",
                    "before": 30,
                    "after": 80,
                    "minimum": 10,
                    "q1": 25,
                    "median": 45,
                    "q3": 65,
                    "maximum": 90,
                    "outliers": [97],
                },
                {
                    "region": "South",
                    "before": 75,
                    "after": 40,
                    "minimum": 15,
                    "q1": 30,
                    "median": 50,
                    "q3": 70,
                    "maximum": 85,
                    "outliers": [],
                },
            ],
            columns=[
                col.text("region"),
                col.range("before", "after", title="Weekly sales", color="#64748b", negative_color="#dc2626")
                .points({"before": "Before", "after": "After"})
                .scale(domain=(0, 100)),
                col.boxplot(
                    "minimum", "q1", "median", "q3", "maximum", outliers="outliers", title="Distribution"
                ).scale(domain=(0, 100)),
            ],
            settings=tooltip_frame,
            title="Inspect ranges and distributions",
        )
    )
    range_table
    return


@app.cell(hide_code=True)
def overrides_doc(mo):
    mo.md(r"""
    ## Override or disable

    `.tooltip("@hover_text")` reads plain text from a row field, including line
    breaks. `.tooltip("Fixed text\nSecond line")` supplies a literal, and
    `.tooltip(False)` disables the cell's tooltip, including child marks.
    `.tooltip()` restores automatic inspection. Overrides apply to scalar and
    graphic columns alike; they do not interpret HTML.
    """)
    return


@app.cell
def custom_tooltips(EvidentialTable, col, mo, tooltip_frame):
    custom_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {
                    "name": "Regional total",
                    "amount": 1253224564.12,
                    "quiet": 70,
                    "hover_text": "Regional total\nIncludes online orders\nExcludes refunds",
                }
            ],
            columns=[
                col.text("name").tooltip("@hover_text"),
                col.number("amount", format="compact").tooltip("Reported amount\nProvisional estimate"),
                col.bar("quiet", title="Tooltip disabled").tooltip(False),
            ],
            settings=tooltip_frame,
            title="Custom multiline text and an explicit opt-out",
        )
    )
    custom_table
    return


@app.cell(hide_code=True)
def sparkline_doc(mo):
    mo.md("""
    ## Sparklines: one observation at a time

    Move across the full height of the area sparkline: its x-position chooses
    the nearest recorded year, with one value in the tooltip. Dense observations
    are never collected as overlapping points. The swatch matches the signed
    area: teal above the 100% reference, red below it.

    Hover delays are in **seconds**. This table uses
    `settings(tooltips={"delay": 0.8, "text_delay": 1.5})`: graphics wait 0.8s
    and text waits 1.5s. The bar overrides this with `.tooltip(delay=0)`, so it
    appears immediately. Elsewhere the defaults are instant graphics and an
    0.8s text delay. Keyboard and touch inspection always responds immediately.
    """)
    return


@app.cell
def sparkline_inspection(
    EvidentialTable,
    col,
    label,
    mo,
    settings,
    tooltip_frame,
):
    spark_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {
                    "country": "Example economy",
                    "amount": 1_253_224_564.12,
                    "ratios": [
                        {"year": 2000 + index, "ratio": value}
                        for index, value in enumerate(
                            [0.8, 0.9, 1.02, 1.12, 0.95, 0.85, 1.04, 1.16, 1.08, 0.92, 0.88, 1.2]
                        )
                    ],
                    "note": "Illustrative exports / imports\n100% means balanced trade",
                }
            ],
            columns=[
                col.text("country").tooltip("@note"),
                col.sparkline(
                    "ratios",
                    title="Exports / imports",
                    type="area",
                    signed=True,
                    reference=1,
                    x="year",
                    y="ratio",
                    y_fmt="pct0",
                    color="#0f766e",
                    width=180,
                    height=28,
                ),
                col.bar("amount", format="compact", label=label.auto_position("inside end"))
                .title("Instant graphic")
                .tooltip(delay=0),
            ],
            settings=settings(**tooltip_frame, tooltips={"delay": 0.8, "text_delay": 1.5}),
            title="Signed area and separate hover delays",
        )
    )
    spark_table
    return


if __name__ == "__main__":
    app.run()
