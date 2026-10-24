# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Surface the World Development Indicators Parquet bundle with Evidential.

WDI is a panel: one value per (country, indicator, year). This notebook reads
the hive-partitioned Parquet bundle and shows the same data several ways — a
live filterable ranking, a pivot, grouped subtotals, a prior-year comparison,
the dimensions, and the footnotes.

Point it at a different bundle with the ``WDI_PARQUET`` environment variable
(default: ``~/Downloads/WDI_CSV_2026_10_01/parquet``).
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import (
        EvidentialTable,
        LiveEvidentialTable,
        col,
        comparison_table,
        grouped_table,
        pivot_table,
    )

    return (
        EvidentialTable,
        LiveEvidentialTable,
        Path,
        col,
        comparison_table,
        duckdb,
        grouped_table,
        mo,
        os,
        pivot_table,
    )


@app.cell
def _(Path, duckdb, mo, os):
    parquet = Path(
        os.environ.get("WDI_PARQUET", "~/Downloads/WDI_CSV_2026_10_01/parquet")
    ).expanduser()
    if not (parquet / "wdi_observations").is_dir():
        mo.stop(
            True,
            mo.md(
                f"No WDI Parquet bundle at `{parquet}`. Set `WDI_PARQUET` to the "
                "`parquet/` directory of a WDI conversion."
            ),
        )

    connection = duckdb.connect()
    views = {
        "observations": "wdi_observations/**/*.parquet",
        "footnotes": "wdi_footnotes/**/*.parquet",
        "country": "country.parquet",
        "series": "series.parquet",
        "country_series": "country_series.parquet",
        "series_time": "series_time.parquet",
    }
    for name, glob in views.items():
        connection.execute(
            f"CREATE VIEW {name} AS "
            f"SELECT * FROM read_parquet('{parquet}/{glob}', hive_partitioning = true)"
        )
    return connection, parquet


@app.cell
def _(mo, parquet):
    mo.md(f"""
    # World Development Indicators

    The World Bank **WDI** bundle, converted to hive-partitioned Parquet
    (`{parquet.name}`) and queried live with DuckDB.

    It is a panel: one `value` per `(country, indicator, year)`. The fact table
    is partitioned by year, so a year filter prunes to a single file. Units vary
    by indicator — the **Unit of measure** lives in the `series` dimension.

    The sections below surface the same data as a **live ranking**, a **trend**,
    a **wide pivot**, **grouped subtotals**, a **prior-year comparison**, the
    **dimensions**, and the **footnotes**.
    """)
    return


@app.cell
def _(connection, mo):
    obs, codes, indicator_count, y0, y1 = connection.sql(
        """
        SELECT count(*), count(DISTINCT country_code),
               count(DISTINCT indicator_code), min(year), max(year)
        FROM observations
        """
    ).fetchone()
    total, real, aggregates = connection.sql(
        """
        SELECT count(*), count(*) FILTER (WHERE Region IS NOT NULL),
               count(*) FILTER (WHERE Region IS NULL)
        FROM country
        """
    ).fetchone()
    mo.md(f"""
    | | |
    | --- | --- |
    | Observations | **{obs:,}** |
    | Years | **{y0}–{y1}** |
    | Countries / territories | {real:,} |
    | World Bank aggregates | {aggregates:,} |
    | Indicators | {indicator_count:,} |
    | Distinct country codes in the fact table | {codes:,} |
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Live ranking

    Pick an indicator, a year and a region — the table re-queries in place,
    keeping its sort, search and page. (The cell that *creates* the widget does
    not reference the controls; a separate reactive cell calls `set_controls`.)
    """)
    return


@app.cell
def _(connection, mo):
    indicator_options = dict(
        connection.sql(
            'SELECT "Indicator Name", "Series Code" FROM series ORDER BY "Indicator Name"'
        ).fetchall()
    )
    # With a {label: value} mapping, `value` selects by label; .value is the code.
    default_indicator = next(
        (
            label
            for label, code in indicator_options.items()
            if code == "SP.DYN.LE00.IN"
        ),
        None,
    )
    indicator = mo.ui.dropdown(
        options=indicator_options,
        value=default_indicator,
        label="Indicator",
        searchable=True,
    )
    years = [
        row[0]
        for row in connection.sql(
            "SELECT DISTINCT year FROM observations ORDER BY year DESC"
        ).fetchall()
    ]
    year = mo.ui.dropdown(options=years, value=2023, label="Year")
    regions = [
        row[0]
        for row in connection.sql(
            "SELECT DISTINCT Region FROM country WHERE Region IS NOT NULL ORDER BY Region"
        ).fetchall()
    ]
    region = mo.ui.dropdown(
        options=["All regions", *regions], value="All regions", label="Region"
    )
    mo.hstack([indicator, year, region], justify="start")
    return indicator, region, year


