# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential", "wigglystuff>=0.5.36"]
# ///
"""AdventureWorks company report over the local Parquet product.

Run uv run marimo edit notebooks/59_adventureworks_company_report.py.
ADVENTUREWORKS_DATASET accepts the dataset checkout or its Parquet directory.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import datetime as dt
    import json
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    from wigglystuff import ObservablePlot

    from evidential import EvidentialTable, col, label, rows

    return (
        EvidentialTable,
        ObservablePlot,
        Path,
        col,
        dt,
        duckdb,
        json,
        label,
        mo,
        os,
        rows,
    )


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # AdventureWorks · company report

    **Commercial performance of the bicycle manufacturer.** Start with the
    latest complete calendar year, then compare markets, product mix and
    customer relationships. The year and channel controls update the whole report.

    Amounts are in **US dollars**, on shipped orders, attributed to their order
    date. Net sales exclude tax and freight. Gross contribution is a standard-cost
    estimate, before freight, overheads, selling expenses and tax—not net profit.
    """)
    return


@app.cell
def queries(Path, dt, duckdb):
    report_directory = Path(__file__).parent
    sql_directory = report_directory / "sql"
    names = ["scorecard", "monthly", "markets", "products", "customers", "accounts", "fulfilment", "countries"]
    report_sql = {name: (sql_directory / f"59_aw_{name}.sql").read_text() for name in ["source", "scope", *names]}
    required = [
        "SalesOrderHeader",
        "SalesOrderDetail",
        "Product",
        "ProductCostHistory",
        "ProductCategory",
        "ProductSubcategory",
        "Customer",
        "Store",
        "SalesTerritory",
        "CountryRegion",
        "ShipMethod",
    ]

    def parquet_directory(root):
        for candidate in [root / "data/processed/parquet", root / "parquet", root]:
            if all((candidate / f"{name}.parquet").is_file() for name in required):
                return candidate
        return None

    def records(connection, statement, parameters=None):
        cursor = connection.execute(statement, parameters or {})
        fields = [column[0] for column in cursor.description]
        return [dict(zip(fields, row, strict=True)) for row in cursor.fetchall()]

    def load_adventureworks(root):
        directory = parquet_directory(root)
        if directory is None:
            raise FileNotFoundError("Expected the AdventureWorks Parquet product; see ADVENTUREWORKS_DATASET.")
        connection = duckdb.connect()
        for name in required:
            connection.read_parquet(str(directory / f"{name}.parquet")).create_view(name)
        connection.execute(report_sql["source"])
        header_orders = connection.sql("SELECT count(*) FROM SalesOrderHeader WHERE Status=5").fetchone()[0]
        order_count = connection.sql("SELECT count(*) FROM aw_orders").fetchone()[0]
        if not order_count or header_orders != order_count:
            connection.close()
            raise ValueError("Every shipped order must have sales lines, and order/dimension keys must be unique.")
        return connection

    def period_window(connection, year):
        first, last = connection.sql("SELECT min(order_date), max(order_date) FROM aw_orders").fetchone()
        if not first.year <= int(year) <= last.year:
            raise ValueError("Choose a year inside the source coverage")
        start, end = max(first, dt.date(int(year), 1, 1)), min(last, dt.date(int(year), 12, 31))
        prior_start, prior_end = connection.execute(
            "SELECT (?::DATE - INTERVAL '1 year')::DATE, (?::DATE - INTERVAL '1 year')::DATE", [start, end]
        ).fetchone()
        return {
            "start": start,
            "end": end,
            "prior_start": prior_start,
            "prior_end": prior_end,
            "comparable": prior_start >= first and prior_end <= last,
        }

    def query_report(connection, year, channel):
        if channel not in ("All channels", "Online", "Sales-assisted"):
            raise ValueError("Choose a supported sales channel")
        window = period_window(connection, year)
        parameters = {**window, "channel": channel}
        result = {name: records(connection, report_sql["scope"] + report_sql[name], parameters) for name in names}
        result["quality"] = records(
            connection,
            report_sql["scope"]
            + """
            SELECT coalesce(sum(net_sales), 0) AS net_sales,
                   coalesce(sum(fallback_sales), 0) AS fallback_sales,
                   coalesce(sum(missing_cost_sales), 0) AS missing_cost_sales,
                   coalesce(sum(net_sales - header_subtotal), 0) AS header_rounding_difference
            FROM current_orders
        """,
            parameters,
        )[0]
        return result, window

    return (
        load_adventureworks,
        parquet_directory,
        query_report,
        report_directory,
    )


