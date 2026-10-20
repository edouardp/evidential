# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Centred ("diverging") bars — labeled `col.bar()` marks on symmetric scales.

A zero centre line, the bar growing left (negative) or right (positive) by its
magnitude, and the value at its outer tip: the shape The
Economist uses for its league-table-of-nations charts. The same module also
shows the **back-to-back** ("tornado") variant — mirrored bars meeting at a
shared centre (using a negative source), with an optional benchmark rule — and a
recreation of Pew Research Center's tolerance-vs-intolerance chart.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, cells_body, col, settings, tab_style

    return EvidentialTable, cells_body, col, mo, settings, tab_style


@app.cell
def _(mo):
    mo.md("""
    # Centred (diverging) bars

    Use **`col.bar()`** with a symmetric scale and a zero reference line: the bar
    grows **right** for a positive value and
    **left** for a negative one, by how far the value sits from zero, and the value
    is labeled at the **outer tip** of the bar.

    ```python
    (
        col.bar("gdp", color="#01A9C3", size=0.65)
        .label(value=True, format="num1")
        .scale(domain=(-30, 30))
        .reference_line(0, color="#94a3b8")
    )
    ```

    Equal positive and negative values draw the same length. The examples leave
    space beyond the largest bar for its label. Colour follows the usual rule
    (`color`, `color_negative`).

    The data below is **illustrative**, in the style of The Economist's league
    table of nations.
    """)
    return


@app.cell
def _():
    leagues = [
        {"country": "**Denmark** (1)", "gdp": 2.1, "income": 3.4, "prices": 57.3, "investment": 12.1, "debt": 3.5},
        {"country": "**Chile** (5)", "gdp": 10.4, "income": 32.7, "prices": -5.6, "investment": 6.7, "debt": 11.9},
        {"country": "**Ireland** (=6)", "gdp": 22.3, "income": 4.8, "prices": 17.1, "investment": -78.8, "debt": 0.9},
        {
            "country": "**United States** (9)",
            "gdp": 1.4,
            "income": 6.2,
            "prices": 24.4,
            "investment": 3.6,
            "debt": 18.9,
        },
        {"country": "**Australia** (=10)", "gdp": -0.2, "income": 3.5, "prices": 9.1, "investment": 7.4, "debt": 10.2},
        {"country": "**Canada** (=10)", "gdp": -1.4, "income": 9.4, "prices": 25.9, "investment": 0.7, "debt": 11.6},
        {"country": "**France** (=15)", "gdp": -0.1, "income": 0.7, "prices": 17.4, "investment": 1.3, "debt": 14.4},
        {"country": "**Portugal** (=17)", "gdp": -3.2, "income": -0.3, "prices": 27.1, "investment": 0.5, "debt": 12.0},
        {"country": "**Germany** (20)", "gdp": -1.1, "income": -0.9, "prices": 15.6, "investment": -1.9, "debt": 13.6},
        {"country": "**Spain** (23)", "gdp": -6.6, "income": -6.3, "prices": -7.2, "investment": -6.5, "debt": 22.3},
    ]
    league_limits = {
        field: 1.4 * max(abs(row[field]) for row in leagues)
        for field in ("gdp", "income", "prices", "investment", "debt")
    }
    league_domains = {field: (-limit, limit) for field, limit in league_limits.items()}
    return league_domains, leagues


