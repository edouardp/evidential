# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Explore the Philippine SRA's dbt-built historical sugar data product.

Run ``uv run marimo edit notebooks/52_sra_historical_statistics.py``.
Set ``SRA_DATASET`` to override ``~/datasets/sra-historical-statistics``.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, label

    return EvidentialTable, Path, col, duckdb, label, mo, os


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Philippine sugar · historical statistics

    Monthly production, withdrawals and prices from the **Sugar Regulatory
    Administration (SRA)**, using the local **dbt data product**. Choose a series
    and price measure, then click a crop year to inspect its months.
    Crop years run **September → August**.

    dbt resolves overlapping publications into one observation per
    series/measure/crop-year/month. Its chosen values are used unchanged here,
    including observations where sources disagreed. The monthly table exposes
    the product's source counts, distinct-value counts and relative spread.

    Summary bars show **observed-month totals** for production/withdrawals and
    **monthly means** for prices. Coverage makes partial years explicit; missing
    months stay blank. Printed totals and averages are shown separately below.
    """)
    return


@app.function
def query_rows(connection, sql, parameters=None):
    result = connection.execute(sql, parameters or {})
    names = [field[0] for field in result.description]
    return [dict(zip(names, row, strict=True)) for row in result.fetchall()]


@app.cell
def dataset(Path, duckdb, mo, os):
    dataset_path = Path(
        os.environ.get("SRA_DATASET", "~/datasets/sra-historical-statistics")
    ).expanduser()
    models = ["sra_monthly", "sra_monthly_wide", "sra_totals"]
    processed = dataset_path / "data" / "processed"
    missing = [name for name in models if not (processed / f"{name}.parquet").is_file()]
    mo.stop(
        bool(missing),
        mo.md(
            "Missing dbt product files: "
            + ", ".join(f"`{name}.parquet`" for name in missing)
            + ". Set `SRA_DATASET` to the dataset repository and run "
            "`uv run dbt build --profiles-dir .` there first."
        ),
    )
    connection = duckdb.connect()
    for model in models:
        connection.read_parquet(str(processed / f"{model}.parquet")).create_view(model)
    mo.stop(
        connection.sql("SELECT count(*) FROM sra_monthly").fetchone()[0] == 0,
        mo.md("The dbt monthly product contains no observations."),
    )
    return connection, dataset_path


@app.cell
def metadata():
    series_names = {
        "raw_sugar_production": "Raw sugar production",
        "refined_sugar_production": "Refined sugar production",
        "raw_sugar_withdrawals": "Raw sugar domestic withdrawals",
        "refined_sugar_withdrawals": "Refined sugar withdrawals",
        "millsite_prices": "Millsite prices",
        "metro_manila_prices": "Metro Manila prices",
    }
    series_units = {
        "raw_sugar_production": "Metric tons",
        "refined_sugar_production": "50-kg bags",
        "raw_sugar_withdrawals": "Metric tons",
        "refined_sugar_withdrawals": "50-kg bags",
        "millsite_prices": "PHP per 50-kg bag",
        "metro_manila_prices": "PHP per LKg / kg",
    }
    crop_months = [
        "september",
        "october",
        "november",
        "december",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
    ]
    return crop_months, series_names, series_units


@app.cell
def presentation_data(crop_months):
    def prepare_views(monthly_rows, wide_rows, is_price):
        """Add display summaries and gaps; resolution remains the dbt model's job."""
        observations = {(row["crop_year"], row["month"]): row for row in monthly_rows}
        seasons = []
        monthly = {}
        for wide in sorted(wide_rows, key=lambda row: row["crop_year"], reverse=True):
            crop_year = wide["crop_year"]
            start_year = int(crop_year[:4])
            previous_year = f"{start_year - 1}-{start_year}"
            months = []
            for offset, name in enumerate(crop_months):
                row = observations.get((crop_year, name), {})
                previous = observations.get((previous_year, name), {}).get("value")
                value = row.get("value")
                number = (offset + 8) % 12 + 1
                year = start_year if number >= 9 else start_year + 1
                months.append(
                    {
                        "period": f"{year}-{number:02d}",
                        "value": value,
                        "previous": previous,
                        "change": value - previous
                        if value is not None and previous is not None
                        else None,
                        "change_pct": value / previous - 1
                        if value is not None and previous not in (None, 0)
                        else None,
                        "n_sources": row.get("n_sources"),
                        "n_values": row.get("n_values"),
                        "rel_spread": row.get("rel_spread"),
                        "status": "Not reported"
                        if value is None
                        else "Sources differ"
                        if row.get("conflict")
                        else "Single source"
                        if row.get("n_sources") == 1
                        else "Sources agree",
                    }
                )
            values = [wide[name] for name in crop_months if wide[name] is not None]
            metric = (
                (sum(values) / len(values) if is_price else sum(values))
                if values
                else None
            )
            seasons.append(
                {
                    "crop_year": crop_year,
                    "metric": metric,
                    "coverage": f"{wide['n_months']}/12",
                    "conflicts": sum(
                        row["status"] == "Sources differ" for row in months
                    ),
                    "monthly": [
                        {"date": row["period"], "value": row["value"]} for row in months
                    ],
                }
            )
            monthly[crop_year] = months
        return seasons, monthly

    return (prepare_views,)


