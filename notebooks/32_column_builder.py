# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""The ``col`` builder and the ``settings`` bundle.

Two tables over the same data: a fully configured report (settings + chained
``col.*`` columns) and a bare default table to experiment with.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, Path, col, duckdb, mo, settings


@app.cell
def _(Path, duckdb):
    sample = Path(__file__).parent / "sample_data" / "needful_things" / "orders.parquet"
    connection = duckdb.connect()
    connection.execute(f"CREATE VIEW orders AS SELECT * FROM read_parquet('{sample}')")
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # The `col` builder and `settings`

    Two ways to make a table more discoverable:

    - **`col.*`** builds one column at a time. Every call returns a new, immutable
      column, so it can be reused and chained — and because a column is a mapping
      it also works as a `column_config` value.
    - **`settings(...)`** collects table-level options into a reusable bundle you
      can splat (`**REPORT`) or pass as `settings=REPORT` (per-table options win).

    Both validate their keys, so a typo suggests the right name.
    """)
    return


@app.cell
def _():
    summary_sql = """
        WITH monthly AS (
            SELECT category, item, channel_group, order_month,
                   sum(sales) AS m_sales, count(*) AS m_orders
            FROM orders
            GROUP BY 1, 2, 3, 4
        ),
        totals AS (SELECT sum(sales) AS total FROM orders)
        SELECT
            category,
            item,
            channel_group,
            round(sum(m_sales), 0) AS sales,
            sum(m_orders)            AS orders,
            round(sum(m_sales) / sum(m_orders), 2) AS avg_sale,
            round(sum(m_sales) / (SELECT total FROM totals), 4) AS share,
            round(
                (sum(m_sales) FILTER (WHERE order_month >= DATE '2021-01-01')
                 - sum(m_sales) FILTER (WHERE order_month < DATE '2021-01-01'))
                / nullif(sum(m_sales) FILTER (WHERE order_month < DATE '2021-01-01'), 0), 3
            ) AS growth,
            array_agg(
                {'month': strftime(order_month, '%Y-%m'), 'value': round(m_sales, 0)}
                ORDER BY order_month
            ) AS trend
        FROM monthly
        GROUP BY 1, 2, 3
        HAVING sum(m_sales) > 1000
    """
    return (summary_sql,)


@app.cell
def _(EvidentialTable, col, connection, mo, settings, summary_sql):
    REPORT = settings(
        title="Orders by category, item and channel",
        subtitle="The needful_things sample, 2019-2021",
        caption="Source: sample_data/needful_things/orders.parquet",
        page_size=12,
        search=True,
        row_shading=True,
        border=False,
        column_stats=True,
        align_decimals=True,
        header_color="#1e293b",
        header_font_color="#f8fafc",
        total_row_color="#e2e8f0",
    )

    report = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(summary_sql),
            settings=REPORT,
            columns=[
                col.text("category").group("Product").info("The product category"),
                col.text("item").group("Product"),
                col.chip("channel_group").group("Channel"),
                col.currency("sales").bar(color="#93c5fd", fit_to_data=True).group("Performance"),
                col.integer("orders").group("Performance"),
                col.currency("avg_sale", decimals=2)
                .title("Avg sale")
                .color(scale=["#fee2e2", "#fef9c3", "#bbf7d0"])
                .group("Performance"),
                col.percent("share").group("Performance"),
                col.percent("growth").delta(down_is_good=False, neutral_range="0.02").group("Performance"),
                col.sparkline("trend", type="area", color="#53768a", fit_to_data=True),
            ],
        )
    )
    report
    return


@app.cell
def _(mo):
    mo.md("""
    ## A default table to play with

    The same data with no table settings and plain `col.*` columns. Open a new
    cell and try chaining, e.g. `col.currency("sales").bar(color="#f97316")`,
    add `.group("Performance")`, or swap `.bar(...)` for `.color(...)` /
    `.delta(...)` / `.sparkline(...)`.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo, summary_sql):
    playground = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(summary_sql),
            columns=[
                col.text("category"),
                col.text("item"),
                col.chip("channel_group", min_width=80),
                col.currency("sales", code="jpy"),
                col.integer("orders"),
                col.currency("avg_sale", decimals=2),
                col.percent("share"),
                col.percent("growth").delta(down_is_good=False),
                col.sparkline("trend", type="area")
            ],
        )
    )
    playground
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `col.*` names a column's **kind** — the first decision. Kinds: `text`,
      `number`, `integer`, `percent`, `currency`, `date`, `boolean`, `array`,
      `flag`, `bar`, `color`, `chip`, `sparkline`, `delta`, `link`/`url`,
      `image`, `logo`, `markdown`, `html`. Each sets a sensible baseline with no
      configuration: `col.currency("sales")` auto-scales, `col.percent("share")`
      picks decimals, and `col.percent("rate", whole=True)` treats the value as
      an already-percent number.
    - Chain methods refine any kind: `.fmt()`, `.title()`, `.align()`, `.group()`,
      `.info()`, `.bar()`, `.color()`, `.delta()`, `.sparkline()`, `.chip()`…
      Each returns a new column, so specs are reusable.
    - A `Column` is a mapping, so it works in `columns=[...]` *and* as a
      `column_config={...}` value.
    - `settings(...)` is a validated bundle of table options: splat it with
      `**REPORT` or pass `settings=REPORT` (explicit keywords override it).
    - Both raise with a suggestion on an unknown key (`borderr` → `border`) and
      on a bad currency or percent (`code="xyz"`, `decimals=9`).
    """)
    return


if __name__ == "__main__":
    app.run()
