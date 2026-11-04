# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Sparkline styles and boolean display.

`col.sparkline` draws an array as a line, area, bar or points, with per-point
markers and a signed area fill. `col.boolean` writes a true/false value as a
symbol and/or label. `col.icons` maps a category to a glyph or image.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col

    return EvidentialTable, col, mo


@app.cell
def _(mo):
    mo.md("""
    # Sparkline styles and booleans

    An array column can be drawn five ways — `type="line"`, `"area"`, `"bar"`,
    `"points"` or `"change"`. `markers=True` puts a dot at every value on a line/area, and
    `signed=True` splits an area fill at the zero baseline, so gains and losses
    get different colours.

    The change column uses `delta=True` to compare adjacent observations, so
    revenue falling from 5 to 4 draws a down marker. Its first slot is blank;
    missing values break comparisons. Without `delta=True`, change sparklines
    expect values that already represent changes or signed outcomes.
    """)
    return


@app.cell
def _():
    trends = [
        {"metric": "Revenue", "values": [3, 5, 4, 7, 9, 8, 11, 13]},
        {"metric": "Costs", "values": [4, 4, 5, 6, 6, 7, 7, 8]},
        {"metric": "Margin", "values": [1, 2, -1, 3, -2, 4, 2, -1]},
        {"metric": "Cash", "values": [2, 4, 6, 5, 8, 7, 9, 12]},
    ]
    return (trends,)


@app.cell
def _(EvidentialTable, col, mo, trends):
    styles = mo.ui.anywidget(
        EvidentialTable(
            trends,
            title="One series, five styles",
            subtitle="line · area · bar · points · change from the previous observation",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("metric"),
                col.array("values", title="Line").sparkline(type="line", color="#2563eb"),
                col.array("values", title="Area").sparkline(type="area", color="#0ea5e9"),
                col.array("values", title="Bar").sparkline(type="bar", color="#6366f1"),
                col.array("values", title="Points").sparkline(type="points", color="#db2777"),
                col.array("values", title="Change (Δ)").sparkline(type="change", delta=True),
            ],
        )
    )
    styles
    return


@app.cell
def _(EvidentialTable, col, mo, trends):
    signed = mo.ui.anywidget(
        EvidentialTable(
            trends,
            title="Markers and a signed area",
            subtitle="markers=True and signed=True on the same series",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("metric"),
                col.array("values", title="Line + markers").sparkline(
                    type="line", color="#2563eb", markers=True
                ),
                col.array("values", title="Signed area").sparkline(
                    type="area", color="#16a34a", signed=True, height=26
                ),
            ],
        )
    )
    signed
    return


@app.cell
def _(mo):
    mo.md("""
    ## End markers and per-point colours

    `markers="ends"` marks only the first and last point (useful on a line),
    and `marker_color=` sets the marker colour. If the array elements are
    objects with a `color` key, each marker takes its own colour — the SQL can
    compute it alongside `x` and `y`.
    """)
    return


@app.cell
def _():
    marked = [
        {
            "metric": "Net",
            "values": [
                {"x": 1, "y": 3, "color": "#dc2626"},
                {"x": 2, "y": 5},
                {"x": 3, "y": 4, "color": "#dc2626"},
                {"x": 4, "y": 7},
                {"x": 5, "y": 9, "color": "#16a34a"},
            ],
        },
        {
            "metric": "Gross",
            "values": [
                {"x": 1, "y": 8, "color": "#16a34a"},
                {"x": 2, "y": 7},
                {"x": 3, "y": 6},
                {"x": 4, "y": 6},
                {"x": 5, "y": 5, "color": "#dc2626"},
            ],
        },
    ]
    return (marked,)


@app.cell
def _(EvidentialTable, col, marked, mo):
    markers = mo.ui.anywidget(
        EvidentialTable(
            marked,
            title="Markers",
            subtitle="Ends only, and a colour per point",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("metric"),
                col.array("values", title="Ends").sparkline(
                    type="line", color="#94a3b8", markers="ends", marker_color="#0f172a", height=24
                ),
                col.array("values", title="Per-point colour").sparkline(
                    type="line", color="#cbd5e1", markers=True, x="x", y="y", height=24
                ),
            ],
        )
    )
    markers
    return


@app.cell
def gradient_doc(mo):
    mo.md("""
    ## Color by y value

    The usual fluent color API also works on every sparkline style:

    ```python
    col.sparkline("values", type="bar").color(
        scale="RdBu", min=-10, max=10, midpoint=0,
    )
    ```

    Bars and dots look up their own y value. Lines and areas use a vertical
    gradient: the color at a given height is the same everywhere in the chart,
    including along a slope between observations. Missing values leave gaps. Without fixed bounds, all matching rows supply the gradient's range
    before pagination. Reuse `.domain(...)` to share a range and palette with
    other columns.

    A data object's `color` overrides bars, dots and change markers; the last
    row highlights one observation in purple. It never colors an outgoing line
    segment. For a line/area, enable markers to show an observation's color. Visible markers may also use `marker_color=`.
    Change sparklines still map their entire `steady` interval to the middle
    color. Other styles use the normal linear or diverging lookup; an explicit
    `stops=[{"value": ..., "color": ...}, ...]` works just as it does for cells.
    """)
    return


