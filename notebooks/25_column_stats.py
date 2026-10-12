# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidence-tables",
# ]
# ///
"""Optional column statistics under the header.

Set ``column_stats=True`` and a summary block appears under each column header,
before the data:

```text
[NUMBER]            [STRING]
min: 12             distinct: 3
max: 141            null: 0
avg: 82
null: 0
```

Numeric columns get min/max/avg plus a null count; every other column gets a
distinct count plus a null count. The values are formatted with the column's
``fmt`` and computed client-side over the full dataset. The checkbox toggles the
section on and off with ``update_options``.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import datetime as dt

    import marimo as mo

    from evidence_tables import EvidenceTable

    return EvidenceTable, dt, mo


@app.cell
def _(mo):
    mo.md("""
    # Column statistics

    Turn on `column_stats=True` and each column gets a summary block directly
    under its header, before the data:

    - **numeric** columns — `min`, `max`, `avg` and a `null` count;
    - **everything else** — a `distinct` count and a `null` count.

    The block starts with the column's datatype in brackets, and the numbers use
    the column's `fmt` (`$2k`, `18.0%`, `12`). Toggle it with the checkbox below.
    """)
    return


@app.cell
def _(dt):
    records = [
        {"city": "New York", "payment": "Credit card", "trips": 128, "fare": 4520.50, "tip_rate": 0.18, "pickup": dt.date(2024, 1, 3)},
        {"city": "New York", "payment": "Cash", "trips": 96, "fare": 3310.00, "tip_rate": 0.05, "pickup": dt.date(2024, 1, 4)},
        {"city": "Chicago", "payment": "Credit card", "trips": 74, "fare": 2890.75, "tip_rate": 0.21, "pickup": dt.date(2024, 1, 5)},
        {"city": "Chicago", "payment": "Dispute", "trips": 12, "fare": None, "tip_rate": None, "pickup": dt.date(2024, 1, 6)},
        {"city": "Los Angeles", "payment": "Credit card", "trips": 141, "fare": 5102.20, "tip_rate": 0.16, "pickup": dt.date(2024, 1, 7)},
        {"city": "Los Angeles", "payment": "Cash", "trips": 88, "fare": 3040.10, "tip_rate": 0.04, "pickup": dt.date(2024, 1, 8)},
        {"city": "Boston", "payment": "Credit card", "trips": 53, "fare": 1980.00, "tip_rate": 0.19, "pickup": dt.date(2024, 1, 9)},
        {"city": "Boston", "payment": "Credit card", "trips": 61, "fare": 2210.40, "tip_rate": 0.22, "pickup": dt.date(2024, 1, 10)},
    ]
    return (records,)


@app.cell
def _(EvidenceTable, mo, records):
    table = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="Trips by city",
            column_stats=True,
            row_shading=True,
            column_config={
                "trips": {"fmt": "num0"},
                "fare": {"fmt": "usd"},
                "tip_rate": {"fmt": "pct1"},
            },
        )
    )
    table
    return (table,)


@app.cell
def _(mo):
    show_stats = mo.ui.checkbox(value=True, label="Column statistics")
    show_stats
    return (show_stats,)


@app.cell
def _(show_stats, table):
    # A separate reactive cell keeps the widget alive: only its options change,
    # so Marimo does not recreate the table when the checkbox flips. Assigning
    # to `_` avoids rendering the widget returned by `update_options`.
    _ = table.widget.update_options(column_stats=show_stats.value)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - The statistics cover the **full dataset**, not just the current page or the
      sorted order (search and pagination do not change them).
    - `null` counts missing values; `distinct` counts unique values (arrays and
      structs are compared by their JSON form).
    - `column_stats` is a table-level option, default `False`.
    """)
    return


if __name__ == "__main__":
    app.run()
