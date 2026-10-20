# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Encoding marks — several visual marks in one column (ADR-058).

A column is a presentation slot that can hold an ordered list of *encodings*
(bar, point, range, stacked_bar, strip), each bound to its own field and sharing
one scale. Labels are mark-owned and may name another field.
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
    # Encoding marks

    A column can carry **several marks**. `col.bar(...).bar(...)` overlays two
    bars; `.point(...)` adds a target; `col.range(...)` draws an interval. Every
    mark binds its own field and they share one horizontal scale, so their
    lengths are comparable. A plain `col.bar("x")` still behaves exactly as it
    always did — the marks layer only engages when you use it.

    ```python
    col.bar("current", color="navy", size=0.8).bar("previous", color="#d1d5db", size=0.2)
    col.bar("votes", label="@candidate", color="@party_colour")
    col.bar("current").point("target")
    col.range("low", "high", cap="line").point("estimate").scale(domain=(0, 100))
    ```
    """)
    return


@app.cell
def _():
    polling = [
        {"party": "National", "votes": 38, "previous": 41, "target": 40, "colour": "#2563eb"},
        {"party": "Labour", "votes": 34, "previous": 31, "target": 33, "colour": "#dc2626"},
        {"party": "Green", "votes": 11, "previous": 7, "target": 9, "colour": "#16a34a"},
        {"party": "ACT", "votes": 9, "previous": 11, "target": 10, "colour": "#eab308"},
        {"party": "Māori", "votes": 4, "previous": 3, "target": 3, "colour": "#9333ea"},
        {"party": "Other", "votes": 4, "previous": 7, "target": 5, "colour": "#64748b"},
    ]
    return (polling,)


@app.cell
def _(EvidentialTable, col, mo, polling, settings):
    # Two overlaid bars (this poll over the last), a per-row colour column, and
    # an independent target marker — all on the same shared scale.
    overlaid = mo.ui.anywidget(
        EvidentialTable(
            polling,
            settings=settings(
                title="Polling",
                subtitle="Latest versus previous, with the target",
                caption="Illustrative data.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=True, width=600
            ),
            columns=[
                col.text("party"),
                col.bar("previous", color="#e2e8f0", size=0.9, title="Previous")
                .bar("votes", color="@colour", size=0.42, label={"value": True, "suffix": "%"}, label_position="outside_end")
                .point("target", color="#0f766e", size=7)
                .scale(domain=(0, 45)),
            ],
        )
    )
    overlaid
    return


@app.cell
def _(mo):
    mo.md("""
    ## An interval with a point

    `col.range("low", "high", cap="line")` draws a capped interval; `.point(...)`
    marks the estimate on the same scale. Nothing statistical is implied — the
    five numbers arrive from SQL.
    """)
    return


@app.cell
def _():
    estimates = [
        {"name": "Effect A", "low": -0.4, "estimate": 0.6, "high": 1.9},
        {"name": "Effect B", "low": 0.1, "estimate": 1.2, "high": 2.4},
        {"name": "Effect C", "low": -1.8, "estimate": -0.5, "high": 0.7},
        {"name": "Effect D", "low": 0.3, "estimate": 0.9, "high": 1.5},
    ]
    return


app._unparsable_cell(
    r"""
    forest = mo.ui.anywidget(
        EvidentialTable(
            estimates,
            settings=settings(
                title="Estimates",
                subtitle="Point with an interval",
                row_lines=False,
                border=False,
                stretch=True, width=600
            ),
            columns=[
                col.text("name"),
                col.range("low", "high", cap="line", color="#94a3b8", title="Estimate", align="center")
                   .point("estimate", color="#1d4ed8", size=8)
                 # .reference_line(0, label="No effect"),
                col.numeric("low")
            ],
        )
    )
    forest
    """,
    name="_"
)


@app.cell
def _(mo):
    mo.md("""
    ## A stack and a categorical strip

    `col.stacked_bar(...)` is a distinct encoding: segment coordinates are
    cumulative. `normalize="percent"` divides each row by its own total.
    `col.strip(...)` encodes an ordered sequence of categories (form, states).
    """)
    return


@app.cell
def _():
    likert = [
        {"question": "Service", "strongly_disagree": 4, "disagree": 9, "neutral": 12, "agree": 41, "strongly_agree": 34},
        {"question": "Price", "strongly_disagree": 11, "disagree": 18, "neutral": 20, "agree": 36, "strongly_agree": 15},
        {"question": "Quality", "strongly_disagree": 3, "disagree": 6, "neutral": 10, "agree": 44, "strongly_agree": 37},
    ]
    form = [
        {"team": "A", "form": ["W", "W", "D", "L", "W"]},
        {"team": "B", "form": ["L", "D", "L", "W", "D"]},
        {"team": "C", "form": ["W", "L", "W", "W", "W"]},
    ]
    return form, likert


@app.cell
def _(EvidentialTable, col, likert, mo, settings):
    blocks = mo.ui.anywidget(
        EvidentialTable(
            likert,
            settings=settings(
                title="How do you feel about…?",
                caption="Illustrative survey data.",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("question"),
                col.stacked_bar(
                    "strongly_disagree",
                    "disagree",
                    "neutral",
                    "agree",
                    "strongly_agree",
                    colors=["#b91c1c", "#fca5a5", "#e5e7eb", "#86efac", "#16a34a"],
                    labels=True,
                    label_align="begin",
                    normalize="percent",
                    diverge_at="neutral",
                    neutral="split",
                    title="Response",
                ),
            ],
        )
    )
    blocks
    return


@app.cell
def _(EvidentialTable, col, form, mo, settings):
    strips = mo.ui.anywidget(
        EvidentialTable(
            form,
            settings=settings(
                title="Recent form",
                row_lines=False,
                border=False,
                stretch=False,
                width="420px",
            ),
            columns=[
                col.text("team"),
                col.strip(
                    "form",
                    colors={"W": "#16a34a", "D": "#9ca3af", "L": "#dc2626"},
                    labels=True,
                ).title("Form"),
            ],
        )
    )
    strips
    return


@app.cell
def _(mo):
    mo.md("""
    ## A log-scale forest plot

    `scale(domain=(0.1, 10), transform="log")` gives the marks one logarithmic
    axis; `.reference_line(1)` is the null effect and `.reference_band(0.8,
    1.25)` shades an equivalence zone. `cap="arrow"` marks an
    endpoint that extends beyond the shown scale instead of clipping it.
    """)
    return


@app.cell
def _():
    effects = [
        {"study": "A", "low": 0.3, "estimate": 1.4, "high": 6.2},
        {"study": "B", "low": 0.8, "estimate": 1.1, "high": 1.5},
        {"study": "C", "low": 0.05, "estimate": 0.6, "high": 2.1},
        {"study": "D", "low": 1.2, "estimate": 3.4, "high": 24.0},
    ]
    return (effects,)


@app.cell
def _(EvidentialTable, col, effects, mo, settings):
    forest_log = mo.ui.anywidget(
        EvidentialTable(
            effects,
            settings=settings(
                title="Odds ratios",
                subtitle="Log scale with the null effect at 1",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("study"),
                col.range("low", "high", cap="arrow", color="#94a3b8")
                .point("estimate", color="#1d4ed8", size=8)
                .scale(domain=(0.1, 10), transform="log")
                .reference_band(0.8, 1.25, label="equivalence")
                .reference_line(1, label="null"),
            ],
        )
    )
    forest_log
    return


@app.cell
def _(mo):
    mo.md("""
    ## A distribution band

    `col.distribution("density", x=, y=)` fills a precomputed density curve — a
    band of uncertainty. Combine it with a point on the same axis.
    """)
    return


@app.cell
def _():
    curves = [
        {
            "party": "A",
            "median": 52,
            "density": [
                {"x": p, "y": y}
                for p, y in ((40, 0.02), (48, 0.6), (52, 0.9), (58, 0.5), (66, 0.05))
            ],
        },
        {
            "party": "B",
            "median": 44,
            "density": [
                {"x": p, "y": y}
                for p, y in ((30, 0.05), (40, 0.5), (44, 0.8), (50, 0.5), (58, 0.05))
            ],
        },
    ]
    return (curves,)


@app.cell
def _(EvidentialTable, col, curves, mo, settings):
    bands = mo.ui.anywidget(
        EvidentialTable(
            curves,
            settings=settings(
                title="Share of the vote",
                subtitle="Density band with a median marker",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("party"),
                col.distribution("density", x="x", y="y", color="#8b5cf6")
                .point("median", color="#4c1d95", size=7)
                .scale(domain=(28, 68)),
            ],
        )
    )
    bands
    return


@app.cell
def _(mo):
    mo.md("""
    ## Adjacent bars with `valign`

    When bars should sit side by side rather than overlaid, place one at the top
    of the cell and one at the bottom with `valign=` and sizes that do not
    collide. The marks still share one horizontal scale.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, polling, settings):
    adjacent = mo.ui.anywidget(
        EvidentialTable(
            polling,
            settings=settings(
                title="Polling",
                subtitle="Last election above, this poll below",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("party"),
                col.bar("previous", color="#cbd5e1", size=0.36, valign="top")
                .bar("votes", color="@colour", size=0.36, valign="bottom")
                .scale(domain=(0, 45)),
            ],
        )
    )
    adjacent
    return


