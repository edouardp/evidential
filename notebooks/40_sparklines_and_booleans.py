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

    from evidential import EvidentialTable, col, settings

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
                col.text("service", title="Service"),
                col.boolean(
                    "healthy",
                    title="Healthy",
                    true_symbol="✓",
                    false_symbol="✗",
                    true_text="Active",
                    false_text="Down",
                ),
                col.boolean(
                    "replicated",
                    title="Replicated",
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
                col.icons("signal", map={"buy": "▲", "sell": "▼", "hold": "●"}, title="Signal"),
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
