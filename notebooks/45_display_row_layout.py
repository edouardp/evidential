# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Display-only headings, summaries and continuation headings over detail data."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, rows

    return EvidentialTable, col, mo, rows


@app.cell
def _(mo):
    mo.md("""
    # A row layout over detail data

    Headings and summaries belong to the display. They never become source
    records, run through detail mark functions, or affect statistics and scales.
    Search for a product to see the counts and totals recalculate. Use the pager
    to see a repeated **(cont.)** heading; page size counts detail records.
    CSV downloads contain matching details, without headings or summaries.
    """)
    return


@app.cell
def _(col):
    products = [
        {"region": "Europe", "category": "Lighting", "product": "Desk lamp", "sales": 120.5},
        {"region": "Europe", "category": "Lighting", "product": "Floor lamp", "sales": 240.0},
        {"region": "Europe", "category": "Lighting", "product": "Wall lamp", "sales": 175.25},
        {"region": "Europe", "category": "Seating", "product": "Desk chair", "sales": 315.0},
        {"region": "Europe", "category": "Seating", "product": "Lounge chair", "sales": 460.0},
        {"region": "Americas", "category": "Lighting", "product": "Desk lamp", "sales": 155.5},
        {"region": "Americas", "category": "Lighting", "product": "Floor lamp", "sales": 225.0},
        {"region": "Americas", "category": "Seating", "product": "Desk chair", "sales": 390.0},
    ]
    product_columns = [
        col.text("product"),
        col.text("category"),
        col.bar("sales", fmt="usd2").point(lambda row: row["sales"]),
    ]
    report_options = dict(border=False, row_lines=False, row_shading=True, stub="product", width=850)
    return product_columns, products, report_options


@app.cell
def _(EvidentialTable, mo, product_columns, products, report_options, rows):
    grouped_layout = (
        rows.group_by("region")
        .section(values={"category": rows.count(suffix=" products"), "sales": "sum"}, rule="below")
        .summary("Region total", values={"sales": "sum"})
        .grand_summary("Grand total", values={"sales": "sum"})
    )
    grouped_display = mo.ui.anywidget(
        EvidentialTable(
            products,
            row_layout=grouped_layout,
            columns=product_columns,
            **report_options,
            title="Heading values, group summaries, and one grand summary",
            page_size=3,
            row_numbers=True,
            section_indent=1,
            column_stats=True,
            download=True,
        )
    )
    grouped_display
    return


@app.cell
def _(mo):
    mo.md("""
    ## Nested groups

    Group order follows first appearance; sorting reorders details within each
    group. Every ancestor heading repeats when its group continues on a later
    page. A group summary appears after its final matching detail; the grand
    summary appears once on the final page. All summaries read detail data, so
    nested subtotals are never counted twice.
    """)
    return


@app.cell
def _(EvidentialTable, mo, product_columns, products, report_options, rows):
    nested_display = mo.ui.anywidget(
        EvidentialTable(
            products,
            row_layout=rows.group_by("region", "category")
            .section()
            .summary("Subtotal", values={"sales": "sum"})
            .grand_summary(values={"sales": "sum"}),
            columns=product_columns,
            **report_options,
            title="Two group levels, with continuation headings",
            page_size=2,
            section_indent=1,
        )
    )
    nested_display
    return


@app.cell
def _(mo):
    mo.md("""
    ## Independent row presentation

    A centered, full-width heading has no value cells. This variant places an
    average before the details and omits the grand summary. Literal strings
    and Python callbacks also work in `values`; callbacks run on Python data
    refresh and retain their source scope during browser search. Use named
    reducers or `rows.count(suffix=" products")` for summaries that track search.
    """)
    return


@app.cell
def _(EvidentialTable, mo, product_columns, products, report_options, rows):
    centered_display = mo.ui.anywidget(
        EvidentialTable(
            products,
            row_layout=rows.group_by("region")
            .section(align="center", style={"font_weight": "normal", "color": "#666666"}, rule="both")
            .summary("Average", values={"category": "Active products", "sales": "mean"}, position="top"),
            columns=product_columns,
            **report_options,
            title="Centered headings and a summary before each group",
            page_size="all",
        )
    )
    centered_display
    return


if __name__ == "__main__":
    app.run()
