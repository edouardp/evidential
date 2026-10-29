# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "pyarrow>=17", "evidential"]
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
    data: select a result to apply it. Selected values keep their ranked positions,
    with bold text and a full-height dark red marker. They remain in the list
    during searches, so you can remove them without clearing the search.

    Use the mouse wheel or slim scrollbar to scroll a category list. Horizontal scrolling and the
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
    keep large sets of dimensions usable. Selected values keep their ranked
    positions, marked with bold text and a dark red strip; slim scrollbars
    make longer category lists easy to navigate.

    This example uses Evidence's committed `needful_things.orders` sample and
    links to monthly sales below. Notebook 57 applies the same slicer to the local AWS CUR data product,
    with linked cost-driver and line-item tables.
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
def cur_explorer_link(mo):
    mo.md("""
    ## Explore AWS cost and usage

    Open **57_aws_cur_explorer.py** for a real CUR explorer using the processed
    product in `~/datasets/aws-cur-example`. Nine useful dimensions filter
    cost-driver totals, daily sparklines and individual charges. Set
    `AWS_CUR_DATASET` to use another local checkout of the data product.
    """)
    return


if __name__ == "__main__":
    app.run()
