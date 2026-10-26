# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Centred ("diverging") bars — labeled `col.bar()` marks on symmetric scales.

A zero centre line, the bar growing left (negative) or right (positive) by its
magnitude, and the value on the opposite side of zero: the shape The
Economist uses for its league-table-of-nations charts. The same module also
shows the **back-to-back** ("tornado") variant — mirrored bars meeting at a
shared centre (using a negative source), with an optional benchmark rule — and a
recreation of Pew Research Center's tolerance-vs-intolerance chart.

The first two tables query the local WDI Parquet bundle configured by
``WDI_PARQUET`` (default: ``~/datasets/WDI_CSV_2026_10_01/parquet``).
A saved real-data query result keeps the demo runnable without that bundle.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, cells_body, col, settings, tab_style

    return (
        EvidentialTable,
        Path,
        cells_body,
        col,
        duckdb,
        json,
        mo,
        os,
        settings,
        tab_style,
    )


@app.cell
def _(mo):
    mo.md("""
    # Centred (diverging) bars

    Use **`col.bar()`** with a symmetric scale and a zero reference line: the bar
    grows **right** for a positive value and
    **left** for a negative one, by how far the value sits from zero, and the value
    is labeled beside zero on the **opposite side** from the bar.

    ```python
    (
        col.bar("gdp", title="Real GDP", color="#01A9C3", size=0.65)
        .label(value=True, format="num1", position="outside_start")
        .scale(domain=(-30, 30))
        .reference_line(0, color="#94a3b8")
    )
    ```

    Equal positive and negative values draw the same length. The largest bar uses
    its full half of the cell; its label occupies the other half. Colour follows
    the usual rule (`color`, `color_negative`).

    The first two examples use **World Development Indicators** data for the
    pandemic comparison, in the style of The Economist's league table of nations.
    """)
    return


@app.cell
def _(Path, os):
    # Compare annual observations; edit these years to query another period.
    base_year, end_year = 2019, 2021
    wdi_path = Path(
        os.environ.get("WDI_PARQUET", "~/datasets/WDI_CSV_2026_10_01/parquet")
    ).expanduser()
    return base_year, end_year, wdi_path


@app.cell
def _(base_year, duckdb, end_year, json, mo, wdi_path):
    if end_year <= base_year:
        raise ValueError("The comparison year must be after the baseline year")
    wdi_sql = (mo.notebook_location() / "sql" / "34_wdi_league.sql").read_text()
    if (wdi_path / "wdi_observations").is_dir() and (wdi_path / "country.parquet").is_file():
        with duckdb.connect() as connection:
            result = connection.execute(
                wdi_sql,
                {
                    "observations": str(wdi_path / "wdi_observations/**/*.parquet"),
                    "countries": str(wdi_path / "country.parquet"),
                    "base_year": base_year,
                    "end_year": end_year,
                },
            )
            fields = [column[0] for column in result.description]
            leagues = [dict(zip(fields, record, strict=True)) for record in result.fetchall()]
        wdi_source = f"Queried local WDI bundle: `{wdi_path}`"
    else:
        snapshot = json.loads(
            (mo.notebook_location() / "data" / "34_wdi_league_2019_2021.json").read_text()
        )
        if (base_year, end_year) != (snapshot["base_year"], snapshot["end_year"]):
            raise ValueError("The saved WDI result covers only 2019–2021; set WDI_PARQUET to query other years")
        leagues = snapshot["records"]
        wdi_source = f"Bundle unavailable at `{wdi_path}`; displaying the saved WDI query result (2019–2021)."
    league_limits = {
        field: (max((abs(row[field]) for row in leagues if row[field] is not None), default=0) or 1)
        for field in ("gdp", "consumption", "prices", "investment", "debt")
    }
    league_domains = {field: (-limit, limit) for field, limit in league_limits.items()}
    return league_domains, leagues, wdi_source


