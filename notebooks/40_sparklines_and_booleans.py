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
symbol and/or label.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, mo, settings


@app.cell
def _(mo):
    mo.md("""
    # Sparkline styles and booleans

    An array column can be drawn four ways — `type="line"`, `"area"`, `"bar"` or
    `"points"`. `markers=True` puts a dot at every value on a line/area, and
    `signed=True` splits an area fill at the zero baseline, so gains and losses
    get different colours.
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
            title="One series, four styles",
            subtitle="line · area · bar · points",
            row_lines=False,
            border=False,
            stretch=False,
            columns=[
                col.text("metric"),
                col.array("values", title="Line").sparkline(type="line", color="#2563eb"),
                col.array("values", title="Area").sparkline(type="area", color="#0ea5e9"),
                col.array("values", title="Bar").sparkline(type="bar", color="#6366f1"),
                col.array("values", title="Points").sparkline(type="points", color="#db2777"),
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
