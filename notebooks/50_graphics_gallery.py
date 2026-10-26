# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential", "scipy>=1.17.1"]
# ///
"""One named cell per graphic example in the README gallery.

Run ``make api-screenshots`` to start this notebook headlessly and capture each
cell's table into ``docs/img/graphics/`` with Playwright.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from evidential import EvidentialTable, col, label, settings

    from scipy import stats  # For random distributions

    def frame(title, width=560, **options):
        return settings(
            title=title,
            width=width,
            border=False,
            row_lines=False,
            page_size=0,
            search=False,
            row_shading=True,
            **options,
        )

    return EvidentialTable, col, frame, label, stats


@app.cell
def graphic_bar(EvidentialTable, col, frame, label):
    _rows = [
        {"region": "West", "sales": 412},
        {"region": "East", "sales": 287},
        {"region": "South", "sales": 141},
        {"region": "North", "sales": 98},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("region"),
            col.bar("sales", format="usd0", label=label.auto_position("outside end"), title="Sales"),
        ],
        settings=frame("Bar", 520),
    )
    return


@app.cell
def graphic_bar_centered(EvidentialTable, col, frame):
    _rows = [
        {"team": "National", "change": 0.12},
        {"team": "Labour", "change": -0.06},
        {"team": "Green", "change": 0.04},
        {"team": "ACT", "change": -0.02},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("team"),
            col.bar("change", center=True, format="pct1", label=True, title="Change").scale(
                domain=(-0.2, 0.2), axis=True, axis_position="bottom"
            ),
        ],
        settings=frame("Centered bar", 540),
    )
    return


@app.cell
def graphic_bar_overlay(EvidentialTable, col, frame, label):
    _rows = [
        {"party": "National", "previous": 41, "current": 38, "target": 40, "colour": "#2563eb"},
        {"party": "Labour", "previous": 31, "current": 34, "target": 31, "colour": "#dc2626"},
        {"party": "Green", "previous": 7, "current": 11, "target": 7, "colour": "#16a34a"},
        {"party": "ACT", "previous": 11, "current": 9, "target": 5, "colour": "#eab308"},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("party"),
            col.bar("previous", format="num0", color="#d1d5db", size=0.85)
            .bar("current", format="num0", color="@colour", size=0.45, label=label.position("inside end"), title="Current vs previous")
            .point("target", color="#0f766e", size=7)
            .scale(domain=(0, 45)),
        ],
        settings=frame("Overlaid bars + target", 560),
    )
    return


@app.cell
def graphic_bar_back_to_back(EvidentialTable, col, frame, label):
    _rows = [
        {"country": "Switzerland", "spend": 26.0, "rate": 1.52, "color": "#d9a01c"},
        {"country": "Australia", "spend": 18.2, "rate": 1.38, "color": "#3a9b9b"},
        {"country": "France", "spend": 12.5, "rate": 0.98, "color": "#d9a01c"},
        {"country": "Germany", "spend": 10.0, "rate": 0.55, "color": "#d9a01c"},
        {"country": "Ireland", "spend": 6.5, "rate": 0.40, "color": "#3a9b9b"},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.bar(
                "spend",
                format="usd1",
                direction="left",
                color="@color",
                label=label.auto_position("outside end"),
                pad=3,
                title="Sales per capita",
            ).align("left"),
            col.text("country", title=""),
            col.bar(
                "rate",
                format="num2",
                color="@color",
                label=label.auto_position("outside end"),
                pad=3,
                title="Foreign-to-Canadian rate",
            ).align("right"),
            col.auto("color").hide(),
        ],
        settings=frame("Back-to-back bars", 620),
    )
    return


@app.cell
def graphic_dumbbell(EvidentialTable, col, frame):
    _rows = [
        {"country": "Finland", "before": 29, "after": 94},
        {"country": "Sweden", "before": 76, "after": 41},
        {"country": "Norway", "before": 27, "after": 47},
        {"country": "Denmark", "before": 15, "after": 19},
        {"country": "Iceland", "before": 10, "after": 20},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("country"),
            col.range("before", "after", color="#222222", color_negative="#cc1111", size=2, direction_marker=True)
            .point("before", color="#6699ee", outline="#2f5fa8", size=12)
            .point("after", color="#ff6666", outline="#cc1111", size=12)
            .title("Before → after")
            .align("center")
            .scale(domain=(0, 100), axis=True, axis_position="bottom"),
        ],
        settings=frame("Dumbbell: range + points", 560),
    )
    return


@app.cell
def graphic_points(EvidentialTable, col, frame, stats):
    _rows = [
        {"metric": "API latency", "samples": [x for x in stats.norm.rvs(loc=30, scale=10, size=100, random_state=42)]},
        {"metric": "Render time", "samples": [x for x in stats.logistic.rvs(loc=20, scale=8, size=100, random_state=42)]},
        {"metric": "Queue wait", "samples": [x*40 for x in stats.beta.rvs(a=3, b=3, size=100, random_state=42)]},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("metric"),
            col.points("samples", color="#2563eb30", size=9, outline=False, title="Samples").scale(
                domain=(0, 60), axis=True, axis_position="bottom"
            ),
        ],
        settings=frame("Points from an array", 560),
    )
    return


@app.cell
def graphic_boxplot(EvidentialTable, col, frame):
    _rows = [
        {"group": "Control", "lo": 4, "q1": 8, "med": 11, "q3": 15, "hi": 21, "outs": [25, 2]},
        {"group": "Treatment A", "lo": 7, "q1": 12, "med": 16, "q3": 20, "hi": 27, "outs": [31]},
        {"group": "Treatment B", "lo": 5, "q1": 9, "med": 12, "q3": 18, "hi": 24, "outs": []},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("group"),
            col.boxplot("lo", "q1", "med", "q3", "hi", outliers="outs", whisker="iqr", title="Spread").scale(
                domain=(0, 32), axis=True, axis_position="bottom"
            ),
        ],
        settings=frame("Box plot", 560),
    )
    return


@app.cell
def graphic_distribution(EvidentialTable, col, frame):
    _rows = [
        {
            "name": "Symmetric",
            "median": 50,
            "ink": "#4169a0",
            "curve": [{"x": x, "pdf": y} for x, y in [(0, 0), (25, 0.5), (50, 1), (75, 0.5), (100, 0)]],
        },
        {
            "name": "Right-skewed",
            "median": 70,
            "ink": "#ad3038",
            "curve": [{"x": x, "pdf": y} for x, y in [(0, 0), (30, 0.2), (50, 0.5), (70, 1), (100, 0)]],
        },
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("name"),
            col.distribution("curve", x="x", y="pdf", color="@ink")
            .point("median", color="#111111", outline=False)
            .title("Density")
            .align("center")
            .scale(domain=(0, 100), axis=True, axis_position="bottom"),
        ],
        settings=frame("Distribution band", 560),
    )
    return


@app.cell
def graphic_stacked_bar(EvidentialTable, col, frame):
    _rows = [
        {"region": "Americas", "new": 42, "renewal": 61, "expansion": 18},
        {"region": "EMEA", "new": 30, "renewal": 74, "expansion": 22},
        {"region": "APAC", "new": 26, "renewal": 48, "expansion": 31},
        {"region": "LATAM", "new": 12, "renewal": 21, "expansion": 9},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("region"),
            col.stacked_bar(
                "new",
                "renewal",
                "expansion",
                colors=["#2563eb", "#60a5fa", "#bfdbfe"],
                labels=True,
                format="num0",
                size=0.6,
                title="New · Renewal · Expansion",
            ),
        ],
        settings=frame("Stacked bar", 580),
    )
    return


@app.cell
def graphic_stack_likert(EvidentialTable, col, frame):
    _rows = [
        {"question": "Ease of use", "sd": 4, "d": 9, "n": 12, "a": 41, "sa": 34},
        {"question": "Value for money", "sd": 11, "d": 18, "n": 20, "a": 36, "sa": 15},
        {"question": "Support", "sd": 3, "d": 6, "n": 10, "a": 44, "sa": 37},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("question"),
            col.stacked_bar(
                "sd",
                "d",
                "n",
                "a",
                "sa",
                colors=["#b91c1c", "#fca5a5", "#e5e7eb", "#86efac", "#16a34a"],
                labels="percent",
                label_align="begin",
                diverge_at="n",
                neutral="split",
                normalize="percent",
                size=1,
                title="Response",
            ),
        ],
        settings=frame("Diverging (Likert) stack", 600),
    )
    return


@app.cell
def graphic_strip(EvidentialTable, col, frame):
    _rows = [
        {"team": "A", "form": ["W", "W", "D", "L", "W"]},
        {"team": "B", "form": ["L", "D", "L", "W", "D"]},
        {"team": "C", "form": ["W", "L", "W", "W", "W"]},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("team"),
            col.strip("form", colors={"W": "#16a34a", "D": "#9ca3af", "L": "#dc2626"}, labels=True).title("Form"),
        ],
        settings=frame("Strip", 460),
    )
    return


@app.cell
def graphic_color(EvidentialTable, col, frame):
    _rows = [
        {"region": "North", "score": 18},
        {"region": "South", "score": 46},
        {"region": "East", "score": 73},
        {"region": "West", "score": 94},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("region"),
            col.number("score", fmt="num0").color(scale="Blues", min=0, max=100).title("Score"),
        ],
        settings=frame("Colour scale", 500),
    )
    return


@app.cell
def graphic_chip(EvidentialTable, col, frame):
    _rows = [
        {"service": "Search", "status": "Healthy", "latency": 84},
        {"service": "Checkout", "status": "Degraded", "latency": 210},
        {"service": "Reports", "status": "Healthy", "latency": 132},
        {"service": "Uploads", "status": "Down", "latency": 480},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("service"),
            col.chip("status", min_width=84, title="Status"),
            col.number("latency", fmt="num0").chip(scale="red", min=0, max=500).title("Latency (ms)"),
        ],
        settings=frame("Chips", 540),
    )
    return


@app.cell
def graphic_delta(EvidentialTable, col, frame):
    _rows = [
        {"metric": "Revenue", "change": 0.12},
        {"metric": "Costs", "change": -0.04},
        {"metric": "Margin", "change": 0.00},
        {"metric": "Headcount", "change": 0.06},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("metric"),
            col.percent("change", decimals=1, title="Change").delta(down_is_good=False, neutral_range="-0.02:0.02"),
            col.percent("change", decimals=1, title="As a chip").delta(
                down_is_good=False, neutral_range="-0.02:0.02", chip=True
            ),
        ],
        settings=frame("Delta indicators", 540),
    )
    return


@app.cell
def graphic_sparklines(EvidentialTable, col, frame):
    _rows = [
        {
            "series": "Product A",
            "line": [3, 5, 4, 7, 9, 8, 12],
            "area": [3, 5, 4, 7, 9, 8, 12],
            "bar": [3, 5, 4, 7, 9, 8, 12],
            "points": [3, 5, 4, 7, 9, 8, 12],
            "change": [1, 0, -1, 2, 0, 1, -2],
        },
        {
            "series": "Product B",
            "line": [9, 8, 7, 7, 5, 6, 4],
            "area": [9, 8, 7, 7, 5, 6, 4],
            "bar": [9, 8, 7, 7, 5, 6, 4],
            "points": [9, 8, 7, 7, 5, 6, 4],
            "change": [-1, 1, 0, -1, 0, -2, 1],
        },
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("series"),
            col.sparkline("line", type="line", width=110, height=30, title="Line"),
            col.sparkline("area", type="area", fit_to_data=True, width=110, height=30, title="Area"),
            col.sparkline("bar", type="bar", width=110, height=30, title="Bar"),
            col.sparkline("points", type="points", width=110, height=30, markers=True, title="Points"),
            col.sparkline("change", type="change", width=110, height=30, title="Change"),
        ],
        settings=frame("Sparkline types", 900),
    )
    return


@app.cell
def graphic_symbols(EvidentialTable, col, frame):
    _rows = [
        {"country": "Ireland", "gold": 4, "score": 3},
        {"country": "Cyprus", "gold": 3, "score": 2},
        {"country": "France", "gold": 2, "score": 4},
        {"country": "Sweden", "gold": 2, "score": 1},
        {"country": "Slovenia", "gold": 1, "score": 5},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("country"),
            col.symbols("gold", symbol="■", color="#d97706", title="Glyph"),
            col.symbols("gold", shape="square", color="#d97706", title="Squares"),
            col.rating("score", title="Rating"),
        ],
        settings=frame("Symbols and rating", 600),
    )
    return


@app.cell
def graphic_boolean_icons(EvidentialTable, col, frame):
    _rows = [
        {"feature": "Search", "active": True, "signal": "up", "country": "USA"},
        {"feature": "Exports", "active": True, "signal": "flat", "country": "DEU"},
        {"feature": "Beta API", "active": False, "signal": "down", "country": "JPN"},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("feature"),
            col.boolean("active", true_symbol="✓", false_symbol="✗", title="Active"),
            col.icons("signal", map={"up": "▲", "flat": "●", "down": "▼"}, title="Signal"),
            col.flag("country", title="Country"),
        ],
        settings=frame("Boolean, icons and flags", 540),
    )
    return


@app.cell
def graphic_reference(EvidentialTable, col, frame, label):
    _rows = [
        {"team": "Alpha", "score": 64},
        {"team": "Beta", "score": 72},
        {"team": "Gamma", "score": 81},
        {"team": "Delta", "score": 91},
    ]
    EvidentialTable(
        _rows,
        columns=[
            col.text("team"),
            col.bar("score", format="num0", label=label.auto_position("outside end"), title="Score")
            .scale(domain=(0, 100), axis=True, axis_position="bottom", gridlines=True)
            .reference_band(60, 80, color="#fef3c7")
            .reference_line(70, color="#dc2626"),
        ],
        settings=frame("Axis, reference line and band", 560, subtitle="Red line = target 70; band = 60–80."),
    )
    return


if __name__ == "__main__":
    app.run()
