# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "pyarrow>=17", "evidential"]
# ///
"""Explore the local aws-cur-example processed data product without copying it.

Set AWS_CUR_DATASET to override ~/datasets/aws-cur-example.
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

    from evidential import DimensionGrid, EvidentialTable, col, label, settings

    return (
        DimensionGrid,
        EvidentialTable,
        Path,
        col,
        duckdb,
        label,
        mo,
        os,
        settings,
    )


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # AWS cost and usage explorer

    Explore the **processed CUR workshop data** in `~/datasets/aws-cur-example`.
    Set `AWS_CUR_DATASET` to use another checkout of that data product; the input
    is `data/processed/cur_line_items.parquet`. No sample charges are generated.

    Select multiple values per dimension. Values within a dimension combine
    with **OR**, dimensions with **AND**. Start with **AmazonRDS** in Service;
    Usage type then shows only its matching categories. Use the header search,
    slim vertical scrollbars and horizontal arrows to explore the nine filters.

    **Cost basis:** amortized cost follows the product's `build.py`: reservation
    effective cost for `DiscountedUsage`, otherwise unblended cost. Existing fee
    rows are retained. Unblended cost is shown alongside it for comparison.
    Quantities are grouped by their billing unit, never added across units.
    """)
    return


@app.cell
def queries(Path, duckdb):
    sql_directory = Path(__file__).parent / "sql"
    cur_sql = {
        name: (sql_directory / f"57_cur_{name}.sql").read_text()
        for name in ["source", "drivers", "details", "summary"]
    }
    cur_dimensions = {
        "service": "Service",
        "usage_type": "Usage type",
        "region": "Region",
        "account": "Account",
        "charge_type": "Charge type",
        "environment": "Environment",
        "workload": "Workload",
        "cost_center": "Cost centre",
        "billing_month": "Billing month",
    }

    def load_cur(path):
        con = duckdb.connect()
        con.read_parquet(str(path)).create_view("cur_source")
        con.execute("CREATE TEMP VIEW cur AS " + cur_sql["source"])
        # Additive costs at the complete selected dimension grain preserve all
        # cross-filter relationships while reducing the widget's in-memory data.
        fields = ", ".join(cur_dimensions)
        con.execute(
            f"CREATE TEMP TABLE cur_facets AS SELECT {fields}, "
            "sum(amortized_cost) AS cost FROM cur GROUP BY ALL"
        )
        return con

    def query_cur(con, predicate="TRUE", parameters=(), detail_limit=500):
        if detail_limit not in (250, 500, 1000, 2500):
            raise ValueError("Choose a supported detail row limit")
        results = {}
        for name in ["summary", "drivers", "details"]:
            arguments = (
                [*parameters, detail_limit] if name == "details" else list(parameters)
            )
            result = con.execute(
                cur_sql[name].replace("/* filters */", predicate), arguments
            )
            if name == "summary":
                results[name] = dict(
                    zip(
                        [column[0] for column in result.description],
                        result.fetchone(),
                        strict=True,
                    )
                )
            else:
                results[name] = result.to_arrow_table()
        return results

    return cur_dimensions, load_cur, query_cur


@app.cell
def local_data(Path, load_cur, mo, os):
    cur_root = Path(
        os.environ.get("AWS_CUR_DATASET", "~/datasets/aws-cur-example")
    ).expanduser()
    cur_path = cur_root / "data" / "processed" / "cur_line_items.parquet"
    mo.stop(
        not cur_path.is_file(),
        mo.md(
            "Build the local `aws-cur-example` data product first, or set `AWS_CUR_DATASET` "
            "to its checkout. Expected `data/processed/cur_line_items.parquet`."
        ),
    )
    cur_connection = load_cur(cur_path)
    currencies = cur_connection.sql(
        "SELECT DISTINCT currency FROM cur WHERE currency IS NOT NULL"
    ).fetchall()
    mo.stop(
        currencies != [("USD",)],
        mo.md(
            "This explorer expects a USD CUR product; currencies cannot be summed together."
        ),
    )
    source_summary = cur_connection.sql(
        "SELECT count(*) AS line_items, min(usage_date), max(usage_date) FROM cur"
    ).fetchone()
    mo.md(
        f"**{source_summary[0]:,} source line items · {source_summary[1]} to {source_summary[2]} · USD**"
    )
    return (cur_connection,)