@app.cell
def _(mo):
    mo.md("""
    ## A strip of observations

    `col.points("observations", ...)` draws one marker per value in an array
    column, on the same scale as a bar or target — a compact strip/scatter for
    the row's distribution.
    """)
    return


@app.cell
def _():
    wards = [
        {"ward": "North", "mean": 48, "observations": [42, 45, 47, 49, 52, 55]},
        {"ward": "South", "mean": 44, "observations": [39, 41, 43, 44, 47, 50]},
        {"ward": "East", "mean": 52, "observations": [46, 49, 51, 53, 57, 61]},
        {"ward": "West", "mean": 46, "observations": [38, 42, 46, 48, 51, 56]},
    ]
    return (wards,)


@app.cell
def _(EvidentialTable, col, mo, settings, wards):
    observations_table = mo.ui.anywidget(
        EvidentialTable(
            wards,
            settings=settings(
                title="Waiting times by ward",
                subtitle="Mean as a bar, every observation as a point",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("ward"),
                col.bar("mean", color="#bfdbfe", title="Mean")
                .points("observations", size=6, color="#1d4ed860"),
            ],
        )
    )
    observations_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## A forecast band

    `range(..., fill=True)` draws the interval as a translucent band — an
    uncertainty or forecast range — behind a point estimate, instead of a line.
    """)
    return


@app.cell
def _():
    forecast = [
        {"month": "Jan", "low": 88, "estimate": 96, "high": 108},
        {"month": "Feb", "low": 92, "estimate": 101, "high": 115},
        {"month": "Mar", "low": 99, "estimate": 110, "high": 126},
        {"month": "Apr", "low": 106, "estimate": 118, "high": 135},
    ]
    return (forecast,)


@app.cell
def _(EvidentialTable, col, forecast, mo, settings):
    band = mo.ui.anywidget(
        EvidentialTable(
            forecast,
            settings=settings(
                title="Forecast",
                subtitle="A filled range with a point estimate",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("month"),
                col.range("low", "high", fill=True, color="#a5b4fc")
                .point("estimate", color="#4338ca", size=8)
                .scale(domain=(80, 140)),
            ],
        )
    )
    band
    return


@app.cell
def _(mo):
    mo.md("""
    ## A box plot from precomputed statistics

    `col.boxplot(minimum, q1, median, q3, maximum, outliers=)` draws a
    five-number summary. It never computes the statistics — they arrive from SQL
    or Python, and `whisker="iqr"` records that the whiskers are 1.5×IQR rather
    than the data extrema.
    """)
    return


@app.cell
def _():
    spread = [
        {"group": "Control", "lo": 4, "q1": 8, "med": 11, "q3": 15, "hi": 21, "outs": [25, 2]},
        {"group": "Treatment A", "lo": 7, "q1": 12, "med": 16, "q3": 20, "hi": 27, "outs": [31]},
        {"group": "Treatment B", "lo": 5, "q1": 9, "med": 12, "q3": 18, "hi": 24, "outs": []},
    ]
    return (spread,)


@app.cell
def _(EvidentialTable, col, mo, settings, spread):
    boxes = mo.ui.anywidget(
        EvidentialTable(
            spread,
            settings=settings(
                title="Distribution by group",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("group"),
                col.boxplot("lo", "q1", "med", "q3", "hi", outliers="outs", whisker="iqr", title="Spread"),
            ],
        )
    )
    boxes
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - A mark source can be a field name, `"@field"`, or `lambda row: ...`. A
      callable is evaluated Python-side into a hidden helper column, so the
      browser (and any static export) only ever sees field names.
    - `.label(...)` annotates the **most recently declared** mark; `label=True`
      labels the mark's own value and `label="@field"` names another field.
    - `.scale(domain=(lo, hi))` fixes the shared axis and `.reference_line(v)`
      adds a column-wide rule.
    - A single plain bar still serialises to the classic `viz="bar"` shape, so
      existing notebooks are unchanged.
    """)
    return


if __name__ == "__main__":
    app.run()