@app.cell
def coverage_data(connection, series_names, series_units):
    coverage_rows = query_rows(
        connection,
        """
        SELECT category, count(*) AS observations,
               count(DISTINCT measure) + max((measure IS NULL)::INT) AS measures,
               count(DISTINCT crop_year) AS crop_years,
               min(crop_year) AS first_crop_year, max(crop_year) AS last_crop_year,
               count(*) FILTER (WHERE conflict) AS conflicts
        FROM sra_monthly GROUP BY category ORDER BY category
    """,
    )
    coverage_display = [
        {
            **row,
            "series": series_names.get(row["category"], row["category"]),
            "unit": series_units.get(row["category"], "See source"),
        }
        for row in coverage_rows
    ]
    return coverage_display, coverage_rows


@app.cell
def coverage(EvidentialTable, col, coverage_display):
    EvidentialTable(
        coverage_display,
        title="Dataset coverage · dbt product",
        caption="One resolved observation per series, measure, crop year and month. Conflicts count observations with differing source values.",
        border=False,
        search=False,
        page_size=0,
        columns=[
            col.text("series").bold(),
            col.text("unit"),
            col.integer("observations"),
            col.integer("measures"),
            col.text("first_crop_year"),
            col.text("last_crop_year"),
            col.integer("conflicts"),
        ],
    )
    return


@app.cell
def series_control(coverage_rows, mo, series_names):
    category_options = {
        series_names.get(row["category"], row["category"]): row["category"]
        for row in coverage_rows
    }
    category_picker = mo.ui.dropdown(
        options=category_options,
        value="Raw sugar production"
        if "Raw sugar production" in category_options
        else next(iter(category_options)),
        label="Series",
    )
    category_picker
    return (category_picker,)


@app.cell
def measure_control(category_picker, connection, mo):
    measures = query_rows(
        connection,
        """
        SELECT DISTINCT measure FROM sra_monthly WHERE category = $category
        ORDER BY measure NULLS FIRST
    """,
        {"category": category_picker.value},
    )
    measure_options = {
        row["measure"] or "Unlabelled / not applicable": row["measure"]
        for row in measures
    }
    default_measure = (
        "composite" if "composite" in measure_options else next(iter(measure_options))
    )
    measure_picker = mo.ui.dropdown(
        options=measure_options, value=default_measure, label="Measure"
    )
    measure_picker
    return (measure_picker,)


@app.cell
def filtered_data(
    category_picker,
    connection,
    measure_picker,
    prepare_views,
    series_units,
):
    parameters = {"category": category_picker.value, "measure": measure_picker.value}
    selection_sql = (
        "WHERE category = $category AND measure IS NOT DISTINCT FROM $measure"
    )
    monthly_rows = query_rows(
        connection, "SELECT * FROM sra_monthly " + selection_sql, parameters
    )
    wide_rows = query_rows(
        connection, "SELECT * FROM sra_monthly_wide " + selection_sql, parameters
    )
    printed_rows = query_rows(
        connection,
        "SELECT * FROM sra_totals "
        + selection_sql
        + " ORDER BY crop_year DESC, kind, row_label",
        parameters,
    )
    seasons, monthly = prepare_views(
        monthly_rows, wide_rows, category_picker.value.endswith("prices")
    )
    selected_unit = series_units.get(category_picker.value, "See source")
    return monthly, printed_rows, seasons, selected_unit