@app.cell(hide_code=True)
def drivers_doc(mo):
    mo.md("""
    ## What drives the cost?

    Each row combines a **service, usage type, region, charge type and unit**.
    Share is of the complete selected cost. Daily sparklines span the selected
    date range, filling days without charges with zero. These totals use every
    matching line item; the detail limit below does not affect them.
    """)
    return


@app.cell
def cost_filters(DimensionGrid, cur_connection, cur_dimensions, mo):
    cur_slicer = mo.ui.anywidget(
        DimensionGrid(
            cur_connection.table("cur_facets"),
            dimensions=cur_dimensions,
            metric="cost",
            format="usd2",
            height=300,
            dimension_width=180,
            title="Filter cost and usage",
            subtitle="Ranked by amortized cost · selections filter every result below",
            color="#2c83b8",
        )
    )
    cur_slicer
    return (cur_slicer,)


@app.cell
def summary_cards(cur_summary, mo):
    mo.hstack(
        [
            mo.stat(f"${cur_summary['amortized_cost']:,.2f}", label="Amortized cost", bordered=True),
            mo.stat(f"${cur_summary['unblended_cost']:,.2f}", label="Unblended cost", bordered=True),
            mo.stat(f"{cur_summary['line_items']:,}", label="Matching line items", bordered=True),
            mo.stat(f"{cur_summary['services']:,}", label="Services", bordered=True),
        ],
        widths="equal",align="center", 
    )
    return


@app.cell
def drivers_table(EvidentialTable, col, label, mo, settings):
    cost_drivers = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.text("service").bold(),
                col.text("usage_type"),
                col.text("region"),
                col.text("charge_type"),
                col.number("quantity", format="num2"),
                col.text("unit"),
                col.bar(
                    "amortized_cost",
                    label=label.fmt("usd2").auto_position("outside end"),
                ),
                col.currency("unblended_cost", decimals=2),
                col.percent("share", decimals=1),
                col.sparkline(
                    "daily_cost",
                    type="area",
                    color="#2c83b8",
                    title="Daily cost",
                    width=160,
                    y_fmt="usd2",
                ),
            ],
            settings=settings(border=False, row_lines=False, page_size=15, search=True),
            title="Cost drivers",
            caption="All matching charges · quantities stay within their billing unit · USD",
        )
    )
    cost_drivers
    return (cost_drivers,)


@app.cell
def detail_control(mo):
    detail_limit = mo.ui.dropdown(
        options={f"{value:,}": value for value in [250, 500, 1000, 2500]},
        value="500",
        label="Most expensive matching line items to load",
    )
    detail_limit
    return (detail_limit,)


@app.cell
def detail_table(EvidentialTable, col, mo, settings):
    cur_details = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.date("usage_date"),
                col.text("service").bold(),
                col.currency("amortized_cost", format="$#,##0.0000"),
                col.currency("unblended_cost", format="$#,##0.0000"),
                col.text("usage_type"),
                col.text("region"),
                col.text("charge_type"),
                col.text("account").fmt("000000000000"),
                col.text("resource", wrap=True),
                col.number("quantity", format="num4"),
                col.text("unit"),
                col.text("description", wrap=True),
            ],
            settings=settings(border=False, row_lines=False, page_size=15, search=True),
            title="Matching line items",
            caption="Highest amortized cost first · row limit applies only here · search and CSV cover loaded rows · USD",
        )
    )
    cur_details
    return (cur_details,)


@app.cell
def update_results(
    cost_drivers,
    cur_connection,
    cur_details,
    cur_slicer,
    detail_limit,
    query_cur,
):
    # Read control values here; keep both tables and the slicer persistent.
    cur_selection = cur_slicer.value["selected"]
    cur_predicate, cur_parameters = cur_slicer.widget.where()
    cur_results = query_cur(
        cur_connection, cur_predicate, cur_parameters, detail_limit.value
    )
    cost_drivers.widget.set_data(cur_results["drivers"])
    cur_details.widget.set_data(cur_results["details"])
    cur_summary = cur_results["summary"]
    return (cur_summary,)


if __name__ == "__main__":
    app.run()
