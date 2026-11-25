# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Hierarchical (grouped) rows: accordion and section styles."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import col, grouped_records

    return Path, col, duckdb, grouped_records, mo


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
    # Hierarchical rows

    DuckDB computes detail-level sums and counts. `grouped_records` groups
    those in-memory records and sums their measures for the subtotals and grand
    total. `group_type` chooses how groups are rendered:

    - `"accordion"` (default) — subtotal rows are clickable to expand/collapse
      their children.
    - `"section"` — the group's dimension cell is merged (rowspan) across its
      rows instead of being collapsible.

    ## Accordion (multi-level)

    Click a subtotal row to collapse its group.
    """)
    return


@app.cell
def _(col, connection, grouped_records, mo):
    accordion = mo.ui.anywidget(
        grouped_records(
            connection.sql("""
                SELECT category, item, sum(sales) AS sales, count(*) AS orders
                FROM needful_things.orders
                GROUP BY category, item
            """),
            group_by=["category", "item"],
            measures=["sales", "orders"],
            total_label="All items",
            subtotal_position="top",
            collapsible=True,
            collapsed=False,
            title="Sales by category and item (accordion)",
            max_height="460px",
            dimension_config={"category": col.text("category"), "item": col.text("item")},
            measure_config={
                "sales": col.bar("sales", format='usd0', color="green", label=True),
                "orders": col.integer("orders"),
            },
        )
    )
    accordion
    return


@app.cell
def _(mo):
    mo.md("""
    ## Section (merged group cells)

    The same data with `group_type="section"` — the category cell spans its
    item rows, and there are no collapse chevrons.
    """)
    return


@app.cell
def _(col, connection, grouped_records, mo):
    section = mo.ui.anywidget(
        grouped_records(
            connection.sql("""
                SELECT category, item, sum(sales) AS sales, count(*) AS orders
                FROM needful_things.orders
                GROUP BY category, item
            """),
            group_by=["category", "item"],
            measures=["sales", "orders"],
            total_label="All items",
            subtotal_position="top",
            group_type="section",
            title="Sales by category and item (section)",
            max_height="460px",
            dimension_config={"category": col.text("category"), "item": col.text("item")},
            measure_config={
                "sales": col.bar("sales", format='usd0', label=True),
                "orders": col.integer("orders"),
            },
        )
    )
    section
    return


@app.cell
def _(mo):
    mo.md("""
    ## Collapsed by default

    `groups_open=False` starts every group collapsed. It is the inverse of
    `collapsed`.
    """)
    return


@app.cell
def _(col, connection, grouped_records, mo):
    collapsed = mo.ui.anywidget(
        grouped_records(
            connection.sql("""
                SELECT channel_group, category, sum(sales) AS sales
                FROM needful_things.orders
                GROUP BY channel_group, category
            """),
            group_by=["channel_group", "category"],
            measures=["sales"],
            total_label="All channels",
            subtotal_position="top",
            collapsible=True,
            groups_open=False,
            title="Sales by channel and category (collapsed)",
            max_height="420px",
            measure_config={"sales": col.currency("sales", decimals=0)},
        )
    )
    collapsed
    return


if __name__ == "__main__":
    app.run()
