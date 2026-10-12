# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Column-level formatting, content types and conditional visualisations."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb

    from evidential import EvidentialTable

    return EvidentialTable, duckdb, mo


@app.cell
def _(duckdb):
    connection = duckdb.connect()
    connection.execute(
        """
        CREATE TABLE demo AS
        SELECT * FROM (VALUES
            ('Alpha', 120, 0.12, [10, 20, 15, 30, 25], 'usd0', 'https://example.com/a', '<b>Bold</b>', 72),
            ('Beta',  -40, -0.05, [30, 25, 20, 15, 10], 'usd2', 'https://example.com/b', '<i>Italic</i>', 18),
            ('Gamma', 250, 0.31, [5, 10, 25, 20, 40], 'num0', 'https://example.com/c', '<code>code</code>', 95),
            ('Delta',  80, 0.00, [12, 12, 12, 12, 12], 'pct1', 'https://example.com/d', 'plain text', 50)
        ) AS t(name, amount, change, trend, row_fmt, url, markup, score)
        """
    )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Column-level options

    Formatting (`fmt`, `fmtColumn`), alignment, wrapping, `redNegatives`, the
    column info icon, per-cell links, HTML content, and the Evidence
    `contentType` shorthands.

    ## Formatting, links and HTML
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    formatting = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("SELECT name, amount, row_fmt, url, markup FROM demo"),
            title="Formatting and content",
            page_size=10,
            row_shading=True,
            column_config={
                # name links to the url column
                "name": {"align": "left", "link": "url", "link_new_tab": True,
                         "info": "Click to open the search result"},
                # per-row format pulled from the row_fmt column (fmtColumn)
                "amount": {"title": "Amount", "fmt_column": "row_fmt", "red_negatives": True,
                           "align": "right"},
                "row_fmt": {"title": "Format code", "align": "left"},
                "url": {"hide": True},
                # raw HTML cell (contentType=html)
                "markup": {"title": "HTML", "content_type": "html", "align": "left"},
            },
        )
    )
    formatting
    return


@app.cell
def _(mo):
    mo.md("""
    ## Conditional visualisations

    `bar`, `colorscale`, `delta` and `sparkline` with their options.
    `color_scale` accepts a list of colours or a named preset (`green`, `blue`,
    `red`, `orange`, `purple`, `grey`).
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    visuals = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("SELECT name, amount, change, score, trend FROM demo"),
            title="Column visualisations",
            page_size=10,
            row_shading=True,
            column_config={
                "name": {"align": "left"},
                "amount": {
                    "title": "Amount (bar)",
                    "fmt": "num0",
                    "viz": "bar",
                    "bar_options": {
                        "bar_color": "#2563eb",
                        "bar_color_negative": "#dc2626",
                        "background_color": "#f1f5f9",
                    },
                },
                "change": {
                    "title": "Change (delta chip)",
                    "fmt": "pct1",
                    "viz": "delta",
                    "delta_options": {"chip": True, "show_value": True, "down_is_good": False},
                },
                "score": {
                    "title": "Score (colour scale)",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": ["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
                    "color_options": {"min": 0, "max": 100, "midpoint": 50},
                },
                "trend": {
                    "title": "Trend (sparkline)",
                    "viz": "sparkline",
                    "sparkline_options": {"type": "area", "color": "#53768a"},
                },
            },
        )
    )
    visuals
    return


@app.cell
def _(mo):
    mo.md("""
    ## `contentType` shorthand

    The Evidence `contentType` strings map to the same options above:

    | `content_type` | effect |
    | --- | --- |
    | `link` | cell value is a URL; renders a link |
    | `image` | cell value is an image URL |
    | `html` | render raw HTML |
    | `bar` | `viz="bar"` |
    | `colorscale` | `viz="color"` |
    | `delta` | `viz="delta"` |
    | `sparkline` / `sparkarea` / `sparkbar` | `viz="sparkline"` with line/area/bar |
    """)
    return


if __name__ == "__main__":
    app.run()