@app.cell
def local_data(Path, dt, load_adventureworks, mo, os, parquet_directory):
    dataset_path = Path(os.environ.get("ADVENTUREWORKS_DATASET", "~/datasets/adventureworks")).expanduser()
    mo.stop(
        parquet_directory(dataset_path) is None,
        mo.md(
            "Build the local AdventureWorks Parquet product first, or set "
            "`ADVENTUREWORKS_DATASET` to its checkout or Parquet directory. "
            "The report reads the files in place and never modifies them."
        ),
    )
    con = load_adventureworks(dataset_path)
    first_date, last_date = con.sql("SELECT min(order_date), max(order_date) FROM aw_orders").fetchone()
    report_years = list(range(first_date.year, last_date.year + 1))
    complete_years = [
        year for year in report_years if first_date <= dt.date(year, 1, 1) and last_date >= dt.date(year, 12, 31)
    ]
    default_year = max(complete_years or report_years)
    return con, default_year, first_date, last_date, report_years


@app.cell
def period_controls(default_year, mo, report_years):
    year_picker = mo.ui.dropdown(
        options={str(year): year for year in reversed(report_years)}, value=str(default_year), label="Reporting year"
    )
    channel_picker = mo.ui.dropdown(
        options=["All channels", "Online", "Sales-assisted"], value="All channels", label="Sales channel"
    )
    mo.hstack([year_picker, channel_picker], justify="start", gap=2)
    return channel_picker, year_picker


@app.cell
def report_results(channel_picker, con, query_report, year_picker):
    report_data, window = query_report(con, year_picker.value, channel_picker.value)
    period_label = f"{window['start']:%d %b %Y} – {window['end']:%d %b %Y}"
    comparison_label = (
        f"Prior year: {window['prior_start']:%d %b %Y} – {window['prior_end']:%d %b %Y}"
        if window["comparable"]
        else "Prior-year comparison unavailable: source coverage is incomplete"
    )
    return comparison_label, period_label, report_data


@app.cell(hide_code=True)
def executive_readout(
    channel_picker,
    comparison_label,
    mo,
    period_label,
    report_data,
):
    metrics = {row["metric"]: row for row in report_data["scorecard"]}
    net_sales = metrics["Net sales"]
    growth_text = (
        f"{net_sales['change']:+.1%} against the same dates last year"
        if net_sales["change"] is not None
        else "no comparable prior-year growth figure"
    )
    leader = report_data["countries"][0] if report_data["countries"] else None
    leader_text = (
        f"The largest country market is **{leader['country']}**, with "
        f"**{leader['net_sales'] / net_sales['current']:.1%}** of net sales."
        if leader and net_sales["current"]
        else "No shipped sales match this selection."
    )
    mo.md(f"""
    ## 1 · Executive view

    **{period_label} · {channel_picker.value}.** {comparison_label}.

    Net sales of **${net_sales["current"]:,.0f}**, with {growth_text}.
    {leader_text}

    Margin change is shown in **percentage points**; other changes are relative
    percentages. A dash means unavailable, not zero. Partial periods are not annualized.
    """)
    return


