# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Synthetic rows — the `rows` builder (ADR-060).

A section row introduces a group, a summary row carries a custom label and
per-column values, and a total closes the table. Values may be literals, built-in
aggregation names, or callables over the group's own rows.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, rows

    return EvidentialTable, col, mo, rows


@app.cell
def _():
    detail = [
        {"region": "North America", "country": "United States", "arr": 135.4, "accounts": 42},
        {"region": "North America", "country": "Canada", "arr": 210.0, "accounts": 31},
        {"region": "North America", "country": "Mexico", "arr": 88.2, "accounts": 19},
        {"region": "LATAM", "country": "Brazil", "arr": 100.4, "accounts": 24},
        {"region": "LATAM", "country": "Chile", "arr": 54.1, "accounts": 12},
        {"region": "EMEA", "country": "France", "arr": 88.7, "accounts": 27},
        {"region": "EMEA", "country": "Germany", "arr": 142.1, "accounts": 35},
        {"region": "APAC", "country": "Japan", "arr": 176.5, "accounts": 48},
        {"region": "APAC", "country": "Australia", "arr": 92.8, "accounts": 22},
    ]
    return (detail,)


@app.cell
def _(mo):
    mo.md("""
    # Synthetic rows

    The grouped helpers (`grouped_table`, `grouped_records`) generate every
    subtotal and total for a hierarchy. When a report needs something else — a
    section divider, a differently-named summary, or an average computed from a
    group's own rows — use the `rows` builder:

    ```python
    rows.of(detail)
        .group_by("region")
        .section()                       # a divider before each group
        .summary(label="Developing average",
                 values={"arr": lambda group: sum(r["arr"] for r in group) / len(group)})
        .total(label="All regions")      # sums the numeric columns by default
    ```

    `values` may be a callable, a built-in aggregation name (`"sum"`, `"mean"`,
    `"median"`, `"min"`, `"max"`, `"count"`, …) or a literal. A summary or total
    with no `values` sums each numeric column.
    """)
    return


@app.cell
def _(EvidentialTable, col, detail, mo, rows):
    built = (
        rows.of(detail)
        .group_by("region")
        .section()
        .summary(
            label="Developing average",
            values={"arr": lambda group: sum(r["arr"] for r in group) / len(group)},
        )
        .total(label="All regions")
        .build()
    )
    table = mo.ui.anywidget(
        EvidentialTable(
            rows=built,
            title="Annual recurring revenue",
            subtitle="A section per region, a custom average, and a grand total",
            row_lines=False,
            border=False,
            columns=[
                col.text("region", title="Region"),
                col.text("country", title="Country"),
                col.currency("arr", decimals=1),
                col.integer("accounts"),
            ],
        )
    )
    table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Built-in aggregations and a callable label

    `values={"arr": "sum", "accounts": "count"}` reuses the shared aggregation
    names. The section label can be a callable over the group's rows, so it can
    carry a count: `f"{region} ({len(group)})"`.
    """)
    return


@app.cell
def _(EvidentialTable, col, detail, mo, rows):
    summarised = (
        rows.of(detail)
        .group_by("region")
        .section(lambda group: f"{group[0]['region']} — {len(group)} countries")
        .summary(label="Subtotal", values={"arr": "sum", "accounts": "sum"})
        .total()
        .build()
    )
    second = mo.ui.anywidget(
        EvidentialTable(
            rows=summarised,
            title="Aggregations by name",
            row_lines="grey",
            border=False,
            columns=[
                col.text("region", title="Region"),
                col.text("country", title="Country"),
                col.currency("arr", decimals=1),
                col.integer("accounts"),
            ],
        )
    )
    second
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - Synthetic rows are separate records: they carry a `render_type`
      (`row_section` / `row_subtotal` / `row_total`) and never modify the detail
      rows.
    - `.group_by(...)` sorts the detail rows and groups by the **first**
      dimension; for nested subtotals at every level use `grouped_records`.
    - `.summary(position="top")` puts the summary above its group; the default is
      `"bottom"`.
    - `.total(values={...})` overrides the default numeric-column sums.
    """)
    return


if __name__ == "__main__":
    app.run()