@app.cell
def _(
    EvidentialTable,
    cells_body,
    col,
    league_domains,
    leagues,
    mo,
    settings,
    tab_style,
):
    league_table = mo.ui.anywidget(
        EvidentialTable(
            leagues,
            settings=settings(
                title="League table of nations",
                subtitle="Selected OECD countries, % change during the covid-19 pandemic*",
                caption="Illustrative data, in the style of The Economist.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                # a small table reads better a step above the dense baseline
                font_size="+1",
            ),
            columns=[
                col.markdown("country"),
                col.bar("gdp", color="#01A9C3", align="center")
                .label(value=True, format="num1")
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
                col.bar("income", title="Household income\nper person", color="#086FA1", align="center")
                .label(value=True, format="num1")
                .scale(domain=league_domains["income"])
                .reference_line(0, color="#94a3b8"),
                col.bar("prices", title="Share prices", color="#8BB9CE",  align="center")
                .label(value=True, format="num1")
                .scale(domain=league_domains["prices"])
                .reference_line(0, color="#94a3b8"),
                col.bar("investment", color="#559CB8", align="center")
                .label(value=True, format="num1")
                .scale(domain=league_domains["investment"])
                .reference_line(0, color="#94a3b8"),
                col.bar("debt", title="Public debt\nto GDP", color="#2EC1D3", align="center")
                .label(value=True, format="num1")
                .scale(domain=league_domains["debt"])
                .reference_line(0, color="#94a3b8"),
            ],
            rules=[tab_style(cells_body(columns=list(league_domains)), min_width="150px")],
        )
    )
    league_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Options

    The same column, three ways. `.label(value=True)` adds the value; omitting
    it shows the bar alone. `color`/`color_negative` set one colour for both signs
    (or two). `size=0.65` uses 65% of the row height, leaving space above and below
    the bar; the zero reference line stays continuous. `.scale(domain=...)`
    controls the range shared by the marks and the reference line.

    Colours accept matplotlib's names too — `tab:blue`, `C0`–`C9`, `k`, … — as the
    third column shows (`tab:blue` with `size=0.5`).
    """)
    return


@app.cell
def _(EvidentialTable, col, league_domains, leagues, mo, settings):
    variants = mo.ui.anywidget(
        EvidentialTable(
            leagues,
            settings=settings(
                title="The same % change, three ways",
                row_shading=True,
                row_lines=False,
                # border=False,
                # stretch=False,
                width="760px",
            ),
            columns=[
                col.text("country"),
                col.bar("gdp", title="With values", color="blue", color_negative="red", size=0.65)
                .label(value=True, format='0.0"%"')
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
                col.bar("gdp", title="Bar only", color="blue", color_negative="red", size=0.65)
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
                col.bar("gdp", title="tab:blue, size=0.5", color="tab:blue", size=0.5)
                .label(value=True, format='0.0"%"')
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
            ],
        )
    )
    variants
    return


@app.cell
def _(mo):
    mo.md("""
    ## Back-to-back bars and a benchmark rule

    A negative source with a scale ending at zero fills a bar from the **right**
    edge, growing left — the mirror of the default. A callable supplies that
    drawing coordinate while `.label(source="spend")` displays the original
    positive value. Put one of each either side of a label column and you
    get a **back-to-back** ("tornado") league table, the shape The Economist uses
    for its drug-price tables.

    `.reference_line(value)` draws a benchmark on the shared scale, such as the
    OECD median. The mirrored panel uses a negative coordinate for its benchmark
    too. `color="@column"` takes each bar's colour from a column, so the same
    colour keys both panels.
    """)
    return


@app.cell
def _():
    # Values transcribed from The Economist's "Foreign-to-Canadian rate of
    # consumption per capita per drug", fig. 2-3e.
    _rows = [
        ("Switzerland", 26.0, 1.52, "7"),
        ("Canada", 19.1, 1.00, "6"),
        ("Australia", 18.2, 1.38, "5"),
        ("United Kingdom", 13.3, 1.00, "7"),
        ("France", 12.5, 0.98, "7"),
        ("Germany", 10.0, 0.55, "7"),
        ("Slovenia", 9.6, 0.96, "5"),
        ("Belgium", 9.0, 0.66, "5"),
        ("Sweden", 7.4, 0.79, "7"),
        ("Ireland", 6.5, 0.40, "5"),
        ("United States", 6.1, 0.15, "7"),
        ("Japan", 6.0, 0.38, "5"),
        ("Slovakia", 6.0, 0.46, "5"),
        ("Finland", 4.5, 0.35, "5"),
        ("Norway", 4.3, 0.35, "5"),
        ("Netherlands", 4.0, 0.32, "5"),
        ("Spain", 3.9, 0.23, "5"),
        ("Italy", 3.8, 0.28, "7"),
        ("Austria", 1.8, 0.14, "5"),
        ("Portugal", 1.7, 0.13, "5"),
        ("Turkey", 1.2, 0.24, "5"),
        ("Hungary", 1.0, 0.06, "5"),
        ("South Korea", 1.0, 0.10, "5"),
        ("Poland", 1.0, 0.09, "5"),
        ("New Zealand", 0.9, 0.03, "5"),
        ("Estonia", 0.2, 0.02, "5"),
    ]
    _category = {"5": "#3a9b9b", "6": "#b23a2e", "7": "#d9a01c"}
    price_table = [{"country": c, "spend": s, "rate": r, "color": _category[k]} for c, s, r, k in _rows]
    return (price_table,)


@app.cell
def _(EvidentialTable, cells_body, col, mo, price_table, settings, tab_style):
    back_to_back = mo.ui.anywidget(
        EvidentialTable(
            price_table,
            settings=settings(
                title="Back-to-back league table",
                subtitle="Mirrored bars either side of a label, one benchmark rule per panel",
                caption=(
                    "Illustrative data, in the style of The Economist. Bar colour marks the drug's review category. "
                    "Reference lines: OECD medians of CAD 4.3 per capita and a consumption ratio of 0.32."
                ),
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                width="820px",
            ),
            columns=[
                col.bar(lambda row: -row["spend"], title="Sales per capita (CAD)", color="@color", size=0.65)
                .label(source="spend", format="usd1")
                .scale(domain=(-34, 0))
                .reference_line(-4.3, color="#94a3b8"),
                col.text("country", title="", align="center"),
                col.bar("rate", title="Foreign-to-Canadian rate", color="@color", size=0.65)
                .label(value=True, format="num2")
                .scale(domain=(0, 2))
                .reference_line(0.32, color="#94a3b8"),
                col.auto("color").hide(),
            ],
            rules=[tab_style(cells_body(), min_width="180px")],
        )
    )
    back_to_back
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - Symmetric domains put zero at the middle of each column. Bars grow from
      zero, and `.reference_line(0)` makes that origin visible.
    - A callable can reverse a bar's coordinate without modifying the input
      data. Its label can still use the original field and its own format.
    - Labels belong to marks: `.label(value=True, format="num1")` labels the
      bar's value; `.label(source="spend", format="usd1")` labels another field.
    - `size` controls bar height; `.scale()` and `.reference_line()` control
      the shared coordinates. `color="@column"` colours each bar from a column.
    - `font_size` raises or lowers the whole table from the shared baseline: a
      CSS length (`"14px"`) sets it absolutely, a step (`"+1"`, `"-1"`) adds
      that many 1px steps. This table uses `font_size="+1"`.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Diverging bars: tolerance vs intolerance

    A survey question with two complementary answers — the share who say religion
    encourages **tolerance** and the share who say it encourages **intolerance** —
    makes a natural back-to-back table. The orange tolerance bars grow **leftward**
    from the shared centre (using a negative drawing coordinate); the blue
    intolerance bars grow rightward. Each percentage sits at the **outer** tip,
    while its source data remains positive.

    The last row is a bold 22-country median, added with a `tab_style` rule.
    """)
    return


