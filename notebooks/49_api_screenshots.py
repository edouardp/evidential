# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Named cells for the README hero and every image in ``docs/api/images``.

Run ``make api-screenshots`` to start this notebook headlessly and capture each
cell's table with Playwright. Keep the cell names stable: they are the image
slugs used by ``docs/api/API.md``, ``docs/preview.png`` and
``scripts/api_screenshots.py``.

Cells without a table (imports, helpers) are deliberately unnamed.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import datetime as dt
    from pathlib import Path

    import duckdb

    from evidential import (
        EvidentialTable,
        cells_body,
        col,
        label,
        cols_merge_n_pct,
        cols_merge_range,
        cols_merge_uncert,
        comparison_table,
        grouped_table,
        pivot_table,
        query_table,
        section_row,
        settings,
        tab_style,
        text_transform,
    )

    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    now = dt.datetime.now().replace(microsecond=0)

    def sample_orders():
        """An in-memory DuckDB with Evidence's sample orders view."""
        connection = duckdb.connect()
        connection.execute("CREATE SCHEMA needful_things")
        path = str(sample).replace("'", "''")
        connection.execute(f"CREATE VIEW needful_things.orders AS SELECT * FROM read_parquet('{path}')")
        return connection

    def ago(**delta):
        return (now - dt.timedelta(**delta)).strftime("%Y-%m-%d %H:%M:%S")

    return (
        EvidentialTable,
        ago,
        cells_body,
        col,
        cols_merge_n_pct,
        cols_merge_range,
        cols_merge_uncert,
        comparison_table,
        grouped_table,
        label,
        pivot_table,
        query_table,
        sample_orders,
        section_row,
        settings,
        tab_style,
        text_transform,
    )


@app.cell
def quickstart(EvidentialTable, col, settings):
    tips = [
        {"city": "Boston", "trips": 1284, "revenue": 48120.50, "tip_rate": 0.183},
        {"city": "New York", "trips": 3502, "revenue": 142880.25, "tip_rate": 0.171},
        {"city": "Chicago", "trips": 2118, "revenue": 76540.00, "tip_rate": 0.164},
        {"city": "San Francisco", "trips": 1907, "revenue": 98320.75, "tip_rate": 0.196},
        {"city": "Seattle", "trips": 1463, "revenue": 61140.10, "tip_rate": 0.188},
    ]
    EvidentialTable(
        tips,
        columns=[
            col.text("city", title="City"),
            col.integer("trips", title="Trips"),
            col.currency("revenue", title="Revenue"),
            col.percent("tip_rate", decimals=1, title="Tip rate"),
        ],
        settings=settings(
            title="Tipping by city",
            caption="Illustrative sample orders.",
            width="620px",
        ),
    )
    return


