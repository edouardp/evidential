# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Synthetic rows — a separate display layout (ADR-064).

A section row introduces a group, a summary row carries a custom label and
per-column values, and an optional grand summary closes the table. Headings and
summaries never enter the source data or run through detail mark functions.
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
    group's own rows — pass a separate `row_layout`:

    ```python
    rows.group_by("region")
        .section()                       # a divider before each group
        .summary("Regional average", values={"arr": "mean"})
        .grand_summary("All regions")    # sums numeric detail fields by default
    ```

    `values` may be a callable, a built-in aggregation name (`"sum"`, `"mean"`,
    `"median"`, `"min"`, `"max"`, `"count"`, …) or a literal. A summary or total
    with no `values` sums each numeric column. Each annotation is optional.
    Named reducers and portable counts track browser search; arbitrary Python
    callbacks run on data refresh and retain their source scope during search.
    """)
    return


@app.cell
def _(EvidentialTable, col, detail, mo, rows):
    regional_layout = (
        rows.group_by("region")
        .section()
        .summary(
            label="Regional average",
            values={"arr": "mean"},
        )
        .grand_summary(label="All regions")
    )
    table = mo.ui.anywidget(
        EvidentialTable(
            detail,
            row_layout=regional_layout,
            title="Annual recurring revenue",
            subtitle="A section per region, a custom average, and a grand total",
            row_lines=False,
            border=False,
            page_size=4,
            row_shading=True,
            row_numbers=True,
            download=True,
            section_indent=1,
            columns=[
                col.text("region"),
                col.text("country"),
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
    ## A heading with values

    `values={"arr": "sum", "accounts": "count"}` reuses the shared aggregation
    names. A heading can show totals and formatted text such as
    `rows.count(suffix=" countries")`. Numeric detail columns can hold text in
    annotation cells without running through a numeric mark or formatter.
    Only the details consume page slots. Move forward to see **(cont.)** headings;
    each group summary stays with its final detail, and the grand summary appears
    once on the final page.
    """)
    return


@app.cell
def _(EvidentialTable, col, detail, mo, rows):
    heading_layout = (
        rows.group_by("region")
        .section(values={"country": rows.count(suffix=" countries"), "arr": "sum", "accounts": "sum"}, rule="below")
        .grand_summary()
    )
    second = mo.ui.anywidget(
        EvidentialTable(
            detail,
            row_layout=heading_layout,
            title="Aggregations by name",
            row_lines="gray",
            border=False,
            page_size=5,
            row_shading=True,
            section_indent=1,
            columns=[
                col.text("region"),
                col.text("country"),
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

    - `table.rows` contains only details; annotations live in `table.row_layout`.
      Statistics, domains, detail callables and CSV exports use only details.
    - `.group_by(...)` accepts multiple dimensions for nested groups and
      preserves first-appearance order; sorting reorders details within groups.
    - `.summary(position="top")` puts the summary above its group; the default is
      `"bottom"`.
    - `.grand_summary(values={...})` overrides the default numeric-column sums;
      `.total()` remains an alias. Omit the call to omit the grand summary.
    - `.section(align="center")` makes a full-width heading without values.
      Each annotation accepts its own `style`, `rule`, and `label_column`.
    - Search hides empty groups and recalculates named aggregates over all
      matching details across pages. Counts in callable labels retain their
      source scope; prefer portable count values when they should track search.
    - The bound `rows.of(detail)...build()` spelling returns a detail-only
      `RowView` with a separate layout. `table.display_rows` is an unfiltered
      inspection snapshot including annotations.
    """)
    return


if __name__ == "__main__":
    app.run()
