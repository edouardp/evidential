# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "pyarrow>=17", "evidential"]
# ///
"""OECD economic cycles and source-series explorer using the local Parquet product.

Set OECD_DATASET to override ~/datasets/oecd. No downloads or fabricated fallback.
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

    from evidential import EvidentialTable, col, label, settings

    return EvidentialTable, Path, col, duckdb, label, mo, os, settings


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # OECD · economic cycles

    The recession timeline uses **quarter-on-quarter real GDP growth**, calendar
    and seasonally adjusted, from the local OECD data product. It opens at
    **1960–2019**, following the reference chart; move the year range to explore
    earlier or later observations. Click a country for the quarterly evidence.

    **Economic context:** GDP in current-price PPP US dollars, gross government
    debt/GDP and fiscal balance/GDP use the **last selected year**, without
    filling gaps from other years. Recession share uses only observed quarters;
    hover it for coverage. Region is a broad geographic display mapping in this
    notebook, not an OECD dimension. GDP per person would require population
    data, which this local product does not contain.

    **Red:** all quarters in a run of at least two consecutive contractions.
    **Blue:** observed quarters outside those runs, including isolated declines.
    **Grey:** missing growth observations. Gaps and zero growth break a run.
    Classification uses the complete local history before clipping the chart,
    so a year-range boundary cannot erase a neighbouring contraction.

    This is a retrospective technical-recession rule, not official recession
    dating. Historical revisions can change the bands compared with an older
    graphic. Estimated/provisional values retain their OECD status below.
    [Methodology: ONS](https://www.ons.gov.uk/economy/grossdomesticproductgdp/methodologies/communicatingtheukeconomiccycle).

    The source-series browser also surfaces the product's GDP components,
    government finance, debt and balance-of-payments datasets. Individual
    observations keep their units and dimensions; no unlike series are summed.
    """)
    return


