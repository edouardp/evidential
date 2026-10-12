# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidence-tables",
# ]
# ///
"""Multi-line column headers.

A newline in a column title forces a line break, and every header is aligned to
the **bottom** of its cell, so single-line and multi-line headers share a
baseline on the header rule. Titles also wrap when a column is narrow; set
``wrap_titles=False`` to keep each line as long as it needs to be.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidence_tables import EvidenceTable

    return EvidenceTable, mo


@app.cell
def _(mo):
    mo.md("""
    # Multi-line column headers

    A column title can span several lines: put a newline where the break should
    go. Every header is `vertical-align: bottom`, so a one-line header sits on
    the same baseline — the header rule — as a two- or three-line one.
    """)
    return


@app.cell
def _():
    records = [
        {"region": "Americas", "revenue": 12400, "orders": 312, "growth": 0.084},
        {"region": "Europe", "revenue": 9800, "orders": 274, "growth": 0.031},
        {"region": "Asia", "revenue": 7600, "orders": 198, "growth": -0.012},
    ]
    return (records,)


@app.cell
def _(EvidenceTable, mo, records):
    multiline = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="Forced line breaks",
            subtitle="A newline in the title, and every header sits on the rule",
            row_shading=True,
            column_config={
                "region": {"align": "left"},
                "revenue": {"title": "Revenue\n(USD thousands)", "fmt": "usd0"},
                "orders": {"title": "Orders\n(count)", "fmt": "num0"},
                "growth": {"title": "Growth\n(year over year)", "fmt": "pct1"},
            },
        )
    )
    multiline
    return


@app.cell
def _(mo):
    mo.md("""
    ## Wrapping titles

    A title also wraps at spaces when its column is narrow (`wrap_titles` is
    `True` by default). The first table below wraps the long titles; the second
    sets `wrap_titles=False`, so each title stays on one line — and the narrower
    table then scrolls horizontally.
    """)
    return


@app.cell
def _(EvidenceTable, mo, records):
    wrapped = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="Wrapping titles (default)",
            width="420px",
            column_config={
                "region": {"title": "Region or territory", "align": "left"},
                "revenue": {"title": "Total revenue in USD thousands", "fmt": "usd0"},
                "orders": {"title": "Number of orders placed", "fmt": "num0"},
                "growth": {"title": "Year over year growth", "fmt": "pct1"},
            },
        )
    )
    wrapped
    return


@app.cell
def _(EvidenceTable, mo, records):
    nowrap = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="wrap_titles=False",
            width="420px",
            wrap_titles=False,
            column_config={
                "region": {"title": "Region or territory", "align": "left"},
                "revenue": {"title": "Total revenue in USD thousands", "fmt": "usd0"},
                "orders": {"title": "Number of orders placed", "fmt": "num0"},
                "growth": {"title": "Year over year growth", "fmt": "pct1"},
            },
        )
    )
    nowrap
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - A newline in a title always forces a break, even under `wrap_titles=False`.
    - Headers stay `vertical-align: bottom`, so the last line of every header
      lines up with the header rule under them.
    - `all_caps` and `format_titles=False` still apply before the title is split
      into lines.
    """)
    return


if __name__ == "__main__":
    app.run()