@app.cell
def tables(EvidentialTable, col, label, rows):
    def margin_column():
        return col.percent("margin", decimals=1).color(
            scale=["red", "#ffffff44", "green"], min=-0.3, max=0.7, midpoint=0
        )

    def sales_column():
        return (
            col.bar(
                "net_sales",
                title="Net sales · prior-year dot",
                format="compact4",
                color="#39799b",
                label=label.fmt("compact4").auto_position("outside end"),
            )
            .point("prior_sales", color="#152e40", size=7, outline=False)
            .legend({"net_sales": "Selected period", "prior_sales": "Prior year"})
        )

    table_options = dict(border=False, row_lines=False, row_shading=True, download=True, page_size="all", null_text="—")
    report_tables = {
        "scorecard": EvidentialTable(
            [],
            columns=[
                col.text("metric").bold(),
                col.number("current").fmt_column("format"),
                col.number("previous").fmt_column("format"),
                col.number("change").fmt_column("change_format").neg(),
            ],
            title="At a glance",
            sortable=False,
            search=False,
            **table_options,
        ),
        "monthly": EvidentialTable(
            [],
            columns=[
                col.date("month", format="mmm"),
                sales_column(),
                col.bar(
                    "sales_change",
                    title="Change · USD",
                    center=True,
                    format="compact4",
                    color="@change_color",
                    label=label.fmt("compact4").auto_position("outside end"),
                ),
                col.stacked_bar(
                    "online_sales",
                    "assisted_sales",
                    normalize="percent",
                    labels="percent",
                    colors=["#39799b", "#d39b48"],
                    title="Channel mix",
                ).legend({"online_sales": "Online", "assisted_sales": "Sales-assisted"}),
                col.integer("orders"),
                margin_column(),
            ],
            title="Monthly trading",
            search=False,
            **table_options,
        ),
        "markets": EvidentialTable(
            [],
            columns=[
                col.text("territory").bold(),
                col.text("country"),
                sales_column(),
                col.percent("growth", decimals=1).neg(),
                margin_column(),
                col.integer("orders"),
                col.integer("customers"),
            ],
            row_layout=rows.group_by("region")
                           .section(collapsible=True, collapsed_summary=True)
                           .summary(
                               "Region subtotal",
                               values={"net_sales": "sum", "orders": "sum"},
                               label_style={"font_weight": "bold", "font_style": "italic"},
                           ),
            title="Territories by region",
            search=True,
            section_indent=1,
            freeze_columns=1,
            **table_options,
        ),
        "products": EvidentialTable(
            [],
            columns=[
                col.text("subcategory").bold(),
                sales_column(),
                col.percent("sales_share", decimals=1),
                margin_column(),
                col.integer("units"),
                col.integer("products"),
                col.percent("discount_rate", decimals=1),
                col.sparkline(
                    "monthly_sales",
                    x="date",
                    y="value",
                    y_fmt="usd0",
                    width=110,
                    height=24,
                    color="#39799b",
                    title="Monthly sales",
                ),
            ],
            row_layout=rows.group_by("category")
            .section(collapsible=True, collapsed_summary=True)
            .summary("Category total", values={"net_sales": "sum", "units": "sum"}),
            title="Product portfolio",
            search=True,
            section_indent=1,
            page_size=14,
            border=False,
            row_lines=False,
            row_shading=True,
            download=True,
            null_text="—",
        ),
        "customers": EvidentialTable(
            [],
            columns=[
                col.text("cohort").bold(),
                col.integer("customers"),
                col.integer("orders"),
                col.bar(
                    "net_sales",
                    format="compact4",
                    color="#39799b",
                    label=label.fmt("compact4").auto_position("outside end"),
                ),
                col.currency("sales_per_customer", decimals=0),
                col.number("orders_per_customer", format="num2"),
                margin_column(),
            ],
            title="Observed customer relationships",
            search=False,
            **table_options,
        ),
        "accounts": EvidentialTable(
            [],
            columns=[
                col.text("customer").bold(),
                col.text("territory"),
                sales_column(),
                col.percent("company_sales_share", decimals=1),
                col.integer("orders"),
                col.currency("average_order", decimals=0),
                margin_column(),
            ],
            title="Largest reseller accounts · top 15",
            search=True,
            row_numbers=True,
            empty_message="No reseller accounts in this period/channel.",
            **table_options,
        ),
        "fulfilment": EvidentialTable(
            [],
            columns=[
                col.text("ship_method").bold(),
                col.text("channel"),
                col.integer("orders"),
                col.integer("dispatched_orders"),
                col.number("median_days", format="num1"),
                col.number("p90_days", format="num1"),
                col.percent("dispatched_by_due", decimals=1),
                col.percent("freight_ratio", decimals=1),
            ],
            title="Dispatch and freight",
            search=False,
            **table_options,
        ),
    }
    return (report_tables,)


@app.cell
def map_widget(ObservablePlot, json, report_directory):
    world = json.loads((report_directory / "sample_data/adventureworks/world-110m.geojson").read_text())
    country_map = ObservablePlot(
        src=str(report_directory / "charts/59_aw_map.js"),
        variables={"world": world, "markets": []},
        width=1050,
        height=380,
        version="0.6.17",
    )
    return country_map, world


@app.cell
def update_report(
    comparison_label,
    country_map,
    period_label,
    report_data,
    report_tables,
    world,
):
    for name, table in report_tables.items():
        data = report_data[name]
        if name == "monthly":
            data = [{**row, "change_color": "#c4443b" if (row["sales_change"] or 0) < 0 else "#39799b"} for row in data]
        with table.hold_sync():
            table.set_data(data)
            table.options = {**table.options, "subtitle": f"{period_label} · {comparison_label}"}
    country_map.variables = {"world": world, "markets": report_data["countries"]}
    return


@app.cell
def scorecard_view(mo, report_tables):
    mo.ui.anywidget(report_tables["scorecard"])
    return


@app.cell(hide_code=True)
def monthly_introduction(mo):
    mo.md("""
    ## 2 · Trading rhythm

    Bars show selected-period net sales; dark dots show the same dates one year
    earlier. A partial final month is compared with that same partial month.
    The channel stack shows revenue mix, not order mix. Margins use total
    contribution divided by total sales, never an average of line percentages.
    """)
    return


@app.cell
def monthly_view(mo, report_tables):
    mo.ui.anywidget(report_tables["monthly"])
    return


