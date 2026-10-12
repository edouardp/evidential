# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""White space as a grouping device (proximity / similarity).

Shows grouped rows, section dividers and padding doing the work that rules and
fills usually (over)do.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import duckdb

    from evidential import EvidentialTable, grouped_table, section_row

    return EvidentialTable, Path, duckdb, grouped_table, mo


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
    # White space for grouping

    Rutter's tables advice: remove rules and fills and let **proximity** (space
    between groups) and **similarity** (consistent look) carry the structure.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A wall of rows (hard to scan)
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT category, item, round(sum(sales), 0) AS sales
                FROM needful_things.orders
                GROUP BY category, item
                ORDER BY category, sales DESC
                """
            ),
            title="Flat list",
            max_height="360px",
            row_lines=True,
            column_config={"sales": {"fmt": "usd0"}},
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Grouped rows, separated by white space

    `group_gap=True` adds room around group boundaries; `row_lines=False` drops
    the rules entirely. The eye groups the rows by proximity.
    """)
    return


@app.cell
def _(connection, grouped_table, mo):
    mo.ui.anywidget(
        grouped_table(
            connection,
            "SELECT category, item, sales FROM needful_things.orders",
            dimensions=["category", "item"],
            measures=["round(sum(sales), 0) AS sales"],
            total_label="All items",
            subtotal_position="top",
            group_gap=True,
            row_lines=False,
            title="Grouped by category",
            max_height="420px",
            measure_config={"sales": {"fmt": "usd0", "viz": "bar"}},
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Stripes in groups of three

    `row_shading=3` shades three rows, skips three, and repeats — a coarser
    grouping cue than strict alternation. Pass `[shaded, unshaded]` for other
    patterns.
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT category, item, round(sum(sales), 0) AS sales
                FROM needful_things.orders
                GROUP BY category, item
                ORDER BY category, sales DESC
                """
            ),
            title="Stripes of three",
            max_height="360px",
            row_shading=3,
            row_lines=False,
            column_config={"sales": {"fmt": "usd0"}},
        )
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Section dividers

    For coarser sections within a single table, `section_row(...)` inserts a
    full-width label with space around it — no rule needed above it.
    """)
    return


@app.cell
def _(EvidentialTable, mo):
    rows = [
        {"metric": "Revenue", "q1": 120000, "q2": 135000},
        {"metric": "Cost of sales", "q1": 54000, "q2": 61000},
        {"metric": "Gross profit", "q1": 66000, "q2": 74000},
        {"render_type": "row_section", "__label": "Operating expenses"},
        {"metric": "Sales & marketing", "q1": 18000, "q2": 21000},
        {"metric": "Research & development", "q1": 12000, "q2": 14000},
        {"metric": "General & admin", "q1": 9000, "q2": 9500},
    ]
    mo.ui.anywidget(
        EvidentialTable(
            rows,
            title="Income statement (illustrative)",
            column_config={
                "metric": {"title": "", "align": "left"},
                "q1": {"title": "Q1", "fmt": "usd0"},
                "q2": {"title": "Q2", "fmt": "usd0"},
            },
        )
    )
    return


if __name__ == "__main__":
    app.run()
