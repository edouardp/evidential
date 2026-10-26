# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential", "scipy>=1.17.1"]
# ///
"""One named cell per graphic example in the README gallery.

Run ``make readme`` to start this notebook headlessly and capture each
cell's table into ``docs/img/graphics/`` with Playwright.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path

    import marimo as mo

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

    return EvidentialTable, Path, col, frame, json, label, mo, stats


@app.cell(hide_code=True)
def graphic_bar_doc(mo):
    mo.md(r"""
    #### Bar

    Labels prefer the outside end, moving inside when space is tight.
    """)
    return


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
            col.bar("sales", format="usd0", label=label.auto_position("outside end")),
        ],
        settings=frame("Bar", 520),
    )
    return


@app.cell(hide_code=True)
def graphic_bar_centered_doc(mo):
    mo.md(r"""
    #### Centered bar

    Positive and negative values extend from zero on a shared scale. Negative
    bars are red.
    """)
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
            col.bar("change", center=True, color_negative="red", format="pct1", label=True).scale(
                domain=(-0.2, 0.2), axis=True, axis_position="bottom"
            ),
        ],
        settings=frame("Centered bar", 540),
    )
    return


@app.cell(hide_code=True)
def graphic_bar_overlay_doc(mo):
    mo.md(r"""
    #### Overlaid bars with a target

    Layer the current value over the previous value, then mark the target.
    """)
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


@app.cell(hide_code=True)
def graphic_bar_back_to_back_doc(mo):
    mo.md(r"""
    #### Back-to-back bars

    Compare imports and exports of goods and services in current US dollars for
    the six largest European traders in 2024, including the UK. Countries are
    ranked by imports plus exports. Both sides use the same scale; labels use
    compact units (B = billion, T = trillion).

    Source: World Bank WDI (`NE.IMP.GNFS.CD` and `NE.EXP.GNFS.CD`).
    """)
    return


@app.cell
def graphic_bar_back_to_back(EvidentialTable, Path, col, frame, json, label):
    _rows = json.loads(
        (Path(__file__).parent / "data/50_europe_trade_2024.json").read_text()
    )
    EvidentialTable(
        _rows,
        columns=[
            col.bar(
                "imports",
                format="compact",
                direction="left",
                color="#2563eb",
                label=label.auto_position("outside end"),
                pad=3,
            ).domain("trade").align("left"),
            col.text("country", title="").align("center"),
            col.bar(
                "exports",
                format="compact",
                color="#0f766e",
                label=label.auto_position("outside end"),
                pad=3,
            ).domain("trade"),
        ],
        settings=frame("Imports and exports · 2024", 720,
            caption="Source: World Bank WDI · Goods and services, current US$ · B = billion, T = trillion"),
    )
    return


@app.cell(hide_code=True)
def graphic_dumbbell_doc(mo):
    mo.md(r"""
    #### Dumbbell: range plus points

    Connect two values, colour decreases red and add a direction chevron.
    """)
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


@app.cell(hide_code=True)
def graphic_points_doc(mo):
    mo.md(r"""
    #### Points from an array

    Plot every sample on one horizontal scale, with transparent marks for overlap.
    """)
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
            col.points("samples", color="#2563eb30", size=9, outline=False).scale(
                domain=(0, 60), axis=True, axis_position="bottom"
            ),
        ],
        settings=frame("Points from an array", 560),
    )
    return


@app.cell(hide_code=True)
def graphic_boxplot_doc(mo):
    mo.md(r"""
    #### Box plot

    Show quartiles, a median, whiskers and outliers.
    """)
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


@app.cell(hide_code=True)
def graphic_distribution_doc(mo):
    mo.md(r"""
    #### Distribution band

    Draw a density band with a median point.
    """)
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


@app.cell(hide_code=True)
def graphic_stacked_bar_doc(mo):
    mo.md(r"""
    #### Stacked bar

    Stack components and label them within the bar.
    """)
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


@app.cell(hide_code=True)
def graphic_stack_likert_doc(mo):
    mo.md(r"""
    #### Diverging Likert stack

    Split neutral responses around zero and label the normalised shares.
    """)
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


@app.cell(hide_code=True)
def graphic_strip_doc(mo):
    mo.md(r"""
    #### Strip

    Display an ordered sequence of categorical outcomes.
    """)
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
            col.strip("form", colors={"W": "#16a34a", "D": "#9ca3af", "L": "#dc2626"}, labels=True),
        ],
        settings=frame("Strip", 460),
    )
    return


@app.cell(hide_code=True)
def graphic_color_doc(mo):
    mo.md(r"""
    #### Color scale

    Encode the score as a background colour while keeping its numeric value.
    """)
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
            col.number("score", fmt="num0").color(scale="Blues", min=0, max=100),
        ],
        settings=frame("Colour scale", 500),
    )
    return


@app.cell(hide_code=True)
def graphic_chip_doc(mo):
    mo.md(r"""
    #### Chip

    Use chips for categories or a numeric colour scale.
    """)
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
            col.chip("status", min_width=84),
            col.number("latency", fmt="num0").chip(scale="red", min=0, max=500).title("Latency (ms)"),
        ],
        settings=frame("Chips", 540),
    )
    return


@app.cell(hide_code=True)
def graphic_delta_doc(mo):
    mo.md(r"""
    #### Delta

    Treat changes within the neutral range as steady, with optional chip backgrounds.
    """)
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
            col.percent("change", decimals=1).delta(down_is_good=False, neutral_range="-0.02:0.02"),
            col.percent("change", decimals=1, title="As a chip").delta(
                down_is_good=False, neutral_range="-0.02:0.02", chip=True
            ),
        ],
        settings=frame("Delta indicators", 540),
    )
    return


@app.cell(hide_code=True)
def graphic_sparklines_doc(mo):
    mo.md(r"""
    #### Sparklines

    Show a series as a line, area, bars, points or increase/steady/decrease marks.
    """)
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
            col.sparkline("line", type="line", width=110, height=30),
            col.sparkline("area", type="area", fit_to_data=True, width=110, height=30),
            col.sparkline("bar", type="bar", width=110, height=30),
            col.sparkline("points", type="points", width=110, height=30, markers=True),
            col.sparkline("change", type="change", width=110, height=30),
        ],
        settings=frame("Sparkline types", 900),
    )
    return


@app.cell(hide_code=True)
def graphic_football_form_doc(mo):
    mo.md(r"""
    #### Change sparkline: Premier League form

    A change sparkline can show match results: blue/up is a win, gray/centered
    is a draw, and red/down is a loss. Each rectangle has the same size;
    a larger winning margin does not make it taller. The sequence runs from
    oldest to newest across each team's last 12 league matches.

    These are the top six teams by league points earned in **calendar year
    2024**, with wins, draws and losses for that year—not season standings.
    The data comes from the football explorer in notebook 46, filtered to
    Premier League matches; international matches are excluded.
    """)
    return


@app.cell
def graphic_football_form(EvidentialTable, Path, col, frame, json):
    form_snapshot = json.loads(
        (Path(__file__).parent / "data/46_football_england_2024.json").read_text()
    )
    form_matches = [
        match for match in form_snapshot["matches"]
        if match["competition"] == "england" and match["level"] == "national"
    ]
    form_rows = []
    for form_team in sorted({match["team"] for match in form_matches}):
        form_games = sorted(
            (match for match in form_matches if match["team"] == form_team),
            key=lambda match: match["match_date"],
        )
        form_wins = sum(game["result"] == "Win" for game in form_games)
        form_draws = sum(game["result"] == "Draw" for game in form_games)
        form_rows.append({
            "team": form_team,
            "wins": form_wins,
            "draws": form_draws,
            "losses": sum(game["result"] == "Loss" for game in form_games),
            "points": 3 * form_wins + form_draws,
            "form": [
                {"date": f"{game['match_date']} · {game['opponent']}", "value": game["goal_margin"]}
                for game in form_games[-12:]
            ],
        })
    form_rows = sorted(form_rows, key=lambda team: (-team["points"], team["team"]))[:6]
    EvidentialTable(
        form_rows,
        columns=[
            col.text("team"),
            col.integer("wins"),
            col.integer("draws"),
            col.integer("losses"),
            col.sparkline("form", type="change", width=156, height=22, y_fmt="num0")
                .title("Last 12 matches"),
        ],
        settings=frame("Premier League form · 2024", 640,
            caption="Source: football-data / worldclubratings.com · Up = win, centered = draw, down = loss · Oldest → newest"),
    )
    return


@app.cell(hide_code=True)
def graphic_symbols_doc(mo):
    mo.md(r"""
    #### Symbols and rating

    Repeat glyphs or shapes for counts, or show a five-point rating.
    """)
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
            col.symbols("gold", symbol="●", color="#d97706", title="Circles"),
            col.symbols("gold", shape="square", color="#d97706", title="Squares").align("center"),
            col.rating("score", title="Rating"),
        ],
        settings=frame("Symbols and rating", 600),
    )
    return


@app.cell(hide_code=True)
def graphic_boolean_icons_doc(mo):
    mo.md(r"""
    #### Boolean, icons and flags

    Render booleans, mapped icons and country flags.
    """)
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
            col.boolean("active", true_symbol="✓", false_symbol="✗"),
            col.icons("signal", map={"up": "▲", "flat": "●", "down": "▼"}),
            col.flag("country"),
        ],
        settings=frame("Boolean, icons and flags", 540),
    )
    return


@app.cell(hide_code=True)
def graphic_reference_doc(mo):
    mo.md(r"""
    #### Axis, reference line and band

    Add an external axis, gridlines, a target line and a reference band.
    """)
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
            col.bar("score", format="num0", label=label.auto_position("outside end"))
            .scale(domain=(0, 100), axis=True, axis_position="bottom", gridlines=True)
            .reference_band(60, 80, color="#fef3c7")
            .reference_line(70, color="#dc2626"),
        ],
        settings=frame("Axis, reference line and band", 560, subtitle="Red line = target 70; band = 60–80."),
    )
    return


if __name__ == "__main__":
    app.run()