@app.cell
def queries(Path, col, duckdb):
    sql_dir = Path(__file__).parent / "sql"
    gdp_sql = (sql_dir / "58_oecd_gdp.sql").read_text()
    quarter_sql = (sql_dir / "58_oecd_quarters.sql").read_text()
    timeline_sql = (sql_dir / "58_oecd_timeline.sql").read_text()
    context_sql = {
        "gdp_quarterly_usd": (sql_dir / "58_oecd_gdp_levels.sql").read_text(),
        "gov_finance": (sql_dir / "58_oecd_fiscal.sql").read_text(),
    }
    source_names = {
        "gdp_growth": "Real GDP and component growth",
        "gdp_quarterly_usd": "GDP and components · US dollars, PPP",
        "gov_finance": "Government finance",
        "public_debt_q": "Quarterly public sector debt",
        "bop": "Balance of payments",
        "iip": "International investment position",
        "tis": "International trade in services",
    }
    state_names = {
        "recession": "In technical recession",
        "other": "Not in technical recession",
        "missing": "No data",
    }

    def load_oecd(root):
        con = duckdb.connect()
        available = {}
        inventory = []
        for name, title in {
            **source_names,
            "dataflows": "OECD dataflow catalogue",
        }.items():
            path = root / "data" / "processed" / f"{name}.parquet"
            if not path.is_file():
                continue
            view = f"oecd_{name}"
            con.read_parquet(str(path)).create_view(view)
            fields = {row[0] for row in con.execute(f"DESCRIBE {view}").fetchall()}
            period_sql = (
                "min(period_start), max(period_start)"
                if "period_start" in fields
                else "NULL, NULL"
            )
            count, first, last = con.execute(
                f"SELECT count(*), {period_sql} FROM {view}"
            ).fetchone()
            inventory.append(
                {
                    "dataset": title,
                    "file": path.name,
                    "observations": count,
                    "first_period": first,
                    "last_period": last,
                }
            )
            if name in source_names:
                available[name] = {"title": title, "fields": fields}
        con.execute("CREATE TEMP VIEW gdp_observed AS " + gdp_sql)
        duplicate = con.sql(
            "SELECT country_code, period_start FROM gdp_observed GROUP BY ALL HAVING count(*) > 1 LIMIT 1"
        ).fetchone()
        if duplicate:
            raise ValueError(
                f"Multiple GDP growth series for one country/quarter: {duplicate}"
            )
        con.execute("CREATE TEMP TABLE gdp_quarters AS " + quarter_sql)
        con.execute("""
            CREATE TEMP TABLE context_observed (
                country_code VARCHAR, year INTEGER, metric VARCHAR, value DOUBLE,
                status VARCHAR, PRIMARY KEY (country_code, year, metric)
            )
        """)
        for source, query in context_sql.items():
            if source in available:
                con.execute("INSERT INTO context_observed " + query)
        return con, available, inventory

    def make_timeline_columns(start_year, end_year):
        return [
            col.text("region").bold().repeat_values(False),
            col.text("country").bold().align("right"),
            col.strip(
                "periods",
                title="Quarterly real GDP",
                segmented=False,
                colors={
                    "recession": "#c52228",
                    "other": "#92cee0",
                    "missing": "#d3d3d3",
                },
            )
            .fmt("num2" if end_year - start_year < 4 else "0")
            .scale(domain=(start_year, end_year + 1), axis=True, axis_position="top")
            .legend(state_names),
            col.number("gdp_ppp", title=f"GDP\u00a0·\u00a0{end_year}\nPPP\u00a0US$")
            .fmt("compact4")
            .tooltip("@gdp_detail"),
            col.number("debt_ratio", title=f"Debt/GDP\n{end_year}")
            .fmt("pct1")
            .tooltip("@debt_detail"),
            col.number("fiscal_ratio", title=f"Fiscal/GDP\n{end_year}")
            .fmt("pct1")
            .neg()
            .tooltip("@fiscal_detail"),
            col.number("recession_share", title="Recession\nshare")
            .fmt("pct1")
            .color(scale=["#fff5f5", "#ef9a9a", "#9f1620"], min=0, max=1)
            .tooltip("@coverage"),
        ]

    def query_timeline(con, start_year, end_year, aggregates=False):
        return con.execute(
            timeline_sql,
            {"start_year": start_year, "end_year": end_year, "aggregates": aggregates},
        ).to_arrow_table()

    def query_quarters(con, country_code, start_year, end_year):
        return con.execute(
            """
            SELECT year || '-Q' || quarter AS period, growth_percent / 100.0 AS growth,
                   CASE category WHEN 'recession' THEN 'Technical recession'
                                 WHEN 'missing' THEN 'No data' ELSE 'Other observed quarter' END AS state,
                   coalesce(obs_status_label, obs_status, 'No observation') AS status
            FROM gdp_quarters WHERE country_code = ? AND year BETWEEN ? AND ?
            ORDER BY period_start DESC
        """,
            [country_code, start_year, end_year],
        ).to_arrow_table()

    def browse_source(
        con, available, name, country_code, start_year, end_year, limit=500
    ):
        if name not in available:
            raise ValueError("Choose an available OECD source")
        fields = available[name]["fields"]
        # Names come from the fixed registry; all user-controlled filters are bound.
        observations = (
            con.execute(
                f"""
            SELECT *, count(*) OVER () AS matching_observations FROM oecd_{name}
            WHERE ref_area = ? AND year BETWEEN ? AND ?
            ORDER BY period_start DESC, time_period LIMIT ?
        """,
                [country_code, start_year, end_year, limit],
            )
            .to_arrow_table()
            .to_pylist()
        )
        dimensions = [
            field
            for field in sorted(fields)
            if field.endswith("_label")
            and field
            not in {
                "ref_area_label",
                "freq_label",
                "unit_measure_label",
                "adjustment_label",
                "obs_status_label",
                "decimals_label",
                "unit_mult_label",
                "conf_status_label",
            }
        ]
        for row in observations:
            row["period"] = row["time_period"]
            row["series"] = (
                row.get("transaction_label")
                or row.get("measure_label")
                or row.get("fs_entry_label")
                or available[name]["title"]
            )
            row["value"] = (
                None
                if row["obs_value"] is None
                else row["obs_value"] * row["multiplier"]
            )
            row["value_format"] = (
                "num2"
                if row.get("unit_measure", "").startswith(("PC", "PT_"))
                else "compact4"
            )
            row["unit"] = row.get("unit_measure_label") or row.get("unit_measure")
            row["frequency"] = row.get("freq_label") or row.get("freq")
            row["adjustment_name"] = row.get("adjustment_label") or row.get(
                "adjustment"
            )
            row["status"] = row.get("obs_status_label") or row.get("obs_status")
            row["dimensions"] = "\n".join(
                f"{field.removesuffix('_label').replace('_', ' ').title()}: {row[field]}"
                for field in dimensions
                if row.get(field)
            )
        return observations

    return (
        browse_source,
        load_oecd,
        make_timeline_columns,
        query_quarters,
        query_timeline,
    )


