# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Reproduce the classic Evidence / gt "Tech giants" comparison table.

Demonstrates section rows, blank cells (`null_text`), conditional cell colours
and data-driven footnotes with row references.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, section_row

    return EvidentialTable, mo, section_row


@app.cell
def _(mo):
    mo.md("""
    # Tech-giant comparison table

    A plain header, a full-width section divider, per-cell conditional colours,
    blank cells where a company isn't in a market, and **data-driven footnotes**
    (the note text lives in a column and is linked into the company cells; the
    footer lists each note with the rows it appears on).
    """)
    return


@app.cell
def _(section_row):
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

    column_config = {
        "metric": {"title": "Company", "align": "left"},
        "metric_fmt": {"hide": True},
    }
    for company in companies:
        column_config[company] = {
            "title": company,
            "align": "right",
            "fmt_column": "metric_fmt",
            # blank activity cells render as truly empty (not "–")
            "null_text": "",
            # conditional cell colour from the hidden colour column
            "viz": "color",
            "color_options": {"conditional_colors": f"{company}_color"},
            # data-driven footnote from the hidden note column
            "footnote": f"{company}_note",
        }
        column_config[f"{company}_color"] = {"hide": True}
        column_config[f"{company}_note"] = {"hide": True}
    return column_config, rows


@app.cell
def _(EvidentialTable, column_config, mo, rows):
    mo.ui.anywidget(
        EvidentialTable(
            rows,
            title="Tech giants invade each other's turf",
            caption="Sources: Company reports; The Economist; Bloomberg.",
            row_lines=True,
            row_shading=False,
            header_color="transparent",
            column_config=column_config,
        )
    )
    return


if __name__ == "__main__":
    app.run()