@app.cell
def _(LiveEvidentialTable, col, connection):
    ranking = LiveEvidentialTable(
        connection,
        """
        SELECT
            c."Short Name"   AS country,
            c.Region         AS region,
            c."Income Group" AS income_group,
            round(o.value, 2) AS value
        FROM observations o
        JOIN country c ON c."Country Code" = o.country_code
        WHERE o.indicator_code = {indicator}
          AND o.year = {year}
          AND c.Region IS NOT NULL
          AND ({region} = 'All regions' OR c.Region = {region})
        ORDER BY o.value DESC
        """,
        auto_run=False,
        title="Countries ranked by the selected indicator",
        page_size=15,
        search=True,
        row_shading=True,
        columns=[
            col.text("country"),
            col.text("region"),
            col.text("income_group", title="Income group"),
            col.bar("value", fmt="num", label=True),
        ],
    )
    ranking
    return (ranking,)


@app.cell
def _(indicator, ranking, region, year):
    _ = ranking.set_controls(indicator=indicator, region=region, year=year)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Trend

    One country, every year on record — a bar column over time.
    """)
    return


@app.cell
def _(connection, mo):
    countries = dict(
        connection.sql(
            'SELECT "Short Name", "Country Code" FROM country '
            'WHERE Region IS NOT NULL ORDER BY "Short Name"'
        ).fetchall()
    )
    default_country = next(
        (label for label, code in countries.items() if code == "JPN"), None
    )
    trend_country = mo.ui.dropdown(
        options=countries, value=default_country, label="Country", searchable=True
    )
    trend_country
    return (trend_country,)


@app.cell
def _(EvidentialTable, col, connection, mo, trend_country):
    trend = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT year, round(value, 2) AS value
                FROM observations
                WHERE indicator_code = 'SP.DYN.LE00.IN' AND country_code = ?
                ORDER BY year
                """,
                params=[trend_country.value],
            ),
            title=f"{trend_country.value} — life expectancy at birth",
            max_height="420px",
            row_lines=False,
            columns=[
                col.number("year", fmt="yyyy", align="left"),
                col.bar("value", fmt="num2", label=True),
            ],
        )
    )
    trend
    return