@app.cell
def _(base_year, end_year, mo, wdi_source):
    mo.md(f"""
    ## WDI source and calculation

    {wdi_source}

    The baseline is **{base_year}** and the comparison year is **{end_year}**.
    Edit those years in the configuration cell, or set `WDI_PARQUET` to another
    copy of the long-format Parquet bundle used in notebook 23.

    | Column | WDI indicator | Calculation |
    | --- | --- | --- |
    | Real GDP | `NY.GDP.MKTP.KD` | Endpoint % change in constant-price GDP |
    | Real consumption per person | `NE.CON.PRVT.PC.KD` | Endpoint % change in constant-price household and NPISH consumption per person |
    | Equity prices (USD) | `CM.MKT.INDX.ZG` | Compound every annual return after the baseline, through the comparison year |
    | Real fixed investment | `NE.GDI.FTOT.KD` | Endpoint % change in constant-price gross fixed capital formation |
    | Central government debt | `GC.DOD.TOTL.GD.ZS` | Difference in debt/GDP, in percentage points |

    Consumption is **not household income**; central-government debt is a
    narrower measure than general-government debt. Missing endpoints or an
    incomplete sequence of equity returns remain missing. All WDI countries
    and territories are included; region and income-group
    aggregates are excluded. Countries with no observations remain in the table.

    **Rank** sums the available values across the five columns, including debt
    with its displayed sign, then rounds the total to the nearest whole point.
    Higher scores rank first. Equal rounded scores share a rank and get an `=`
    suffix (for example, `2=`); the following rank skips the tied places.
    Countries with no reported metrics have no score or rank and appear last.
    Countries sharing a score are ordered by name. These ranks use an unweighted
    sum of the displayed changes.

    Without a local bundle, the notebook uses a saved **real WDI query result**
    for 2019–2021. The drug-price and Pew examples below use their own sources.
    """)
    return


@app.cell
def _(
    EvidentialTable,
    base_year,
    cells_body,
    col,
    end_year,
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
                subtitle=f"WDI countries and territories, {base_year}→{end_year}; % change except debt (percentage points)",
                caption="Source: World Bank WDI. Missing observations are left blank; debt covers central government only.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                search=True,
                # a small table reads better a step above the dense baseline
                font_size="+1",
            ),
            columns=[
                col.markdown("country"),
                col.bar("gdp", title="Real GDP", color="#01A9C3", align="center")
                   .label(value=True, format="num1", position="outside_start")
                   .scale(domain=league_domains["gdp"])
                   .reference_line(0, color="#94a3b8"),
                col.bar("consumption", title="Real consumption\nper person", color="#086FA1", align="center")
                   .label(value=True, format="num1", position="outside_start")
                   .scale(domain=league_domains["consumption"])
                   .reference_line(0, color="#94a3b8"),
                col.bar("prices", title="Equity prices\n(USD)", color="#8BB9CE",  align="center")
                   .label(value=True, format="num1", position="outside_start")
                   .scale(domain=league_domains["prices"])
                   .reference_line(0, color="#94a3b8"),
                col.bar("investment", title="Real fixed\ninvestment", color="#559CB8", align="center")
                   .label(value=True, format="num1", position="outside_start")
                   .scale(domain=league_domains["investment"])
                   .reference_line(0, color="#94a3b8"),
                col.bar("debt", title="Central gov debt\n(pp of GDP)", color="#2EC1D3", align="center")
                   .label(value=True, format="num1", position="outside_start")
                   .scale(domain=league_domains["debt"])
                   .reference_line(0, color="#94a3b8"),
            ],
            rules=[tab_style(cells_body(columns=list(league_domains)), min_width="110px")],
        )
    )
    league_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Options

    The same column, three ways. `.label(value=True, position="outside_start")`
    places the value beside zero, across from the bar; omitting it shows the bar
    alone. `color`/`color_negative` set one colour for both signs (or two).
    `size=0.65` uses 65% of the row height, leaving space above and below
    the bar; the zero reference line stays continuous. `.scale(domain=...)`
    controls the range shared by the marks and the reference line.

    Colours accept matplotlib's names too — `tab:blue`, `C0`–`C9`, `k`, … — as the
    third column shows (`tab:blue` with `size=0.5`).
    """)
    return


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
                col.markdown("country"),
                col.bar("gdp", title="With values", color="blue", color_negative="red", size=0.65)
                .label(value=True, format='0.0"%"', position="outside_start")
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
                col.bar("gdp", title="Bar only", color="blue", color_negative="red", size=0.65)
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
                col.bar("gdp", title="tab:blue, size=0.5", color="tab:blue", size=0.5)
                .label(value=True, format='0.0"%"', position="outside_start")
                .scale(domain=league_domains["gdp"])
                .reference_line(0, color="#94a3b8"),
            ],
            rules=[tab_style(cells_body(columns=["gdp"]), min_width="110px")],
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
                stretch=False,
                # width="720px",
            ),
            columns=[
                col.text("country", title="", align="right"),
                col.bar(lambda row: -row["tolerance"], title="Tolerance", color="#fea224", size=0.65)
                .label(source="tolerance", format="pct0")
                .scale(domain=(-1, 0))
                .reference_line(0, color="#94a3b8"),
                col.bar("intolerance", color="#1374a8", size=0.65)
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
