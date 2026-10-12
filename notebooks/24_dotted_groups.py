# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Column groups from dotted column names.

A SQL alias like ``"GDP Measure.GDP (nominal)"`` is grouped under **GDP Measure**
with the leaf label **GDP (Nominal)** — no ``column_groups`` mapping needed. The
part before the last dot is the group (extra dots nest), and the frontend's
``formatTitle`` turns the trailing segment into the leaf title. This notebook
pivots World Bank WDI indicators into dotted columns with one ``SELECT``.

Point it at a WDI Parquet bundle with the ``WDI_PARQUET`` environment variable
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

    from evidential import EvidentialTable

    return EvidentialTable, Path, duckdb, mo, os


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
        "country": "country.parquet",
    }
    for name, glob in views.items():
        connection.execute(
            f"CREATE VIEW {name} AS "
            f"SELECT * FROM read_parquet('{parquet}/{glob}', hive_partitioning = true)"
        )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Column groups from dotted names

    Give a column a dotted **name** and the table groups it automatically: the
    part before the last dot becomes the `column_group`, and the trailing
    segment is the leaf title (`formatTitle` replaces `_` with spaces and
    capitalises each word). No `column_groups` mapping is required.

    ```text
    "GDP Measure.GDP (nominal)"  ->  GDP Measure  >  GDP (Nominal)
    "Labour.unemployment"        ->  Labour       >  Unemployment
    "Root.Sub.Leaf"              ->  Root > Sub   >  Leaf        (dots nest)
    ```

    The hierarchy is read straight off the names, so a SQL query can carry its
    own header structure. Below, one `SELECT` pivots seven World Bank indicators
    into dotted aliases.
    """)
    return


@app.cell
def _(connection):
    reference_year = 2023
    ranking = connection.sql(
        """
        SELECT
            c."Short Name" AS country,
            c.Region       AS region,
            max(o.value) FILTER (WHERE o.indicator_code = 'NY.GDP.MKTP.CD')    AS "GDP Measure.GDP (nominal)",
            max(o.value) FILTER (WHERE o.indicator_code = 'NY.GDP.MKTP.PP.CD') AS "GDP Measure.GDP (PPP)",
            max(o.value) FILTER (WHERE o.indicator_code = 'NY.GDP.PCAP.CD')    AS "GDP Measure.GDP per capita",
            max(o.value) FILTER (WHERE o.indicator_code = 'SP.POP.TOTL')       AS "Population.total",
            max(o.value) FILTER (WHERE o.indicator_code = 'SP.URB.TOTL.IN.ZS') AS "Population.urban share",
            max(o.value) FILTER (WHERE o.indicator_code = 'SL.UEM.TOTL.ZS')    AS "Labour.unemployment",
            max(o.value) FILTER (WHERE o.indicator_code = 'SL.TLF.TOTL.IN')    AS "Labour.labor force"
        FROM observations o
        JOIN country c ON c."Country Code" = o.country_code
        WHERE o.year = $year AND c.Region IS NOT NULL
        GROUP BY c."Short Name", c.Region
        HAVING max(o.value) FILTER (WHERE o.indicator_code = 'NY.GDP.MKTP.CD') IS NOT NULL
        ORDER BY "GDP Measure.GDP (nominal)" DESC
        """,
        params={"year": reference_year},
    )
    return ranking, reference_year


@app.cell
def _(EvidentialTable, mo, ranking, reference_year):
    grouped = mo.ui.anywidget(
        EvidentialTable(
            ranking,
            title=f"World Bank WDI — reference year {reference_year}",
            subtitle="One SELECT; the header groups come from the dotted column aliases",
            row_shading=True,
            page_size=12,
            column_config={
                "GDP Measure.GDP (nominal)": {"fmt": "usd", "align": "right"},
                "GDP Measure.GDP (PPP)": {"fmt": "usd", "align": "right"},
                "GDP Measure.GDP per capita": {"fmt": "usd", "align": "right"},
                "Population.total": {"fmt": '#,##0.0,,"M"', "align": "right"},
                "Population.urban share": {"fmt": '0.0"%"', "align": "right"},
                "Labour.unemployment": {"fmt": '0.0"%"', "align": "right"},
                "Labour.labor force": {"fmt": "num", "align": "right"},
            },
        )
    )
    grouped
    return


@app.cell
def _(mo):
    mo.md("""
    ## Explicit configuration still wins

    A `column_group` in `column_config` (or a `column_groups` mapping) overrides
    the name convention. Below, the two GDP columns are regrouped under
    **Output**, while **GDP per capita** keeps its inferred **GDP Measure** group
    but is renamed **GDP per person**.
    """)
    return


@app.cell
def _(EvidentialTable, mo, ranking):
    overridden = mo.ui.anywidget(
        EvidentialTable(
            ranking,
            title="Explicit groups override the convention",
            subtitle="Two GDP columns regrouped under Output, one leaf renamed",
            row_shading=True,
            page_size=8,
            column_groups={
                "Output": [
                    "GDP Measure.GDP (nominal)",
                    "GDP Measure.GDP (PPP)",
                ],
            },
            column_config={
                "GDP Measure.GDP per capita": {"title": "GDP per person", "fmt": "usd"},
                "Population.total": {"fmt": '#,##0.0,,"M"'},
                "Population.urban share": {"fmt": '0.0"%"'},
                "Labour.unemployment": {"fmt": '0.0"%"'},
                "Labour.labor force": {"fmt": "num"},
            },
        )
    )
    overridden
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - The group is everything before the **last** dot; the trailing segment is
      the leaf title (`formatTitle` capitalises it, so `"Labour.unemployment"`
      reads **Unemployment**). Extra dots **nest**.
    - An explicit `column_group` — or a `column_groups` entry — always wins. To
      show a dotted name verbatim, set both `column_group` and `title`.
    - The `%` columns use the format code `'0.0"%"'` because WDI already stores
      them as percentages (the `pct1` code would multiply by 100 again).
    """)
    return


if __name__ == "__main__":
    app.run()
