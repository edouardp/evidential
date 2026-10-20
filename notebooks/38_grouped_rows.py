# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Synthetic section and summary rows (ADR-059).

How grouped tables present their structure: a combined section+summary row, a
centered section divider, continued section labels across pages, and the row
rule variants (black / grey / white / none).
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, grouped_records, section_row, spacer_row

    return EvidentialTable, col, grouped_records, mo, section_row, spacer_row


@app.cell
def _():
    sales = [
        {"region": "Americas", "country": "United States", "arr": 135.4, "accounts": 42},
        {"region": "Americas", "country": "Canada", "arr": 210.0, "accounts": 31},
        {"region": "Americas", "country": "Mexico", "arr": 88.2, "accounts": 19},
        {"region": "LATAM", "country": "Brazil", "arr": 100.4, "accounts": 24},
        {"region": "LATAM", "country": "Chile", "arr": 54.1, "accounts": 12},
        {"region": "EMEA", "country": "France", "arr": 88.7, "accounts": 27},
        {"region": "EMEA", "country": "Germany", "arr": 142.1, "accounts": 35},
        {"region": "EMEA", "country": "Poland", "arr": 61.3, "accounts": 16},
        {"region": "APAC", "country": "Japan", "arr": 176.5, "accounts": 48},
        {"region": "APAC", "country": "Australia", "arr": 92.8, "accounts": 22},
    ]
    return (sales,)


@app.cell
def _(mo):
    mo.md("""
    # Synthetic rows

    Grouped tables are built from **synthetic rows** that do not correspond to an
    input record: a *section* row introduces a group, a *summary* row reports its
    aggregate, and the two can be **combined** into one row — `North America |
    345.4M` — which saves a row and makes a small table read as a hierarchy.

    Row rules are a design token: `row_lines=True` (default grey), `False`, or a
    colour name (`"black"`, `"grey"`, `"white"`).
    """)
    return


@app.cell
def _(col, grouped_records, mo, sales):
    # combined=True keeps each group's label and its subtotal in one row.
    combined = mo.ui.anywidget(
        grouped_records(
            sales,
            group_by=["region", "country"],
            measures=["arr", "accounts"],
            combined=True,
            total=False,
            subtotal_position="top",
            title="Combined section + summary",
            subtitle="Each region's label carries its subtotal",
            row_lines="black",
            measure_config={
                "arr": col.currency("arr", decimals=1),
                "accounts": col.integer("accounts"),
            },
        )
    )
    combined
    return


@app.cell
def _(mo):
    mo.md("""
    ## Section labels: left or centered

    `section_row(label, align="center")` inserts a full-width divider. A centered
    section carries its meaning in the label alone, so it is used **without**
    summary cells; a left-aligned one can sit above a subtotal row.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, sales, section_row):
    # Interleave full-width section rows with the detail rows. `page_size=4`
    # forces a page break inside a section to demonstrate the repeated label.
    def with_sections():
        rows = []
        for area in ("Americas", "EMEA", "APAC"):
            members = [row for row in sales if row["region"] == area]
            subtotal = sum(row["arr"] for row in members)
            rows.append(section_row(f"{area} — {subtotal:,.1f}", align="left"))
            rows.extend(members)
        return rows

    continued = mo.ui.anywidget(
        EvidentialTable(
            rows=with_sections(),
            page_size=4,
            title="Section rows and continuations",
            subtitle="Page forward: a section that spans pages repeats as “(cont.)”",
            row_lines=False,
            columns=[
                col.text("region", title="Region"),
                col.text("country", title="Country"),
                col.currency("arr", decimals=1),
                col.integer("accounts"),
            ],
        )
    )
    continued
    return


@app.cell
def _(EvidentialTable, col, mo, sales, section_row):
    def with_centered_sections():
        rows = []
        for area in ("Americas", "EMEA", "APAC"):
            rows.append(section_row(area.upper(), align="center"))
            rows.extend(row for row in sales if row["region"] == area)
        return rows

    centered = mo.ui.anywidget(
        EvidentialTable(
            rows=with_centered_sections(),
            title="Centered section labels",
            subtitle="The label spans the table; there are no summary cells",
            row_lines="grey",
            border=False,
            columns=[
                col.text("region"),
                col.text("country"),
                col.currency("arr", decimals=1, title="ARR"),
            ],
        )
    )
    centered
    return


@app.cell
def _(mo):
    mo.md("""
    ## Spacer rows

    `spacer_row(height=)` inserts a blank gap with no rule, to separate blocks
    without carrying a label. When `row_shading` is on, section rows take part
    in the alternating pattern like any other row.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, sales, spacer_row):
    blocks = []
    for area in ("Americas", "EMEA"):
        blocks.extend(row for row in sales if row["region"] == area)
        blocks.append(spacer_row(10))
    spaced = mo.ui.anywidget(
        EvidentialTable(
            rows=blocks,
            title="Spaced blocks",
            subtitle="spacer_row separates blocks without a label",
            row_shading=False,
            border=False,
            columns=[
                col.text("region"),
                col.text("country"),
                col.currency("arr", decimals=1),
            ],
        )
    )
    spaced
    return


@app.cell
def _(mo):
    mo.md("""
    ## Multiple stub columns

    The *stub* is the row-label area. `stub=["region", "country"]` marks both
    columns as the stub, so a hierarchical row label keeps its left alignment and
    stub styling.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, sales):
    stubs = mo.ui.anywidget(
        EvidentialTable(
            sales,
            title="Where the revenue comes from",
            subtitle="Region and country are both stub columns",
            stub=["region", "country"],
            stretch=False,
            columns=[
                col.text("region", title="Region"),
                col.text("country", title="Country"),
                col.currency("arr", decimals=1),
                col.integer("accounts"),
            ],
        )
    )
    stubs
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `combined=True` marks subtotal rows with `__combined`; the row keeps its
      `row_subtotal` kind and its collapsible behaviour, and is styled with the
      section rule.
    - `section_row(..., align="center")` only changes the label's placement; the
      section row remains a single full-width cell.
    - A page that begins in the middle of a section is preceded by a repeated
      `"<label> (cont.)"` row, so the reader always knows where they are.
    - `row_lines` accepts a colour name, which sets the `--et-row-border` token.
    """)
    return


if __name__ == "__main__":
    app.run()
