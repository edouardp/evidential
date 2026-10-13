# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
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

    from evidential import EvidentialTable

    return EvidentialTable, dt, mo


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
def _(EvidentialTable, mo, records):
    table = mo.ui.anywidget(
        EvidentialTable(
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
def _(show_stats, subcolumn_stats, table):
    # A separate reactive cell keeps the widget alive: only its options change,
    # so Marimo does not recreate the table when the checkbox flips. Assigning
    # to `_` avoids rendering the widget returned by `update_options`.
    _ = table.widget.update_options(column_stats=show_stats.value)
    _ = table.widget.update_options(column_stats=subcolumn_stats)
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


@app.cell
def mixed_statistics_explanation(mo):
    mo.md("""
    ## Statistics for sub-columns

    This example mixes ordinary columns with two shared headers:

    - **Activity**: a right-aligned trip count and left-aligned unit text.
    - **Fare & payment**: a currency amount, payment text and a centered chip.
    - **City**, **Tip rate** and **Pickup** remain ordinary columns.

    Each shared header gets **one statistics cell**. Its small centered dots
    show which member is active: **●○** or **●○○** initially. Click the dots to
    advance, looping back after the last member. Enter and Space also work.
    Numeric members show min/max/average; text and chip members show distinct
    and null counts. All summaries have the same footer space; ordinary
    columns have a blank, inactive footer. Switching members keeps the
    statistics row at the same height.
    """)
    return


@app.cell
def mixed_statistics_data(records):
    mixed_records = [
        {
            **record,
            "trip_unit": "trips",
            "status": "Review" if record["payment"] == "Dispute" else "Recorded",
            "status_color": "#ffe0c2" if record["payment"] == "Dispute" else "#c7e8d2",
        }
        for record in records
    ]
    return (mixed_records,)


@app.cell
def mixed_statistics_table(EvidentialTable, mixed_records, mo):
    subcolumn_stats = mo.ui.anywidget(
        EvidentialTable(
            mixed_records,
            title="Mixed columns and sub-columns",
            subtitle="Click the small dots below a summary to inspect its next member",
            columns=["city", "trips", "trip_unit", "fare", "payment", "status", "tip_rate", "pickup"],
            column_stats=True,
            row_shading=True,
            page_size=4,
            column_config={
                "trips": {"type": "number", "fmt": "num0", "align": "right", "subcolumn_group": "Activity"},
                "trip_unit": {"title": "Unit", "align": "left", "font_color": "#808080", "subcolumn_group": "Activity"},
                "fare": {"type": "number", "fmt": "usd2", "align": "right", "subcolumn_group": "Fare & payment"},
                "payment": {"align": "left", "subcolumn_group": "Fare & payment"},
                "status": {
                    "align": "center", "viz": "chip", "subcolumn_group": "Fare & payment",
                    "color_options": {"conditional_colors": "status_color"},
                },
                "tip_rate": {"title": "Tip rate", "type": "number", "fmt": "pct1", "align": "right"},
                "pickup": {"type": "date", "fmt": "date"},
            },
        )
    )
    subcolumn_stats
    return (subcolumn_stats,)


if __name__ == "__main__":
    app.run()
