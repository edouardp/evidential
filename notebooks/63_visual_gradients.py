# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Review the same numeric gradient across mark types and their scale strips."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import math

    import marimo as mo

    from evidential import EvidentialTable, col, label, settings

    return EvidentialTable, col, label, math, mo, settings


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # One gradient, different visualizations

    This is a review notebook for the `shared-visual-gradients` branch.
    Every numeric visualization uses the same `.gradient(scale=, stops=, min=,
    max=, midpoint=)` arguments. **Points sample a solid colour at their value;
    spans paint the colours along their numeric axis.** That includes horizontal
    bars, ranges, boxes, density bands and vertical sparkline bars/areas.
    Sparkline points sample y; scalar marks sample x. Existing sparkline
    `.color(...)` declarations still work.

    `.scale(gradient=True)` adds a three-pixel colour strip across the full axis,
    outside the rows. It enables the axis automatically. The strip respects
    geometry bounds, log/reversed coordinates, colour bounds and transparent
    stops. With multiple gradient-configured marks it uses the last one.
    Solid marker overlays do not replace the strip's palette.

    Stacks and category strips keep their categorical colours. Gradient marks
    use the numeric scale strip rather than a categorical `.legend()` key.
    Repeated symbols, ratings and chips retain their existing colour interfaces.
    All values here are illustrative.
    """)
    return


@app.cell
def common_style(settings):
    colors = dict(scale=["#b91c1c", "#e5e7eb", "#1d4ed8"], min=-10, max=10, midpoint=0)
    frame = settings(border=False, row_lines=False, row_shading=True, search=False, page_size=0, width=960)
    return colors, frame


@app.cell
def scalar_marks(EvidentialTable, col, colors, frame, label, mo):
    samples = [
        {"case": "Negative", "bar": -8, "point": -8, "low": -10, "high": -6},
        {"case": "Across zero", "bar": -3, "point": -3, "low": -6, "high": 2},
        {"case": "Neutral", "bar": 0, "point": 0, "low": -2, "high": 2},
        {"case": "Positive", "bar": 4, "point": 4, "low": 1, "high": 7},
        {"case": "Clamped colour", "bar": 12, "point": 12, "low": 8, "high": 15},
        {"case": "Missing", "bar": None, "point": None, "low": None, "high": None},
    ]
    scalar_table = mo.ui.anywidget(EvidentialTable(
        samples,
        columns=[
            col.text("case"),
            col.bar("bar", center=True, label=label.fmt("num0").auto_position("outside end"))
            .gradient(**colors).scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
            col.point("point", shape="star", size=11, outline="#334155")
            .gradient(**colors).scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
            col.range("low", "high", cap="round", size=7).gradient(**colors)
            .title("Range").scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
        ],
        title="Bars, points and ranges agree on value colours",
        subtitle="Geometry spans −15…15; colours clamp outside −10…10",
        settings=frame,
    ))
    scalar_table
    return (scalar_table,)


@app.cell
def distribution_marks(EvidentialTable, col, colors, frame, math, mo):
    distribution_data = [
        {"case": name, "minimum": centre-4, "q1": centre-2, "median": centre,
         "q3": centre+2, "maximum": centre+4, "outliers": [-12, 12],
         "curve": [{"position": x / 2, "density": math.exp(-0.5 * ((x / 2 - centre) / 2)**2)}
                   for x in range(-20, 21)],
         "points": [centre-4, centre-2, centre, centre+2, centre+4]}
        for name, centre in [("Below", -5), ("Central", 0), ("Above", 5)]
    ]
    distribution_table = mo.ui.anywidget(EvidentialTable(
        distribution_data,
        columns=[
            col.text("case"),
            col.boxplot("minimum", "q1", "median", "q3", "maximum", outliers="outliers")
            .gradient(**colors).title("Box plot").scale(domain=(-10, 10), gradient=True),
            col.distribution("curve").gradient(**colors).title("Density band")
            .scale(domain=(-10, 10), gradient=True),
            col.points("points", shape="diamond", size=10, outline="#334155")
            .gradient(**colors).scale(domain=(-10, 10), gradient=True),
        ],
        title="Box plots, density bands and point arrays",
        caption="Density still controls opacity; the colour gradient does not change the supplied density curve.",
        settings=frame,
    ))
    distribution_table
    return (distribution_table,)


@app.cell
def miniatures(EvidentialTable, col, colors, frame, mo):
    miniature_table = mo.ui.anywidget(EvidentialTable(
        [{"case": "Rising", "last": 8, "history": [-8, -5, -2, 0, 4, 8]},
         {"case": "Falling", "last": -8, "history": [8, 5, 2, 0, -4, -8]},
         {"case": "Gaps", "last": 5, "history": [-5, None, -2, 2, None, 5]}],
        columns=[
            col.text("case"),
            col.number("last", format="num0").gradient(**colors),
            col.sparkline("history", type="bar", title="Bars").gradient(**colors),
            col.sparkline("history", type="points", shape="diamond", title="Points").gradient(**colors),
            col.sparkline("history", type="line", title="Line").gradient(**colors),
            col.sparkline("history", type="area", title="Area").gradient(**colors),
        ],
        title="The same gradient API for cells and sparklines",
        settings=frame,
    ))
    miniature_table
    return (miniature_table,)


@app.cell
def special_scales(EvidentialTable, col, frame, mo):
    transparent_stops = [
        {"value": -10, "color": "#b91c1c"}, {"value": 0, "color": "#ffffff00"},
        {"value": 10, "color": "#1d4ed8"},
    ]
    scales_table = mo.ui.anywidget(EvidentialTable(
        [{"case": "A", "forward": 8, "reverse": 8, "log": 10, "low": -10, "high": 10},
         {"case": "B", "forward": -8, "reverse": -8, "log": 60, "low": 10, "high": -10}],
        columns=[
            col.text("case"),
            col.bar("forward").gradient(stops=transparent_stops)
            .scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
            col.bar("reverse", direction="left").gradient(stops=transparent_stops)
            .scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
            col.range("low", "high", cap="round", size=7).gradient(stops=transparent_stops)
            .title("Reversed endpoints").scale(domain=(-15, 15), gradient=True, axis_position="bottom"),
            col.bar("log", fit_to_data=True).gradient(scale="viridis", min=1, max=100)
            .scale(domain=(1, 100), transform="log", gradient=True),
        ],
        title="Transparent stops, reversal and logarithmic geometry",
        settings=frame,
    ))
    scales_table
    return (scales_table,)


if __name__ == "__main__":
    app.run()
