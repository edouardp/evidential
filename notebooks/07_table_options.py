# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidence-tables",
# ]
# ///
"""Table-level display options demonstrated on Evidence's sample data."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidence_tables import EvidenceTable

    return EvidenceTable, Path, duckdb, mo


@app.cell
def _(Path, duckdb):
    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    connection = duckdb.connect()
    connection.execute("CREATE SCHEMA IF NOT EXISTS needful_things")
    connection.execute(
        f"CREATE VIEW needful_things.orders AS SELECT * FROM read_parquet('{sample}')"
    )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Table-level display options

    These map to Evidence's DataTable props: `rowNumbers`, `compact`,
    `rowShading`, `rowLines`, `sort`, `freezeColumns`, `rowConditionalColors`,
    `headerColor`, `emptyMessage`, `link`, and the title/info props.
    """)
    return


@app.cell
def _(EvidenceTable, connection, mo):
    summary = mo.ui.anywidget(
        EvidenceTable(
            connection.sql(
                """
                SELECT
                    category,
                    count(*) AS orders,
                    round(sum(sales), 0) AS sales,
                    round(avg(sales), 2) AS avg_sale,
                    CASE WHEN sum(sales) > 100000 THEN '#dcfce7' ELSE NULL END AS tint
                FROM needful_things.orders
                GROUP BY category
                ORDER BY sales DESC
                """
            ),
            title="Categories",
            subtitle="row numbers, compact density, default sort, row shading, tinted rows",
            info="Totals across the whole 2019-2021 sample",
            row_numbers=True,
            compact=True,
            row_shading=True,
            freeze_columns=1,
            default_sort={"column": "sales", "direction": "desc"},
            row_conditional_colors="tint",
            header_color="#1e293b",
            header_font_color="#f8fafc",
            total_row_color="#e2e8f0",
            column_config={
                "category": {"align": "left"},
                "orders": {"title": "Orders", "fmt": "num0"},
                "sales": {"title": "Sales", "fmt": "usd0", "viz": "bar"},
                "avg_sale": {"title": "Avg sale", "fmt": "usd2"},
                "tint": {"hide": True},
            },
        )
    )
    summary
    return


@app.cell
def _(mo):
    mo.md("""
    ## Row links

    `link="url_column"` makes each row clickable; `show_link_column=True` also
    keeps the URL column visible.
    """)
    return


@app.cell
def _(EvidenceTable, connection, mo):
    links = mo.ui.anywidget(
        EvidenceTable(
            connection.sql(
                """
                SELECT
                    item,
                    category,
                    round(sum(sales), 0) AS sales,
                    'https://www.google.com/search?q=' || item AS lookup
                FROM needful_things.orders
                GROUP BY item, category
                ORDER BY sales DESC
                LIMIT 25
                """
            ),
            title="Top items",
            link="lookup",
            show_link_column=True,
            page_size=8,
            row_lines=False,
            column_config={
                "item": {"align": "left"},
                "category": {"align": "left"},
                "sales": {"fmt": "usd0", "viz": "bar"},
                "lookup": {"title": "Search", "content_type": "link", "link_new_tab": True},
            },
        )
    )
    links
    return


@app.cell
def _(mo):
    mo.md("""
    ## Outer border

    `border=False` drops the frame (and rounded corners) around the table — handy
    when it sits inside a card, or when the surrounding layout already frames it.
    The rows keep their own lines (`row_lines`).
    """)
    return


@app.cell
def _(EvidenceTable, connection, mo):
    borderless = mo.ui.anywidget(
        EvidenceTable(
            connection.sql(
                """
                SELECT category, count(*) AS orders, round(sum(sales), 0) AS sales
                FROM needful_things.orders
                GROUP BY category
                ORDER BY sales DESC
                """
            ),
            title="No outer border",
            subtitle="border=False",
            border=False,
            row_shading=True,
            column_config={
                "category": {"align": "left"},
                "orders": {"fmt": "num0"},
                "sales": {"fmt": "usd0", "viz": "bar"},
            },
        )
    )
    borderless
    return


@app.cell
def _(mo):
    mo.md("""
    ## Empty state

    `empty_message` replaces the default “No records”.
    """)
    return


@app.cell
def _(EvidenceTable, connection, mo):
    empty = mo.ui.anywidget(
        EvidenceTable(
            connection.sql("SELECT category, sales FROM needful_things.orders WHERE 1=0"),
            title="No matching orders",
            empty_message="No orders matched this filter",
            row_shading=True,
        )
    )
    empty
    return


if __name__ == "__main__":
    app.run()