@app.cell
def _(mo):
    mo.md("""
    ## All years in one sparkline

    The same **indicator** and **region** controls drive a second view: one row
    per country with every reported year packed into a sparkline — an
    `ARRAY_AGG` of `{'year': …, 'value': …}` objects. `% change` compares the
    **last 5 years** with the **previous 10** (averages, computed in SQL), and
    `Kendall τ` measures the monotonic trend across every year — computed in SQL
    with an O(n log n) bottom-up merge-sort pair count (Knight's algorithm).
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, indicator, mo, region):
    sparklines = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                WITH anchored AS (
                    SELECT max(year) AS anchor
                    FROM observations
                    WHERE indicator_code = $indicator
                ),
                series AS (
                    SELECT o.country_code, c."Short Name" AS country,
                           c.Region AS region, o.year, o.value
                    FROM observations o
                    JOIN country c ON c."Country Code" = o.country_code
                    WHERE o.indicator_code = $indicator
                      AND c.Region IS NOT NULL
                      AND ($region = 'All regions' OR c.Region = $region)
                      AND o.year >= 2000
                ),
                -- Kendall's S per country: bottom-up merge-sort pair counting.
                -- i is the 0-based year position (distinct per country); a pair
                -- is counted once, at the highest bit where the two i differ.
                pos AS (
                    SELECT s.*, s.year - min(s.year) OVER () AS i
                    FROM series s
                ),
                lv AS (
                    SELECT range AS l
                    FROM range(0, (SELECT ceil(log2(greatest(max(i) + 1, 1)))::INT FROM pos))
                ),
                pair_input AS (
                    SELECT p.country_code, l, p.i >> (l + 1) AS blk,
                           ((p.i >> l) & 1) = 0 AS is_left, p.value AS y
                    FROM pos p, lv
                ),
                pair_counts AS (
                    SELECT
                        country_code,
                        is_left,
                        sum(is_left::INT) OVER (
                            PARTITION BY country_code, l, blk ORDER BY y
                            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ) AS le,
                        sum(is_left::INT) OVER (PARTITION BY country_code, l, blk, y) AS eq,
                        sum(is_left::INT) OVER (PARTITION BY country_code, l, blk) AS tot
                    FROM pair_input
                ),
                kendall AS (
                    SELECT country_code, sum((le - eq) - (tot - le))::BIGINT AS s
                    FROM pair_counts
                    WHERE NOT is_left
                    GROUP BY country_code
                ),
                stats AS (
                    SELECT
                        country_code,
                        any_value(country) AS country,
                        any_value(region) AS region,
                        count(*) AS years,
                        round(arg_max(value, year), 2) AS latest,
                        (avg(value) FILTER (WHERE year BETWEEN a.anchor - 4 AND a.anchor)
                         - avg(value) FILTER (WHERE year BETWEEN a.anchor - 14 AND a.anchor - 5))
                          / nullif(avg(value) FILTER (
                                WHERE year BETWEEN a.anchor - 14 AND a.anchor - 5), 0) AS pct_change,
                        round(avg(value) FILTER (
                            WHERE year BETWEEN a.anchor - 4 AND a.anchor), 2) AS avg_last_5,
                        round(avg(value) FILTER (
                            WHERE year BETWEEN a.anchor - 14 AND a.anchor - 5), 2) AS avg_prev_10,
                        array_agg(
                            {'year': year, 'value': round(value, 2)}
                            ORDER BY year
                        ) AS trend
                    FROM series, anchored a
                    GROUP BY country_code
                )
                SELECT
                    st.country,
                    st.region,
                    st.years,
                    st.latest,
                    st.pct_change,
                    k.s / nullif(st.years * (st.years - 1) / 2.0, 0) AS kendall_tau,
                    st.avg_last_5,
                    st.avg_prev_10,
                    st.trend
                FROM stats st
                JOIN kendall k USING (country_code)
                ORDER BY st.country ASC
                """,
                params={"indicator": indicator.value, "region": region.value},
            ),
            title="Last 5 years vs the previous 10, with every year in a sparkline",
            search=True,
            page_size=12,
            row_shading=True,
            default_sort={"column": "trend", "direction": "desc"},
            columns=[
                col.text("country"),
                col.text("region"),
                col.integer("years"),
                col.number("latest", fmt="num"),
                col.percent("pct_change", decimals=1, title="% change (5y vs 10y)").delta(),
                col.number("kendall_tau", fmt="num2", title="Kendall τ").color(
                    scale="rdylgn", min=-1, max=1, midpoint=0
                ),
                col.number("avg_last_5", fmt="num2", title="Last 5y avg"),
                col.number("avg_prev_10", fmt="num2", title="Prev 10y avg"),
                col.sparkline("trend", title="Since 2000", x="year", y="value", type="bar", 
                    fit_to_data=True, width=130, height=26,
                )
                .sort_by("kendall_tau")
                .align("center"),
            ],
        )
    )
    sparklines
    return


@app.cell
def _(mo):
    mo.md("""
    ## Wide view (pivot)

    `pivot_table` turns the `year` column into one column per year, grouped
    under spanners.
    """)
    return


@app.cell
def _(col, connection, mo, pivot_table):
    wide = mo.ui.anywidget(
        pivot_table(
            connection,
            """
            SELECT c."Short Name" AS country, o.year, o.value
            FROM observations o
            JOIN country c ON c."Country Code" = o.country_code
            WHERE o.indicator_code = 'SP.DYN.LE00.IN'
              AND o.year IN (1990, 2000, 2010, 2020, 2023)
              AND c."Short Name" IN ('Japan', 'United States', 'India', 'Nigeria', 'Brazil')
            """,
            dimensions=["country"],
            pivots=["year"],
            measures=["max(value) AS life_expectancy"],
            show_total_column=False,
            title="Life expectancy at birth, by year",
            dimension_config={"country": col.text("country")},
        )
    )
    wide
    return