@app.cell
def local_data(Path, load_oecd, mo, os):
    oecd_root = Path(os.environ.get("OECD_DATASET", "~/datasets/oecd")).expanduser()
    mo.stop(
        not (oecd_root / "data/processed/gdp_growth.parquet").is_file(),
        mo.md(
            "Build the local OECD Parquet product first, or set `OECD_DATASET` to its checkout. "
            "Expected `data/processed/gdp_growth.parquet`."
        ),
    )
    oecd_connection, oecd_sources, oecd_inventory = load_oecd(oecd_root)
    first_year, last_year = oecd_connection.sql(
        "SELECT min(year), max(year) FROM gdp_quarters"
    ).fetchone()
    mo.stop(
        first_year is None,
        mo.md(
            "No matching quarterly, seasonally adjusted real GDP growth series found."
        ),
    )
    country_names = dict(
        oecd_connection.sql(
            "SELECT country_code, any_value(country) FROM gdp_quarters GROUP BY country_code ORDER BY 2"
        ).fetchall()
    )
    return (
        country_names,
        first_year,
        last_year,
        oecd_connection,
        oecd_inventory,
        oecd_sources,
    )


@app.cell
def controls(first_year, last_year, mo):
    initial_start = max(1960, first_year)
    initial_end = max(initial_start, min(2019, last_year))
    years = mo.ui.range_slider(
        start=first_year,
        stop=max(first_year + 1, last_year),
        step=1,
        value=(initial_start, initial_end),
        show_value=True,
        debounce=True,
        label="Years",
        full_width=True,
    )
    include_aggregates = mo.ui.checkbox(
        value=False, label="Include regional aggregates"
    )
    mo.vstack([years, include_aggregates])
    return include_aggregates, years


@app.cell
def timeline(
    EvidentialTable,
    country_names,
    make_timeline_columns,
    mo,
    settings,
):
    cycle_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=make_timeline_columns(1960, 2019),
            title="Technical recessions, 1960–2019",
            subtitle="Select a country for quarterly growth and source observations",
            caption="Source: OECD local extract · retrospective two-quarter rule · annual context uses the final selected year; missing values stay missing · hover values for units and coverage",
            select="country_code",
            settings=settings(
                border=False,
                row_lines=False,
                row_shading=False,
                page_size=0,
                search=True,
            ),
        )
    )
    cycle_table.widget.selected = (
        "NZL" if "NZL" in country_names else next(iter(country_names))
    )
    cycle_table
    return (cycle_table,)


@app.cell
def update_timeline(
    cycle_table,
    include_aggregates,
    make_timeline_columns,
    oecd_connection,
    query_timeline,
    years,
):
    start_year, end_year = map(int, years.value)
    timeline_data = query_timeline(
        oecd_connection, start_year, end_year, include_aggregates.value
    )
    visible_codes = set(timeline_data.column("country_code").to_pylist())
    with cycle_table.widget.hold_sync():
        cycle_table.widget.set_data(
            timeline_data, columns=make_timeline_columns(start_year, end_year)
        )
        cycle_table.widget.update_options(
            title=f"Technical recessions, {start_year}–{end_year}"
        )
        if cycle_table.widget.selected not in visible_codes:
            cycle_table.widget.selected = None
    return end_year, start_year, visible_codes