@app.cell
def gradient_data():
    gradient_rows = [
        {"series": "Rising", "values": [-10, -7, -2, 0, 3, 8, 10]},
        {"series": "Falling", "values": [10, 8, 3, 0, -2, -7, -10]},
        {"series": "Gaps and override", "values": [
            {"x": 0, "y": -10}, {"x": 1, "y": -4}, None,
            {"x": 3, "y": 0, "color": "#7c3aed"}, {"x": 4, "y": 5}, {"x": 5, "y": 10},
        ]},
    ]
    return (gradient_rows,)


@app.cell
def gradient_sparklines(EvidentialTable, col, gradient_rows, mo):
    gradient_table = mo.ui.anywidget(EvidentialTable(
        gradient_rows,
        title="One y-value gradient, five sparkline styles",
        subtitle="Red for low values, gray at zero, blue for high values; purple overrides one observation",
        border=False,
        row_lines=False,
        columns=[
            col.text("series"),
            col.sparkline("values", title="Bars", type="bar", width=150, height=30)
                .color(scale=["#b2182b", "#b8bcc2", "#2166ac"], min=-10, max=10, midpoint=0),
            col.sparkline("values", title="Points", type="points", width=150, height=30)
                .color(scale=["#b2182b", "#b8bcc2", "#2166ac"], min=-10, max=10, midpoint=0),
            col.sparkline("values", title="Line", type="line", markers=True, width=150, height=30)
                .color(scale=["#b2182b", "#b8bcc2", "#2166ac"], min=-10, max=10, midpoint=0),
            col.sparkline("values", title="Area", type="area", fill_opacity=0.5, width=150, height=30)
                .color(scale=["#b2182b", "#b8bcc2", "#2166ac"], min=-10, max=10, midpoint=0),
            col.sparkline("values", title="Change", type="change", steady=(-1, 1), width=150, height=30)
                .color(scale=["#b2182b", "#b8bcc2", "#2166ac"], min=-10, max=10),
        ],
    ))
    gradient_table
    return


@app.cell
def vertical_area_doc(mo):
    mo.md("""
    ## Vertical area colors: fades, thresholds and anomalies

    These illustrative series show four uses of the same vertical paint. A
    constant green outline with `fill_opacity=(0, 0.65)` fades from transparent
    at the baseline to 65% opacity at the edge. The baseline is `reference=`
    (zero by default), clamped to the plotted range with `fit_to_data=True`.

    `.color(stops=...)` gives explicit colors at y values. Closely spaced stops
    make the transition at 40 sharp, so only the portion **above** 40 is red.
    Likewise, anomaly fills can switch at zero or use several severity bands.
    Alpha in a stop is preserved; `fill_opacity` multiplies it. The plain area
    default is 0.22 opacity; a color gradient defaults to 1 so its alpha stops
    determine the fill. `fill_opacity` only affects the area, never its outline.

    Color bounds do not constrain height: an anomaly of 3 with color endpoints
    -1 and 1 still plots at 3, using the endpoint color at 1. The last column
    demonstrates this clamping with a transparent zero stop.
    """)
    return


@app.cell
def vertical_area_data():
    area_profiles = [
        {"series": "Coastal", "stock": [2952, 3150, 3070, 3290, 3210, 3380, 3731, 3450, 3372],
         "threshold": [0, 27, 19, 35, 24, 45, 29, 53, 31, 41, 20],
         "anomaly": [0, 0.7, 1.5, 0.4, -0.8, -2.4, -0.5, 0.6, 2.8, 1.2, -0.3]},
        {"series": "Inland", "stock": [3120, 3240, 3190, 3350, 3310, 3430, 3490, 3280, 3400],
         "threshold": [12, 36, 43, 25, 39, 47, 21, 32, 46, 28, 17],
         "anomaly": [1.2, -0.2, -1.8, -0.4, 1.1, 2.2, 0.3, -1.3, -0.5, 1.8, 0.8]},
        {"series": "Highland", "stock": [3080, 3200, None, 3310, 3420, 3350, 3550, 3460, 3510],
         "threshold": [7, 28, 38, None, 44, 23, 34, 48, 30, 40, 24],
         "anomaly": [-1.5, 0.2, 2.4, None, 0.5, -0.7, -2.1, -0.2, 1.7, 0.6, -0.9]},
    ]
    return (area_profiles,)


