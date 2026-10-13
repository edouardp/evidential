# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Relative date and time columns.

``col.date``, ``col.time`` and ``col.datetime`` are the temporal kinds. Pass
``relative=`` (a unit, or ``True`` for an automatic unit) to render a value
relative to now instead of absolutely.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, duckdb, mo, settings


@app.cell
def _(duckdb):
    connection = duckdb.connect()
    connection.execute(
        """
        CREATE TABLE events AS
        SELECT * FROM (VALUES
            ('Deploy web',       now() - INTERVAL 5 MINUTE),
            ('Nightly build',    now() - INTERVAL 3 HOUR),
            ('Data import',      now() - INTERVAL 2 DAY),
            ('Quarterly report', now() - INTERVAL 45 DAY),
            ('Contract renewal', now() + INTERVAL 20 DAY),
            ('Archive',          now() - INTERVAL 14 MONTH),
            ('Launch',           now() + INTERVAL 8 MONTH)
        ) AS t(event, happened_at)
        """
    )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Relative date and time columns

    `col.date`, `col.time` and `col.datetime` are the temporal kinds. Each takes
    `relative=` — a unit (`"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`,
    `"month"`, `"year"`) or `True` for an automatic unit — and then renders the
    value relative to now instead of as an absolute date.

    It uses `Intl.RelativeTimeFormat`, so the text is localised and pluralised
    ("yesterday", "in 3 days", "2 hours ago"). On the chain it is
    `.relative(...)`.
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo, settings):
    table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("SELECT * FROM events ORDER BY happened_at"),
            settings=settings(title="Release events", row_shading=True, border=False),
            columns=[
                col.text("event"),
                col.datetime("happened_at", relative=True).title("Relative"),
                col.date("happened_at", relative="day").title("Relative (days)"),
                col.datetime("happened_at").title("Absolute"),
                col.time("happened_at").title("Time"),
            ],
        )
    )
    table
    return


if __name__ == "__main__":
    app.run()