@app.cell(hide_code=True)
def market_introduction(mo):
    mo.md("""
    ## 3 · Where the business sells

    Country net sales on an equal-area world map; gray countries have no recorded
    sales in the selection. Colors scale to the current selection. Hover for
    values. The map uses **wigglystuff
    ObservablePlot**; the detailed territorial comparisons remain in Evidential.
    Geography: [Natural Earth](https://www.naturalearthdata.com/). Country borders
    are approximate and do not locate individual customers. The Plot/d3 libraries
    load from a CDN on first use; the tables work independently of the map.

    Fold a region to see its additive totals in the closed heading. Distinct
    customer counts and margins are deliberately not summed in regional footers.
    """)
    return


@app.cell
def market_map(country_map, mo):
    mo.ui.anywidget(country_map)
    return


@app.cell
def markets_view(mo, report_tables):
    mo.ui.anywidget(report_tables["markets"])
    return


@app.cell(hide_code=True)
def product_introduction(mo):
    mo.md("""
    ## 4 · Product portfolio and pricing

    Category sections contain subcategory detail. Sales shares use the complete
    selection, not just the visible page. Sparklines run oldest to newest across
    the selected months; their vertical scales fit each subcategory, so compare
    their shape rather than their height. Zero means no sales in an observed
    month. Discounts are the reduction from pre-discount line value, not a
    reduction from the current product list price.
    """)
    return


@app.cell
def products_view(mo, report_tables):
    mo.ui.anywidget(report_tables["products"])
    return


@app.cell(hide_code=True)
def customer_introduction(mo):
    mo.md("""
    ## 5 · Customers and account concentration

    **First observed** means a customer's earliest shipped order anywhere in this
    source falls within the selected dates. It is not a claim about lifetime
    acquisition, and changing channel does not reset that first-seen date.
    Reseller accounts are customers linked to a store; consumer names are not
    needed here. The top-15 account shares use **all company net sales in the
    selected channel**, not just the displayed accounts. Prior-only accounts
    remain eligible with zero current sales.
    """)
    return


@app.cell
def customer_view(mo, report_tables):
    mo.ui.anywidget(report_tables["customers"])
    return


@app.cell
def accounts_view(mo, report_tables):
    mo.ui.anywidget(report_tables["accounts"])
    return


@app.cell(hide_code=True)
def operations_introduction(mo):
    mo.md("""
    ## 6 · Fulfilment economics

    Dispatch days run from order date to recorded ship date. **Dispatched by due**
    compares ship date with the order's due date; it is not delivery performance.
    Freight is the recorded order freight charge divided by net sales. These
    observations describe the sample's shipped orders, not a backlog or a live
    service-level commitment. Current inventory is omitted because its snapshot
    cannot be reconstructed at the selected historical year-end.
    """)
    return


@app.cell
def fulfilment_view(mo, report_tables):
    mo.ui.anywidget(report_tables["fulfilment"])
    return


@app.cell(hide_code=True)
def methodology(first_date, last_date, mo, report_data):
    quality = report_data["quality"]
    fallback = quality["fallback_sales"] / quality["net_sales"] if quality["net_sales"] else 0
    mo.md(f"""
    ## 7 · Basis of preparation

    - **Source:** Microsoft's fictional AdventureWorks OLTP sample, read directly
      from the local Parquet product. Order coverage: **{first_date:%d %b %Y} to
      {last_date:%d %b %Y}**. Use `ADVENTUREWORKS_DATASET` to override the location.
    - **Net sales:** discounted `SalesOrderDetail.LineTotal`, for order status 5
      (shipped), excluding tax and freight. Order metrics use one row per order;
      product metrics use one row per line. The two grains are never joined in a
      way that repeats an order's full value for every line.
    - **Cost basis:** quantity × the standard cost whose validity covers the order
      date. Where history is absent, current product standard cost is a disclosed
      fallback (**{fallback:.2%}** of selected sales). Sales with no known cost:
      **${quality["missing_cost_sales"]:,.2f}**. An unknown cost makes its group's
      contribution/margin unavailable rather than treating that cost as zero.
    - **Reconciliation:** selected line sales minus header subtotals is
      **${quality["header_rounding_difference"]:,.4f}**. Tiny differences reflect
      source rounding; all report sales totals use the same line-sales basis.
    - **Comparability:** prior-year windows use matching calendar dates. A missing
      portion of source history suppresses the comparison; a fully covered
      prior window with no matching sales is zero. Growth from a zero base is
      unavailable. Percentages and per-customer measures use aggregated numerators
      and denominators; summary rows show additive measures only.
    - **Scope:** a sample-company operating report, not audited financial
      statements. No overhead, cash-flow, balance-sheet or actual delivered-date
      data is inferred. Local source files are never changed or copied here.
    """)
    return


if __name__ == "__main__":
    app.run()