@app.cell
def preview(EvidentialTable, col, label, section_row, settings):
    def destination(
        city,
        visitors,
        revenue,
        revenue_prior,
        occupancy,
        trend,
        change,
        revenue_note=None,
        occupancy_note=None,
    ):
        return {
            "city": city,
            "visitors": visitors,
            "revenue": revenue,
            "revenue_prior": revenue_prior,
            "occupancy": occupancy,
            "trend": trend,
            "change": change,
            "revenue_note": revenue_note,
            "occupancy_note": occupancy_note,
        }

    cities = [
        section_row("Americas"),
        destination("New York", 61.8, 16.4, 14.9, 0.84, [46, 48, 50, 53, 55, 58, 60, 62], 0.10),
        destination("Los Angeles", 50.2, 13.1, 12.4, 0.80, [38, 40, 42, 44, 46, 47, 49, 50], 0.06),
        destination("Chicago", 30.4, 7.8, 7.3, 0.74, [22, 23, 24, 24, 25, 26, 27, 30], 0.07),
        destination("Toronto", 27.1, 6.9, 6.1, 0.78, [18, 19, 20, 21, 22, 23, 25, 27], 0.13),
        destination("Mexico City", 24.8, 5.6, 5.2, 0.71, [17, 18, 19, 20, 21, 22, 23, 25], 0.08),
        section_row("Europe"),
        destination(
            "London",
            58.4,
            17.2,
            15.8,
            0.86,
            [41, 43, 46, 48, 51, 53, 55, 58],
            0.09,
            revenue_note="Prior year includes a one-off terminal opening.",
        ),
        destination("Paris", 44.1, 12.9, 11.7, 0.82, [31, 33, 35, 37, 39, 41, 43, 44], 0.10),
        destination("Rome", 35.7, 9.4, 8.8, 0.79, [24, 25, 27, 28, 30, 32, 34, 36], 0.07),
        destination("Barcelona", 32.6, 8.7, 8.1, 0.81, [21, 23, 24, 26, 27, 29, 31, 33], 0.07),
        destination("Amsterdam", 28.9, 7.5, 7.0, 0.83, [19, 20, 21, 22, 24, 25, 27, 29], 0.07),
        section_row("Asia-Pacific"),
        destination(
            "Tokyo",
            31.9,
            11.3,
            10.1,
            0.77,
            [22, 23, 25, 26, 27, 28, 30, 32],
            0.12,
            occupancy_note="Rooms sold, not rooms available.",
        ),
        destination("Singapore", 27.5, 9.8, 8.7, 0.85, [20, 21, 22, 23, 24, 25, 26, 27], 0.13),
        destination("Sydney", 25.3, 8.2, 7.6, 0.78, [17, 18, 19, 20, 21, 22, 23, 25], 0.08),
        destination("Seoul", 23.7, 7.0, 6.4, 0.75, [16, 17, 17, 18, 19, 20, 22, 24], 0.09),
        destination("Bangkok", 22.1, 6.3, 5.9, 0.69, [15, 16, 17, 18, 18, 19, 21, 22], 0.07),
    ]

    preview_table = EvidentialTable(
        cities,
        columns=[
            col.text("city", title="City"),
            col.number("visitors", fmt="num1", title="Visitors (m)"),
            col.subcolumns("Revenue (US$m) · latest / prior", [
                col.bar("revenue", format="usd1", label=label.auto_position("outside end")),
                col.currency("revenue_prior", decimals=1)
                   .font_color("#94a3b8")
                   .footnote("revenue_note"),
            ]),
            col.percent("occupancy", decimals=0, title="Occupancy")
               .color(scale=["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
                      min=0.6, max=0.9)
               .footnote("occupancy_note"),
            col.sparkline("trend", type="area", fit_to_data=True, width=120, height=30, title="Visitors trend"),
            col.percent("change", decimals=0, title="Change")
               .delta(down_is_good=False, neutral_range="-0.02:0.02"),
            col.auto("revenue_note").hide(),
            col.auto("occupancy_note").hide(),
        ],
        settings=settings(
            title="Global city tourism",
            subtitle="Visitors, revenue and occupancy across 15 city destinations",
            caption="Illustrative data. Revenue pairs show the latest year beside the muted prior year.",
            search=True,
            page_size=18,
            row_shading=True,
            freeze_columns=2,
            width="1200px",
            stub="city",
            stub_head="City",
            section_indent=1,
        ),
    )
    preview_table
    return


@app.cell
def kinds(EvidentialTable, col, settings):
    menu = [
        {
            "item": "Espresso",
            "count": 1240,
            "price": 3.50,
            "share": 0.42,
            "day": "2024-03-04",
            "origin": "ITA",
            "active": True,
        },
        {
            "item": "Cortado",
            "count": 861,
            "price": 4.25,
            "share": 0.29,
            "day": "2024-03-05",
            "origin": "ESP",
            "active": True,
        },
        {
            "item": "Cold brew",
            "count": 512,
            "price": 5.00,
            "share": 0.17,
            "day": "2024-03-07",
            "origin": "USA",
            "active": False,
        },
        {
            "item": "Matcha",
            "count": 344,
            "price": 5.75,
            "share": 0.12,
            "day": "2024-03-09",
            "origin": "JPN",
            "active": True,
        },
    ]
    EvidentialTable(
        menu,
        columns=[
            col.text("item", title="Item"),
            col.integer("count", title="Count"),
            col.currency("price", title="Price"),
            col.percent("share", decimals=0, title="Share"),
            col.date("day", title="Day"),
            col.flag("origin", title="Origin"),
            col.boolean("active", title="Active"),
        ],
        settings=settings(title="Column kinds", width="760px"),
    )
    return


@app.cell
def relative_time(EvidentialTable, ago, col, settings):
    events = [
        {"event": "Deploy", "at": ago(hours=2)},
        {"event": "Backup", "at": ago(days=1)},
        {"event": "Report", "at": ago(days=6)},
        {"event": "Audit", "at": ago(weeks=3)},
        {"event": "Renewal", "at": ago(days=200)},
    ]
    EvidentialTable(
        events,
        columns=[
            col.text("event", title="Event"),
            col.datetime("at", relative=True, title="When"),
        ],
        settings=settings(title="Relative time", width="420px"),
    )
    return


@app.cell
def symbols(EvidentialTable, col, settings):
    medals = [
        {"country": "Ireland", "gold": 4, "score": 3},
        {"country": "Cyprus", "gold": 3, "score": 2},
        {"country": "France", "gold": 2, "score": 4},
        {"country": "Sweden", "gold": 2, "score": 1},
        {"country": "Slovenia", "gold": 1, "score": 5},
    ]
    EvidentialTable(
        medals,
        columns=[
            col.text("country", title="Country"),
            col.symbols("gold", symbol="■", color="#d97706", title="Glyph"),
            col.symbols("gold", shape="square", color="#d97706", title="Squares"),
            col.symbols("gold", shape="circle", color="#d97706", title="Circles"),
            col.rating("score", title="Rating"),
        ],
        settings=settings(
            title="Repeated symbols",
            width="720px",
            row_lines=False,
            border=False,
        ),
    )
    return


@app.cell
def visualizations(EvidentialTable, col, settings):
    regions = [
        {
            "region": "West",
            "revenue": 142000,
            "growth": 0.12,
            "share": 0.38,
            "trend": [3, 4, 4, 6, 7, 9, 11],
        },
        {
            "region": "East",
            "revenue": 98000,
            "growth": -0.04,
            "share": 0.26,
            "trend": [9, 8, 8, 6, 5, 5, 4],
        },
        {
            "region": "South",
            "revenue": 76000,
            "growth": 0.07,
            "share": 0.21,
            "trend": [4, 5, 5, 6, 6, 7, 7],
        },
        {
            "region": "North",
            "revenue": 54000,
            "growth": 0.02,
            "share": 0.15,
            "trend": [6, 6, 6, 5, 6, 6, 6],
        },
    ]
    EvidentialTable(
        regions,
        columns=[
            col.text("region", title="Region"),
            col.bar("revenue", title="Revenue"),
            col.bar("growth", center=True, title="Growth"),
            col.color("share", title="Share"),
            col.chip("region", title="Chip"),
            col.sparkline("trend", type="area", title="Trend"),
            col.percent("growth", decimals=0, title="Δ").delta(),
        ],
        settings=settings(title="Visualisations", width="860px"),
    )
    return


@app.cell
def back_to_back(EvidentialTable, col, settings):
    countries = [
        {"country": "Switzerland", "spend": 26.0, "rate": 1.52, "color": "#d9a01c"},
        {"country": "Canada", "spend": 19.1, "rate": 1.00, "color": "#b23a2e"},
        {"country": "Australia", "spend": 18.2, "rate": 1.38, "color": "#3a9b9b"},
        {"country": "United Kingdom", "spend": 13.3, "rate": 1.00, "color": "#d9a01c"},
        {"country": "France", "spend": 12.5, "rate": 0.98, "color": "#d9a01c"},
        {"country": "Germany", "spend": 10.0, "rate": 0.55, "color": "#d9a01c"},
        {"country": "Slovenia", "spend": 9.6, "rate": 0.96, "color": "#3a9b9b"},
        {"country": "Belgium", "spend": 9.0, "rate": 0.66, "color": "#3a9b9b"},
        {"country": "Sweden", "spend": 7.4, "rate": 0.79, "color": "#d9a01c"},
        {"country": "Ireland", "spend": 6.5, "rate": 0.40, "color": "#3a9b9b"},
    ]
    EvidentialTable(
        countries,
        settings=settings(
            title="Back-to-back bars",
            caption="Illustrative data, in the style of The Economist.",
            width="500px",
            row_shading=True,
            row_lines=False,
            border=False,
            stretch=False,
        ),
        columns=[
            col.bar(
                "spend",
                format="usd1",
                title="Sales per capita (CAD)",
                direction="left",
                reference=4.3,
                reference_label="OECD median 4.3",
                color="@color",
                pad=3,
            ).align("left"),
            col.text("country", title=""),
            col.bar(
                "rate",
                format="num2",
                title="Foreign-to-Canadian rate",
                reference=0.32,
                reference_label="OECD median 0.32",
                color="@color",
                pad=3,
            ).align("right"),
            col.auto("color").hide(),
        ],
    )
    return


@app.cell
def styling(EvidentialTable, col, settings):
    metrics = [
        {"metric": "Revenue", "q1": 48120.50, "q2": 51240.00, "change": 0.065},
        {"metric": "Costs", "q1": -31400.00, "q2": -29180.00, "change": 0.071},
        {"metric": "Margin", "q1": 16720.50, "q2": 22060.00, "change": 0.319},
        {"metric": "Headcount", "q1": -124, "q2": -131, "change": -0.056},
    ]
    EvidentialTable(
        metrics,
        columns=[
            col.text("metric", title="Metric").bold(),
            col.currency("q1", decimals=0, title="Q1").neg(),
            col.currency("q2", decimals=0, title="Q2").neg(bracket=True),
            col.percent("change", decimals=1, title="Change").neg().italic(),
            col.percent("change", decimals=1, title="Δ %").bold().highlight("#fef3c7"),
        ],
        settings=settings(
            title="Body-cell styling",
            align_decimals=True,
            font_size="+1",
            width="600px",
        ),
    )
    return


@app.cell
def groups(EvidentialTable, col, settings):
    financials = [
        {"region": "North", "revenue": 48120.5, "cost": -19800.0, "profit": 28320.5},
        {"region": "South", "revenue": 36740.0, "cost": -16120.0, "profit": 20620.0},
        {"region": "East", "revenue": 51280.0, "cost": -21500.0, "profit": 29780.0},
        {"region": "West", "revenue": 29860.0, "cost": -13240.0, "profit": 16620.0},
    ]
    EvidentialTable(
        financials,
        columns=[
            col.text("region", title="Region"),
            col.group(
                "Financials",
                [
                    col.currency("revenue", title="Revenue"),
                    col.currency("cost", title="Cost"),
                    col.currency("profit", title="Profit"),
                ],
            ),
        ],
        settings=settings(title="Grouped headers", width="520px"),
    )
    return


@app.cell
def subcolumns(EvidentialTable, col, settings):
    economies = [
        {"country": "Ireland", "gdp": 2.4, "quarter": "Q4", "forecast": 2.1, "cpi": 1.8, "month": "Dec"},
        {"country": "Portugal", "gdp": 3.1, "quarter": "Q4", "forecast": 2.6, "cpi": 2.4, "month": "Dec"},
        {"country": "Greece", "gdp": 2.8, "quarter": "Q3", "forecast": 2.3, "cpi": 3.2, "month": "Nov"},
        {"country": "Spain", "gdp": 1.9, "quarter": "Q4", "forecast": 2.0, "cpi": 2.1, "month": "Dec"},
    ]
    EvidentialTable(
        economies,
        columns=[
            col.text("country", title="Country"),
            col.group(
                "Gross domestic product",
                [
                    col.subcolumns(
                        "Latest",
                        [
                            col.number("gdp", fmt="num1", align="right").neg(),
                            col.auto("quarter").align("left").font_color("#94a3b8"),
                        ],
                    ),
                    col.number("forecast", fmt="num1", align="right", title="Annual forecast"),
                ],
            ),
            col.group(
                "Consumer prices",
                [
                    col.subcolumns(
                        "Latest",
                        [
                            col.number("cpi", fmt="num1", align="right").neg(),
                            col.auto("month").align("left").font_color("#94a3b8"),
                        ],
                    )
                ],
            ),
        ],
        settings=settings(title="Sub-columns inside groups", width="760px"),
        row_lines=False,
        border=False,
    )
    return


@app.cell
def merged(
    EvidentialTable,
    col,
    cols_merge_n_pct,
    cols_merge_range,
    cols_merge_uncert,
    settings,
):
    sites = [
        {"site": "Alpha", "low": 12, "high": 48, "value": 30.2, "uncert": 1.4, "n": 842, "pct": 0.62},
        {"site": "Beta", "low": 8, "high": 31, "value": 19.6, "uncert": 0.9, "n": 511, "pct": 0.38},
        {"site": "Gamma", "low": 21, "high": 60, "value": 42.1, "uncert": 2.0, "n": 1204, "pct": 0.89},
    ]
    EvidentialTable(
        sites,
        columns=[
            col.text("site", title="Site"),
            col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
            col.merge(
                "measurement",
                cols_merge_uncert("value", "uncert", fmt="num1", title="Value"),
            ),
            col.merge("share", cols_merge_n_pct("n", "pct", title="Share")),
        ],
        settings=settings(title="Merged columns", width="560px"),
    )
    return


@app.cell
def grouped_totals(col, grouped_table, sample_orders, settings):
    grouped_table(
        sample_orders(),
        "SELECT category AS category, sales FROM needful_things.orders",
        dimensions=["category"],
        measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
        dimension_config={"category": col.text("category")},
        measure_config={
            "sales": col.currency("sales", decimals=0),
            "orders": col.integer("orders"),
        },
        settings=settings(title="Grouped totals", page_size=10, width="560px"),
    )
    return


@app.cell
def pivoted_columns(col, pivot_table, sample_orders, settings):
    pivot_table(
        sample_orders(),
        "SELECT category, year(order_datetime) AS year, sales FROM needful_things.orders",
        dimensions=["category"],
        pivots=["year"],
        measures=["round(sum(sales), 0) AS sales"],
        dimension_config={"category": col.text("category")},
        measure_config={"sales": col.currency("sales", decimals=0)},
        settings=settings(title="Pivoted columns", page_size=10, width="640px"),
    )
    return


@app.cell
def prior_comparison(col, comparison_table, sample_orders, settings):
    comparison_table(
        sample_orders(),
        "SELECT category, order_datetime, sales FROM needful_things.orders",
        dimensions=["category"],
        measures=["round(sum(sales), 0) AS sales"],
        date_column="order_datetime",
        compare_vs="prior year",
        measure_config={"sales": col.currency("sales", decimals=0)},
        settings=settings(title="Prior-period comparison", page_size=10, width="820px"),
    )
    return


@app.cell
def rules(
    EvidentialTable,
    cells_body,
    col,
    settings,
    tab_style,
    text_transform,
):
    categories = [
        {"category": "Widgets", "sales": 128400.0},
        {"category": "Gadgets", "sales": 96210.0},
        {"category": "Gizmos", "sales": 54180.0},
        {"category": "Doohickeys", "sales": 21760.0},
    ]
    EvidentialTable(
        categories,
        columns=[
            col.text("category", title="Category"),
            col.bar("sales", format="usd0", title="Sales", label=True),
        ],
        rules=[
            text_transform(cells_body("category"), str.upper),
            tab_style(cells_body("sales"), color="#b45309"),
        ],
        settings=settings(title="Display rules", width="480px"),
    )
    return


@app.cell
def ad_hoc_query(col, query_table, sample_orders, settings):
    query_table(
        sample_orders(),
        "SELECT category, item, round(sum(sales), 0) AS sales FROM needful_things.orders GROUP BY category, item",
        order="sales DESC",
        limit=6,
        columns=[col.text("category"), col.text("item"), col.currency("sales", decimals=0)],
        settings=settings(title="Ad-hoc query", width="620px"),
    )
    return


if __name__ == "__main__":
    app.run()
