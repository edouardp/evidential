# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Searchable, scrollable category slicers, including high-cardinality dimensions."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
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
        settings,
    )


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Dimension slicers

    Click category bars to filter a linked result. The other dimensions narrow
    automatically; a dimension retains its own alternatives. Click a selected
    category again to remove it, or **Clear selections** to start over.

    Each **⌕** replaces the heading with a string search. Moving focus away
    restores the heading; **⌕●** indicates an active search. Open it again to
    edit, or use **×** to clear. Search filters category choices, not the linked
    data: select a result to apply it. Selected values stay pinned and removable.

    Use the mouse wheel to scroll a category list. Horizontal scrolling and the
    arrow buttons reveal more dimensions without making their columns narrower.
    Keyboard: Tab to a list, then arrows or Home/End; Enter/Space selects.
    """)
    return


@app.cell
def source(Path, duckdb):
    connection = duckdb.connect()
    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    connection.read_parquet(str(sample)).create_view("orders")
    return (connection,)


@app.cell(hide_code=True)
def orders_grid_doc(mo):
    mo.md("""
    ## Dimension slicers

    Search and mouse-scroll ranked category lists; click to filter linked
    results. Other dimensions narrow automatically. The **⌕** switches the
    heading to a search input, while horizontal scrolling and arrow controls
    keep large sets of dimensions usable. Selected values stay visible.

    This example uses Evidence's committed `needful_things.orders` sample and
    links to monthly sales below. The same notebook also demonstrates 230
    illustrative cloud services, 23,000 usage types, and twenty dimensions.
    """)
    return


@app.cell
def orders_grid(DimensionGrid, connection, mo):
    orders_slicer = mo.ui.anywidget(
        DimensionGrid(
            connection.sql("SELECT state, category, item, channel, sales FROM orders"),
            dimensions=["state", "category", "item", "channel"],
            metric="sales",
            multiple=True,
            format="compact4",
            height=320,
            title="Explore orders",
            subtitle="Select a state, category, item or channel to narrow monthly sales.",
        )
    )
    orders_slicer
    return (orders_slicer,)


@app.cell
def monthly_table(EvidentialTable, col, label, mo, settings):
    monthly_sales = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.date("month", format="mmm-yy"),
                col.bar("sales", label=label.fmt("usd0").auto_position("outside end")),
                col.integer("orders"),
            ],
            settings=settings(border=False, row_lines=False, page_size=8),
            title="Monthly sales for the selected categories",
        )
    )
    monthly_sales
    return (monthly_sales,)


@app.cell
def update_monthly(connection, monthly_sales, orders_slicer):
    # Read the wrapper's synced value in a reactive cell; do not recreate widgets.
    selection = orders_slicer.value["selected"]
    predicate, parameters = orders_slicer.widget.where()
    result = connection.execute(
        f"""SELECT date_trunc('month', order_datetime) AS month,
                   sum(sales) AS sales, count(*) AS orders
            FROM orders WHERE {predicate} GROUP BY ALL ORDER BY month""",
        parameters,
    ).to_arrow_table()
    monthly_sales.widget.set_data(result)
    return


@app.cell(hide_code=True)
def cloud_doc(mo):
    mo.md("""
    ## High cardinality: 230 services, 23,000 usage types, 20 dimensions

    **Illustrative cloud costs**, generated locally. Scroll within **Service**,
    or search for **RDS**. Select it and **Usage type** narrows to its 100 usage
    types. Search `Backup` there to find it anywhere in the ranking. Selection
    is OR within a dimension, AND between dimensions. Incompatible selections
    stay pinned with an unavailable value so you can remove them.

    The arrow buttons navigate all twenty dimensions; trackpads and the native
    horizontal scrollbar work too. Only visible category buttons are rendered.
    Aggregation runs in Python, and source records stay out of the browser.
    For very large sources, pass a SQL-preaggregated relation at the required
    dimension grain with `metric="cost"` and the default `aggregate="sum"`.
    """)
    return


@app.cell
def cloud_data():
    services = ["RDS", "EC2", "Lambda", "S3", *[f"Service {index:03}" for index in range(4, 230)]]
    tag_names = [
        "project", "environment", "cost_center", "team", "owner", "application",
        "product", "department", "business_unit", "billing_entity", "platform",
        "support_tier", "lifecycle", "compliance", "purchase_option", "resource_group",
    ]
    cloud_records = [
        {
            "service": service,
            "usage_type": f"{service}: {'Backup' if usage == 99 else 'Usage'} {usage:03}",
            "region": ["us-east-1", "eu-west-1", "ap-southeast-2"][usage % 3],
            "account": f"Account {index % 12 + 1:02}",
            **{tag: f"{tag.replace('_', ' ').title()} {(index + usage + offset) % 8 + 1}" for offset, tag in enumerate(tag_names)},
            "cost": round((230 - index) * (100 - usage) * 0.017, 2),
        }
        for index, service in enumerate(services)
        for usage in range(100)
    ]
    return (cloud_records,)


@app.cell
def cloud_grid(DimensionGrid, cloud_records, mo):
    cloud_slicer = mo.ui.anywidget(
        DimensionGrid(
            cloud_records,
            metric="cost",
            format="usd0",
            multiple=True,
            height=340,
            dimension_width=240,
            title="Cloud cost explorer",
            subtitle="Illustrative data · 230 services · 23,000 usage types · 20 dimensions",
            color="#2c83b8",
        )
    )
    cloud_slicer
    return (cloud_slicer,)


@app.cell
def cloud_selection(cloud_slicer, mo):
    cloud_selected = cloud_slicer.value["selected"]
    matching_costs = cloud_slicer.widget.filtered
    mo.md(
        f"**{len(matching_costs):,} matching records · "
        f"${sum(row['cost'] for row in matching_costs):,.2f}**\n\n"
        f"Selections: `{cloud_selected}`"
    )
    return


if __name__ == "__main__":
    app.run()
