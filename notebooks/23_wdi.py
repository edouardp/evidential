# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///
"""Surface the World Development Indicators Parquet bundle with EvidenceTables.

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

    from evidence_tables import (
        EvidenceTable,
        LiveEvidenceTable,
        comparison_table,
        grouped_table,
        pivot_table,
    )

    return (
        EvidenceTable,
        LiveEvidenceTable,
        Path,
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
    indicator = mo.ui.dropdown(
        options=indicator_options,
        value="SP.DYN.LE00.IN",
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
def _(LiveEvidenceTable, connection, mo):
    ranking = LiveEvidenceTable(
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
        column_config={
            "country": {"align": "left"},
            "region": {"align": "left"},
            "income_group": {"title": "Income group", "align": "left"},
            "value": {"fmt": "num", "viz": "bar"},
        },
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
    trend_country = mo.ui.dropdown(
        options=countries, value="JPN", label="Country", searchable=True
    )
    trend_country
    return (trend_country,)


@app.cell
def _(EvidenceTable, connection, mo, trend_country):
    trend = mo.ui.anywidget(
        EvidenceTable(
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
            column_config={
                "year": {"fmt": "num0", "align": "left"},
                "value": {"fmt": "num2", "viz": "bar"},
            },
        )
    )
    trend
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
def _(connection, mo, pivot_table):
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
            column_config={"country": {"align": "left"}},
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
def _(connection, grouped_table, mo):
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
                "region": {"align": "left"},
                "income_group": {"title": "Income group", "align": "left"},
            },
            measure_config={
                "avg_life_expectancy": {"fmt": "num1", "viz": "bar"},
                "countries": {"fmt": "num0"},
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
def _(comparison_table, connection, mo):
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
            dimension_config={"region": {"align": "left"}},
            measure_config={"avg_life_expectancy": {"fmt": "num2"}},
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
def _(EvidenceTable, connection, mo):
    countries_table = mo.ui.anywidget(
        EvidenceTable(
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
            column_config={
                "code": {"align": "left"},
                "name": {"align": "left"},
                "Region": {"title": "Region", "align": "left"},
                "income_group": {"align": "left"},
                "currency": {"align": "left"},
            },
        )
    )
    countries_table
    return


@app.cell
def _(EvidenceTable, connection, mo):
    indicators_table = mo.ui.anywidget(
        EvidenceTable(
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
            column_config={
                "code": {"align": "left"},
                "name": {"align": "left", "wrap": True},
                "Topic": {"align": "left"},
                "unit": {"align": "left"},
            },
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
def _(EvidenceTable, connection, mo):
    footnotes_table = mo.ui.anywidget(
        EvidenceTable(
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
            column_config={
                "country_code": {"title": "Country", "align": "left"},
                "year": {"fmt": "num0", "align": "left"},
                "description": {"align": "left", "wrap": True},
            },
        )
    )
    footnotes_table
    return


if __name__ == "__main__":
    app.run()