@app.cell
def vertical_area_sparklines(EvidentialTable, area_profiles, col, mo):
    vertical_area_table = mo.ui.anywidget(EvidentialTable(
        area_profiles,
        title="Color follows height, not the next observation",
        subtitle="Illustrative series · stock-style fade, threshold at 40, signed bands, and clamped alpha gradient",
        border=False,
        row_lines=False,
        columns=[
            col.text("series"),
            col.sparkline("stock", title="Baseline fade", type="area", color="#00a878",
                          fit_to_data=True, fill_opacity=(0, 0.65), width=150, height=36),
            col.sparkline("threshold", title="Above 40", type="area", fill_opacity=0.7, width=150, height=36)
                .color(stops=[
                    {"value": 0, "color": "#20af4b"},
                    {"value": 40, "color": "#20af4b"},
                    {"value": 40.001, "color": "#ed1c24"},
                    {"value": 60, "color": "#ed1c24"},
                ]),
            col.sparkline("anomaly", title="Severity bands", type="area", reference=0,
                          fill_opacity=0.8, width=150, height=36)
                .color(stops=[
                    {"value": -3, "color": "#e66b13"}, {"value": -1, "color": "#e66b13"},
                    {"value": -0.999, "color": "#ffe49a"}, {"value": -0.001, "color": "#ffe49a"},
                    {"value": 0, "color": "#cae9c2"}, {"value": 0.999, "color": "#cae9c2"},
                    {"value": 1, "color": "#6dc3cd"}, {"value": 3, "color": "#6dc3cd"},
                ]),
            col.sparkline("anomaly", title="Clamped gradient", type="area", reference=0, width=150, height=36)
                .color(stops=[
                    {"value": -1, "color": "#ff7f50"},
                    {"value": 0, "color": "#ffffff00"},
                    {"value": 1, "color": "#4682b4"},
                ]),
        ],
    ))
    vertical_area_table
    return


@app.cell
def fade_threshold_doc(mo):
    mo.md("""
    ## Transparent to green, then red above 40

    This area uses one vertical gradient: transparent green at zero, fully
    opaque green at 40, then red above 40. The very small interval from 40 to
    40.001 makes the switch sharp. Only the portion of a peak above that height
    is red; everything below it still fades from transparent to green.

    ```python
    col.sparkline("threshold", type="area").color(stops=[
        {"value": 0, "color": "#20af4b00"},
        {"value": 40, "color": "#20af4b"},
        {"value": 40.001, "color": "#ed1c24"},
        {"value": 60, "color": "#ed1c24"},
    ])
    ```
    """)
    return


@app.cell
def fade_threshold_sparklines(EvidentialTable, area_profiles, col, mo):
    fade_threshold_table = mo.ui.anywidget(EvidentialTable(
        area_profiles,
        title="Transparent → green → red",
        subtitle="Illustrative series · green reaches full opacity at 40; peaks turn red above 40",
        border=False,
        row_lines=False,
        stretch=False,
        columns=[
            col.text("series"),
            col.sparkline("threshold", title="Fade, then threshold", type="area", width=240, height=48)
                .color(stops=[
                    {"value": 0, "color": "#20af4b00"},
                    {"value": 40, "color": "#20af4b"},
                    {"value": 40.001, "color": "#ed1c24"},
                    {"value": 60, "color": "#ed1c24"},
                ]),
        ],
    ))
    fade_threshold_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Booleans as a symbol and label

    `col.boolean(..., true_symbol="✓", false_symbol="✗", true_text="Active",
    false_text="Inactive")` writes the state directly, rather than `true` /
    `false`. The symbol is green when true and red when false.
    """)
    return


@app.cell
def _():
    services = [
        {"service": "API", "healthy": True, "replicated": True},
        {"service": "Worker", "healthy": True, "replicated": False},
        {"service": "Scheduler", "healthy": False, "replicated": True},
        {"service": "Database", "healthy": True, "replicated": True},
    ]
    return (services,)


@app.cell
def _(EvidentialTable, col, mo, services):
    status = mo.ui.anywidget(
        EvidentialTable(
            services,
            title="Service health",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("service"),
                col.boolean(
                    "healthy",
                    true_symbol="✓",
                    false_symbol="✗",
                    true_text="Active",
                    false_text="Down",
                ),
                col.boolean(
                    "replicated",
                    true_symbol="●",
                    false_symbol="○",
                    true_text="Yes",
                    false_text="No",
                ),
            ],
        )
    )
    status
    return


@app.cell
def _(mo):
    mo.md("""
    ## An icon mapped from a category

    `col.icons("signal", map={...})` draws each category as a glyph (or an image
    URL / data-URI). An unmapped value falls back to its text.
    """)
    return


@app.cell
def _():
    signals = [
        {"asset": "Bonds", "signal": "buy", "note": "Yield peak"},
        {"asset": "Equities", "signal": "hold", "note": "Fairly valued"},
        {"asset": "Oil", "signal": "sell", "note": "Demand falling"},
        {"asset": "Gold", "signal": "buy", "note": "Hedge"},
    ]
    return (signals,)


@app.cell
def _(EvidentialTable, col, mo, signals):
    icons = mo.ui.anywidget(
        EvidentialTable(
            signals,
            title="Position signals",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("asset"),
                col.icons("signal", map={"buy": "▲", "sell": "▼", "hold": "●"}),
                col.text("signal", title="Meaning"),
                col.text("note"),
            ],
        )
    )
    icons
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `type="points"` draws only the markers; `markers=True` adds them to a
      line/area without changing the series.
    - `signed=True` needs a series that crosses zero; the zero baseline is drawn
      automatically when the range straddles it.
    - A boolean column keeps sorting/search/export on the underlying value; the
      symbol and label are presentation only.
    """)
    return


if __name__ == "__main__":
    app.run()
