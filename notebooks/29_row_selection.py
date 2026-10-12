# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///
"""Click a country in one table to drill into a second table.

The country list sets ``select="country_code"``. Clicking a row stores that
row's key in the widget's ``selected`` trait and saves the change, which Marimo
treats as a cell dependency. A second cell reads ``table.widget.selected`` and a
third queries the World Bank WDI bundle for that country — years as rows,
indicators as columns.

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

    from evidence_tables import EvidenceTable

    return EvidenceTable, Path, duckdb, mo, os


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
    # A table that drives the notebook

    The country list sets `select="country_code"`: clicking a row stores that
    row's key in the widget's **`selected`** trait and calls `save_changes()`.
    Marimo sees the new value as a cell dependency, so the two cells below
    re-run — a second table queries the World Bank data for the clicked country,
    with **years as rows and indicators as columns**.

    ```python
    table = mo.ui.anywidget(EvidenceTable(rows, select="country_code"))
    ...
    selected = table.widget.selected   # re-runs when a row is clicked
    ```

    Click a row (and click it again to clear).
    """)
    return


@app.cell
def _(EvidenceTable, connection, mo):
    countries = mo.ui.anywidget(
        EvidenceTable(
            connection.sql(
                """
                SELECT
                    c."Country Code" AS country_code,
                    c."Short Name"   AS country,
                    c.Region         AS region,
                    max(o.value) FILTER (WHERE o.indicator_code = 'SP.POP.TOTL')     AS "Population",
                    max(o.value) FILTER (WHERE o.indicator_code = 'NY.GDP.PCAP.CD')  AS "GDP per capita"
                FROM country c
                LEFT JOIN observations o
                  ON o.country_code = c."Country Code" AND o.year = 2023
                WHERE c.Region IS NOT NULL
                GROUP BY 1, 2, 3
                ORDER BY "Population" DESC NULLS LAST
                """
            ),
            title="Countries",
            subtitle="Click a row to drill in",
            select="country_code",
            search=True,
            page_size=10,
            row_shading=True,
            freeze_columns=2,
            column_config={
                "country_code": {"title": "Code", "align": "left"},
                "country": {"align": "left"},
                "region": {"align": "left"},
                "Population": {"fmt": "num0"},
                "GDP per capita": {"fmt": "usd0"},
            },
        )
    )
    countries
    return (countries,)


@app.cell
def _(countries):
    selected = countries.widget.selected
    return (selected,)


@app.cell
def _(mo, selected):
    mo.md(
        "### Click a country above to drill in."
        if not selected
        else f"### Selected country: **{selected}**"
    )
    return


@app.cell
def _(EvidenceTable, connection, mo, selected):
    mo.stop(not selected, mo.md("*No country selected yet.*"))

    detail = mo.ui.anywidget(
        EvidenceTable(
            connection.sql(
                """
                SELECT
                    year,
                    max(value) FILTER (WHERE indicator_code = 'NY.GDP.MKTP.CD')    AS "GDP (current US$)",
                    max(value) FILTER (WHERE indicator_code = 'NY.GDP.PCAP.CD')    AS "GDP per capita (US$)",
                    max(value) FILTER (WHERE indicator_code = 'SP.POP.TOTL')       AS "Population",
                    max(value) FILTER (WHERE indicator_code = 'SP.DYN.LE00.IN')    AS "Life expectancy",
                    max(value) FILTER (WHERE indicator_code = 'SP.URB.TOTL.IN.ZS') AS "Urban share (%)",
                    max(value) FILTER (WHERE indicator_code = 'FP.CPI.TOTL.ZG')    AS "Inflation (%)"
                FROM observations
                WHERE country_code = $code
                GROUP BY year
                ORDER BY year DESC
                """,
                params={"code": selected},
            ),
            title=f"{selected} — every year",
            subtitle="Rows are years; columns are indicators",
            page_size=12,
            row_shading=True,
            default_sort={"column": "year", "direction": "desc"},
            column_config={
                "year": {"fmt": "yyyy", "align": "left"},
                "GDP (current US$)": {"fmt": "usd"},
                "GDP per capita (US$)": {"fmt": "usd"},
                "Population": {"fmt": "num"},
                "Life expectancy": {"fmt": "num1"},
                "Urban share (%)": {"fmt": '0.0"%"'},
                "Inflation (%)": {"fmt": '0.0"%"'},
            },
        )
    )
    detail
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `select` names the column whose value becomes the selection. Rows get a
      pointer cursor; the clicked row is marked, and clicking it again clears it.
    - The value crosses to Python because the renderer calls
      `model.set("selected", ...)` **and** `model.save_changes()` — Marimo treats
      the saved change as a UI-element value update and re-runs the cells that
      read `table.widget.selected`.
    - `EvidenceTable(..., select="country_code", selected="NZL")` preselects a
      row.
    - The country table is not re-created on click: only the cells that depend on
      `selected` re-run.
    """)
    return


if __name__ == "__main__":
    app.run()
