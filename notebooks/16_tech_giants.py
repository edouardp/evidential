# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Reproduce the classic Evidence / gt "Tech giants" comparison table.

Demonstrates section rows, blank cells (`null_text`), conditional cell colours
and data-driven footnotes with row references. An interactive example explores
single symbols, interleaved doubles and numeric fallback.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, section_row

    return EvidentialTable, col, mo, section_row


@app.cell
def _(mo):
    mo.md("""
    # Tech-giant comparison table

    A plain header, a full-width section divider, per-cell conditional colours,
    blank cells where a company isn't in a market, and **data-driven footnotes**
    (the note text lives in a column and is attached to the company cells; the
    footer lists each note with the rows it appears on).
    """)
    return


@app.cell
def _(col, section_row):
    companies = ["Apple", "Google", "Microsoft", "Intel", "HP", "IBM", "Oracle", "Cisco"]

    metrics = [
        ("Revenues, 2009, $bn", [46.7, 23.7, 58.7, 35.1, 117.0, 95.8, 23.2, 35.5], "num1"),
        ("Net income, 2009, $bn", [9.4, 6.5, 16.3, 4.4, 8.0, 13.4, 5.8, 6.1], "num1"),
        ("Employees, latest", [34300, 19835, 93000, 79800, 304000, 399409, 86000, 68574], "num0"),
    ]

    activity = [
        ("Processors", [3, None, None, 1, None, None, None, 1]),
        ("Computers", [1, 3, None, None, 1, 1, None, 1]),
        ("Network equipment", [None, None, None, 1, 2, 3, 1, None]),
        ("Mobile devices", [1, 3, 3, None, 1, None, None, 3]),
        ("Software**", [1, 1, 1, 1, 1, 1, 1, None]),
        ("Applications", [1, None, 1, None, None, None, 3, 1]),
        ("Web-based services", [2, 1, 1, None, 3, None, 2, 1]),
        ("Online advertising", [3, 1, 1, None, None, None, None, None]),
        ("Cloud computing", [1, 1, None, None, 2, None, None, None]),
        ("IT services/consulting", [3, 2, 2, 1, 1, 2, 2, 1]),
    ]

    shade = {1: "#d1fae5", 2: "#6ee7b7", 3: "#10b981"}

    # Data-driven footnotes: per (row, company) note text.
    notes = {
        ("Processors", "Intel"): "Custom processors",
        ("Computers", "Google"): "Discontinued",
        ("Mobile devices", "Google"): "Smart-phone / tablet",
        ("Mobile devices", "Microsoft"): "Smart-phone / tablet",
        ("Software**", "Apple"): "Operating systems, databases, middleware etc.",
        ("IT services/consulting", "Intel"): "Discontinued",
    }

    rows = []
    for label, values, code in metrics:
        row = {"metric": label, "metric_fmt": code}
        for company, value in zip(companies, values):
            row[company] = value
            row[f"{company}_color"] = None
            row[f"{company}_note"] = None
        rows.append(row)

    rows.append(section_row("Amount of activity in each market"))

    for label, values in activity:
        row = {"metric": label, "metric_fmt": "id"}
        for company, value in zip(companies, values):
            row[company] = value
            row[f"{company}_color"] = None if value is None else shade[value]
            row[f"{company}_note"] = notes.get((label, company))
        rows.append(row)

    columns = [
        col.text("metric", title="Company"),
        col.auto("metric_fmt").hide(),
    ]
    for company in companies:
        columns.append(
            col.number(
                company,
                title=company,
                fmt_column="metric_fmt",
                # blank activity cells render as truly empty (not "–")
                null_text="",
            )
            # conditional cell colour from the hidden colour column
            .color(conditional_colors=f"{company}_color")
            # data-driven footnote from the hidden note column
            .footnote(f"{company}_note")
        )
        columns.append(col.auto(f"{company}_color").hide())
        columns.append(col.auto(f"{company}_note").hide())
    return columns, rows


@app.cell
def _(EvidentialTable, columns, mo, rows):
    mo.ui.anywidget(
        EvidentialTable(
            rows,
            title="Tech giants invade each other's turf",
            caption="Sources: Company reports; The Economist; Bloomberg.",
            row_lines=True,
            row_shading=False,
            header_color="transparent",
            columns=columns,
        )
    )
    return


@app.cell
def footnote_explanation(mo):
    mo.md("""
    ## Footnote symbols

    Footnotes are **plain superscripts**, in the surrounding text colour, with
    no link styling. Hovering a mark still shows the note text. Repeated note
    text shares one mark and one footer entry.

    The default singles are:

    **`*`, `†`, `‡`, `§`, `¶`, `#`, `+`, `◆`, `◇`, `△`**

    Move the slider to inspect the boundaries:

    - **10 notes**: every single symbol is used once.
    - **11 notes**: `*`, `**`, `†`, `‡`, … .
    - **12 notes**: `*`, `**`, `†`, `††`, `‡`, … .
    - **20 notes**: every single is followed by its double.
    - **21–23 notes**: the remaining marks are `1`, `2`, `3`.

    Explicit `footnote_marks="numbers"` or `"letters"` remains available.
    The sample values and notes below are illustrative, with no external data
    required. The widget persists when the slider changes; only its rows update.
    """)
    return


@app.cell
def footnote_controls(mo):
    footnote_count = mo.ui.slider(start=1, stop=23, step=1, value=12, label="Unique footnotes", show_value=True)
    footnote_count
    return (footnote_count,)


@app.cell
def footnote_example_data():
    footnote_descriptions = [
        "Estimated from the previous reporting period.",
        "Seasonally adjusted.",
        "Provisional result.",
        "Revised after publication.",
        "Different reporting period.",
        "Series starts after a methodology change.",
        "Rounded to one decimal place.",
        "Includes overseas territories.",
        "Excludes small establishments.",
        "Survey estimate.",
        "Forecast rather than an observed value.",
        "Adjusted for exchange rates.",
        "Measured at constant prices.",
        "Includes imputed observations.",
        "Excludes one-off transactions.",
        "Reported on a fiscal-year basis.",
        "Data coverage is incomplete.",
        "Comparable series begins this year.",
        "Definition differs from the earlier period.",
        "Population-weighted estimate.",
        "Model-based estimate.",
        "Source changed in the latest period.",
        "Classification changed this year.",
    ]
    footnote_records = [
        {"observation": f"Observation {index + 1}", "value": 10 + index / 10, "note": description}
        for index, description in enumerate(footnote_descriptions)
    ]
    return (footnote_records,)


@app.cell
def footnote_example_table(EvidentialTable, col, footnote_records, mo):
    footnote_table = mo.ui.anywidget(
        EvidentialTable(
            footnote_records[:12],
            title="Single symbols, interleaved doubles, then numbers",
            page_size="all",
            row_shading=True,
            row_lines=False,
            stretch=False,
            columns=[
                col.number("value", fmt="num1").footnote("note"),
                col.auto("note").hide(),
            ],
            footnotes=["Illustrative data; this unmarked source note does not consume a symbol."],
        )
    )
    footnote_table
    return (footnote_table,)


@app.cell
def update_footnote_example(footnote_count, footnote_records, footnote_table):
    # Keep widget creation independent of controls so the renderer persists.
    _ = footnote_table.widget.set_data(footnote_records[:footnote_count.value])
    return


if __name__ == "__main__":
    app.run()