@app.cell
def selected_country(cycle_table, visible_codes):
    country_selection = cycle_table.value["selected"]
    selected_code = country_selection if country_selection in visible_codes else None
    return (selected_code,)


@app.cell(hide_code=True)
def detail_doc(mo):
    mo.md("""
    ## The quarterly evidence

    Click a country above. Growth is relative to the previous quarter, not the
    same quarter a year earlier. Missing quarters remain missing. A one-quarter
    decline can be blue; two or more adjacent negative quarters form a red run.
    Status is copied from the local OECD observation. Values are not rounded
    before classifying their sign.
    """)
    return


@app.cell
def quarterly_table(EvidentialTable, col, label, mo, settings):
    quarterly = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.text("period"),
                col.bar(
                    "growth",
                    center=True,
                    color="#92cee0",
                    color_negative="#c52228",
                    label=label.fmt("pct2").auto_position("outside end"),
                ),
                col.text("state"),
                col.text("status"),
            ],
            title="Quarterly real GDP growth",
            empty_message="Select a country in the timeline",
            settings=settings(border=False, row_lines=False, page_size=12),
        )
    )
    quarterly
    return (quarterly,)


@app.cell
def source_control(mo, oecd_sources):
    source_flow = mo.ui.dropdown(
        options={info["title"]: name for name, info in oecd_sources.items()},
        value=oecd_sources["gdp_growth"]["title"],
        label="Browse source dataset",
    )
    source_flow
    return (source_flow,)


@app.cell
def observations_table(EvidentialTable, col, mo, settings):
    observations_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.text("period").fmt("@"),
                col.text("series").tooltip("@dimensions"),
                col.number("value").fmt_column("value_format"),
                col.text("unit"),
                col.text("frequency"),
                col.text("adjustment_name", title="Adjustment"),
                col.text("status"),
            ],
            title="Published observations",
            empty_message="Select a country in the timeline",
            settings=settings(border=False, row_lines=False, page_size=12, search=True),
        )
    )
    observations_table
    return (observations_table,)


@app.cell
def update_details(
    browse_source,
    country_names,
    end_year,
    observations_table,
    oecd_connection,
    oecd_sources,
    quarterly,
    query_quarters,
    selected_code,
    source_flow,
    start_year,
):
    quarter_rows = query_quarters(oecd_connection, selected_code, start_year, end_year)
    source_rows = browse_source(
        oecd_connection,
        oecd_sources,
        source_flow.value,
        selected_code,
        start_year,
        end_year,
    )
    country_title = country_names.get(selected_code, "Select a country")
    quarterly.widget.set_data(quarter_rows)
    quarterly.widget.update_options(
        title=f"{country_title} · Quarterly real GDP growth"
    )
    observations_table.widget.set_data(source_rows)
    matching_count = source_rows[0]["matching_observations"] if source_rows else 0
    observations_table.widget.update_options(
        title=f"{country_title} · {oecd_sources[source_flow.value]['title']}",
        caption=f"{len(source_rows):,} of {matching_count:,} observations · latest periods first · no aggregation · hover Series for dimensions · values include the source multiplier",
    )
    return


@app.cell
def inventory(EvidentialTable, col, mo, oecd_inventory, settings):
    mo.vstack(
        [
            mo.md("## Available local data products"),
            EvidentialTable(
                oecd_inventory,
                columns=[
                    col.text("dataset").bold(),
                    col.text("file"),
                    col.integer("observations"),
                    col.date("first_period"),
                    col.date("last_period"),
                ],
                caption="Separate flow extracts; the combined bop_family file repeats the BOP/IIP/TIS data and is intentionally omitted.",
                settings=settings(border=False, row_lines=False, page_size=0),
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