@app.cell
def _():
    # Pew Research Center, "Many Religious 'Nones' Around the World Hold
    # Spiritual Beliefs" (Spring 2024 Global Attitudes Survey).
    _survey = [
        ("Australia", 21, 76),
        ("Sweden", 20, 73),
        ("Germany", 23, 73),
        ("Spain", 22, 71),
        ("Netherlands", 25, 70),
        ("Greece", 28, 70),
        ("UK", 28, 70),
        ("Canada", 23, 68),
        ("U.S.", 32, 64),
        ("Italy", 33, 61),
        ("Chile", 29, 58),
        ("France", 37, 57),
        ("Hungary", 42, 49),
        ("Mexico", 46, 48),
        ("Argentina", 37, 46),
        ("South Korea", 41, 45),
        ("Brazil", 49, 45),
        ("Colombia", 50, 44),
        ("Peru", 53, 39),
        ("South Africa", 52, 31),
        ("Singapore", 68, 31),
        ("Japan", 54, 28),
        ("22-country\nmedian", 35, 58),
    ]
    attitudes = [{"country": c, "tolerance": t / 100, "intolerance": i / 100} for c, t, i in _survey]
    return (attitudes,)


@app.cell
def _(EvidentialTable, attitudes, cells_body, col, mo, settings, tab_style):
    diverging = mo.ui.anywidget(
        EvidentialTable(
            attitudes,
            settings=settings(
                title="Tolerance vs intolerance",
                subtitle="% of religiously unaffiliated adults who say religion encourages …",
                caption=("Illustrative data after Pew Research Center, Spring 2024 Global Attitudes Survey."),
                row_lines=False,
                border=False,
                #stretch=False,
                # width="720px",
            ),
            columns=[
                col.text("country", title="", align="right"),
                col.bar(lambda row: -row["tolerance"], title="Tolerance", color="#fea224", size=0.65)
                .label(source="tolerance", format="pct0")
                .scale(domain=(-1, 0))
                .reference_line(0, color="#94a3b8"),
                col.bar("intolerance", title="Intolerance", color="#1374a8", size=0.65)
                .label(value=True, format="pct0")
                .scale(domain=(0, 1))
                .reference_line(0, color="#94a3b8"),
            ],
            rules=[
                tab_style(
                    cells_body(
                        rows=lambda r: r["country"].startswith("22-country"),
                    ),
                    font_weight="700",
                ),
                tab_style(cells_body(), min_width="180px"),
            ],
        )
    )
    diverging
    return


if __name__ == "__main__":
    app.run()