@app.cell
def _(mo):
    mo.md("""
    ## Grouped subtotals

    `grouped_table` runs one `GROUPING SETS` query to build region → income-group
    subtotals and a grand total.
    """)
    return


@app.cell
def _(col, connection, grouped_table, mo):
    grouped = mo.ui.anywidget(
        grouped_table(
            connection,
            """
            SELECT c.Region AS region, c."Income Group" AS income_group, o.value
            FROM observations o
            JOIN country c ON c."Country Code" = o.country_code
            WHERE o.indicator_code = 'SP.DYN.LE00.IN'
              AND o.year = 2023
              AND c.Region IS NOT NULL
            """,
            dimensions=["region", "income_group"],
            measures=[
                "round(avg(value), 1) AS avg_life_expectancy",
                "count(*) AS countries",
            ],
            subtotal_position="top",
            total_label="All countries",
            title="Average life expectancy by region and income group (2023)",
            max_height="460px",
            dimension_config={
                "region": col.text("region"),
                "income_group": col.text("income_group", title="Income group"),
            },
            measure_config={
                "avg_life_expectancy": col.bar("avg_life_expectancy", fmt="num1", label=True),
                "countries": col.integer("countries"),
            },
        )
    )
    grouped
    return


@app.cell
def _(mo):
    mo.md("""
    ## Prior-year change

    `comparison_table` adds prior / change / % change columns. For life
    expectancy the change is in **years**, so the delta is formatted as a
    number rather than a percentage.
    """)
    return


@app.cell
def _(col, comparison_table, connection, mo):
    changes = mo.ui.anywidget(
        comparison_table(
            connection,
            """
            SELECT c.Region AS region, make_date(o.year, 1, 1) AS date, o.value
            FROM observations o
            JOIN country c ON c."Country Code" = o.country_code
            WHERE o.indicator_code = 'SP.DYN.LE00.IN'
              AND o.year >= 2015
              AND c.Region IS NOT NULL
            """,
            dimensions=["region"],
            measures=["round(avg(value), 2) AS avg_life_expectancy"],
            date_column="date",
            compare_vs="prior year",
            title="Life expectancy by region — latest year vs the year before",
            dimension_config={"region": col.text("region")},
            measure_config={"avg_life_expectancy": col.number("avg_life_expectancy", fmt="num2")},
        )
    )
    changes
    return


@app.cell
def _(mo):
    mo.md("""
    ## The dimensions

    Small lookup tables, stored as single Parquet files: countries (with region,
    income group and currency) and indicators (with topic and unit).
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    countries_table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT "Country Code" AS code, "Short Name" AS name, Region,
                       "Income Group" AS income_group, "Currency Unit" AS currency
                FROM country
                ORDER BY name
                """
            ),
            title="Country / entity dimension",
            search=True,
            page_size=12,
            columns=[
                col.text("code"),
                col.text("name"),
                col.text("Region", title="Region"),
                col.text("income_group"),
                col.text("currency"),
            ],
        )
    )
    countries_table
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    indicators_table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT "Series Code" AS code, "Indicator Name" AS name, Topic,
                       "Unit of measure" AS unit
                FROM series
                ORDER BY code
                """
            ),
            title="Indicator dimension",
            search=True,
            page_size=12,
            columns=[
                col.text("code"),
                col.text("name").wrap(),
                col.text("Topic"),
                col.text("unit"),
            ],
        )
    )
    indicators_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Footnotes

    An 846k-row footnote table (partitioned by year) keyed by country, series
    and year. Here it is for under-5 mortality, the best-documented indicator.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    footnotes_table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT country_code, year, description
                FROM footnotes
                WHERE series_code = 'SH.DYN.MORT'
                ORDER BY country_code, year
                """
            ),
            title="Footnotes — under-5 mortality (SH.DYN.MORT)",
            search=True,
            page_size=10,
            columns=[
                col.text("country_code", title="Country"),
                col.number("year", fmt="yyyy", align="left"),
                col.text("description").wrap(),
            ],
        )
    )
    footnotes_table
    return


if __name__ == "__main__":
    app.run()