@app.cell
def tables(EvidentialTable, col, label, mo):
    season_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Crop-year overview",
            select="crop_year",
            search=False,
            page_size=0,
            border=False,
            columns=[
                col.text("crop_year").bold(),
                col.text("coverage").title("Months").align("center"),
                col.bar(
                    "metric",
                    format="num0",
                    label=label.auto_position("outside end"),
                    color="#3b827b",
                ),
                col.integer("conflicts"),
                col.sparkline(
                    "monthly",
                    type="line",
                    title="September → August",
                    width=240,
                    height=30,
                    y_fmt="num1",
                ),
            ],
        )
    )
    monthly_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Monthly detail",
            search=False,
            sortable=False,
            page_size=0,
            border=False,
            columns=[
                col.text("period"),
                col.bar(
                    "value",
                    format="num1",
                    label=label.auto_position("outside end"),
                    color="#3b827b",
                ),
                col.number("previous", format="num1").title("Previous crop year"),
                col.bar(
                    "change",
                    format="num1",
                    center=True,
                    color="#3b827b",
                    color_negative="#c64f4f",
                    label=label.auto_position("outside end"),
                ),
                col.percent("change_pct", decimals=1).title("Change %").red_negatives(),
                col.integer("n_sources").title("Sources"),
                col.integer("n_values").title("Distinct values"),
                col.percent("rel_spread", decimals=1).title("Source spread"),
                col.text("status"),
            ],
        )
    )
    printed_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Printed totals and averages",
            search=False,
            page_size=0,
            border=False,
            empty_message="No printed total or average for this crop year and measure",
            caption="Labels are retained verbatim. Rows may describe different quantities (including area); they are never added together or automatically matched to a monthly summary.",
            columns=[
                col.text("crop_year"),
                col.text("kind"),
                col.text("row_label"),
                col.number("value", format="num2"),
                col.integer("n_votes").title("Source votes"),
            ],
        )
    )
    mo.vstack(
        [
            season_table,
            monthly_table,
            mo.accordion(
                {"Printed totals and averages · selected crop year": printed_table}
            ),
        ],
        gap=2,
    )
    return monthly_table, printed_table, season_table


@app.cell
def update_seasons(
    category_picker,
    measure_picker,
    season_table,
    seasons,
    selected_unit,
    series_names,
):
    is_price = category_picker.value.endswith("prices")
    with season_table.widget.hold_sync():
        season_table.widget.set_data(seasons)
        season_table.widget.set_column(
            "metric",
            title="Monthly mean" if is_price else "Observed-month total",
            fmt="num1" if is_price else "num0",
        )
        season_table.widget.update_options(
            title=series_names.get(category_picker.value, category_picker.value),
            subtitle=f"{selected_unit} · {measure_picker.value or 'Unlabelled / not applicable'} · Click a crop year; the latest is shown initially.",
            caption="Monthly sparkline: September → August. Gaps remain blank; partial coverage is not an annual estimate. Resolved source conflicts remain included.",
        )
        if season_table.widget.selected not in {row["crop_year"] for row in seasons}:
            season_table.widget.selected = None
    return


@app.cell
def selection(season_table):
    selected_crop_year = season_table.widget.selected
    return (selected_crop_year,)


@app.cell
def update_detail(
    monthly,
    monthly_table,
    printed_rows,
    printed_table,
    seasons,
    selected_crop_year,
    selected_unit,
):
    crop_year = (
        selected_crop_year
        if selected_crop_year in monthly
        else (seasons[0]["crop_year"] if seasons else None)
    )
    with monthly_table.widget.hold_sync():
        monthly_table.widget.set_data(monthly.get(crop_year, []))
        monthly_table.widget.update_options(
            title=f"Monthly detail · {crop_year}" if crop_year else "Monthly detail",
            subtitle=f"{selected_unit} · Compared with the same month in the immediately preceding crop year.",
            caption="Source spread is (maximum − minimum) / |resolved value|, as supplied by dbt. Percentage change is blank when the previous value is missing or zero.",
        )
    printed_table.widget.set_data(
        [row for row in printed_rows if row["crop_year"] == crop_year]
    )
    return


@app.cell(hide_code=True)
def attribution(dataset_path, mo):
    mo.md(f"""
    Source: **Sugar Regulatory Administration, Republic of the Philippines**.
    Reading `sra_monthly.parquet`, `sra_monthly_wide.parquet` and
    `sra_totals.parquet` from `{dataset_path.name}/data/processed/`.

    dbt resolves values by document majority vote, breaking ties using the most
    recently published document. A source disagreement is retained as a flag;
    the notebook does not re-resolve or discard it. A single source is not
    independent corroboration. The product defines spread as zero when its
    resolved value is zero.

    Millsite price labels remain heuristic. Metro Manila's average/prevailing
    table distinction is not represented in the product; its unit label is
    coarse and depends on the measure. See the dataset's README and original
    PDFs for these extraction limitations. The notebook displays the product;
    it does not rerun or certify dbt tests.

    Set `SRA_DATASET` to use another build. No source PDFs or parsed-layer files
    are needed, downloaded or modified by this notebook.
    """)
    return


if __name__ == "__main__":
    app.run()
