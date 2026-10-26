# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""The README's table layout gallery: descriptions, real calls and screenshots.

Run ``make readme`` to extract the named cells and capture their widget output.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, Rows, col, rows, settings

    return EvidentialTable, Rows, col, duckdb, mo, rows, settings


@app.cell
def _(duckdb):
    con = duckdb.connect()
    con.sql("""
        CREATE TABLE orders AS
        SELECT * FROM (VALUES
            ('North', 'Aster lamp', 12, 15, 1200, 720, 'Includes the October launch order.'),
            ('North', 'Cove lamp', 18, 20, 1800, 990, NULL),
            ('North', 'Horizon lamp', 9, 10, 900, 540, NULL),
            ('South', 'Reed chair', 8, 12, 1600, 880, 'Stock was limited during the month.'),
            ('South', 'Studio chair', 14, 15, 2800, 1680, NULL),
            ('South', 'Field chair', 11, 12, 2200, 1210, NULL)
        ) AS source(region, product, units, target_units, sales, cost, note)
    """)
    return (con,)


@app.cell
def _(col, settings):
    layout_columns = [
        col.text("product"),
        col.integer("units"),
        col.currency("sales", decimals=0),
    ]
    layout_frame = settings(width="640px", search=False, sortable=False, page_size=0)
    return layout_columns, layout_frame


@app.cell(hide_code=True)
def layout_simple_doc(mo):
    mo.md(r"""
    ### Table layout gallery

    The frame, rules, notes and summaries are independent of cell graphics. These
    examples query an illustrative DuckDB `orders` table with six product records.
    Each query lists the fields it needs, including fields used only for grouping
    or footnotes. The notebook creates `con` and the table before the examples.
    They share basic columns and a settings bundle for width and disabled search,
    sorting and pagination. Excerpts use
    `...` for those shared column/settings references; follow a source link for
    the complete runnable setup. Inline definitions and layout options stay visible.

    #### Simple table

    Start with the standard frame, header and row rules.
    """)
    return


@app.cell
def layout_simple(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(con.sql("SELECT product, units, sales FROM orders"), columns=layout_columns, settings=layout_frame)
    return


@app.cell(hide_code=True)
def layout_titles_doc(mo):
    mo.md(r"""
    #### Title, subtitle and caption

    Use the title for the subject, the subtitle for context, and the caption for
    a source or explanatory note.
    """)
    return


@app.cell
def layout_titles(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        title="Products by region",
        subtitle="Six products · October 2026",
        caption="Source: illustrative product sales. Amounts in US dollars.",
    )
    return


@app.cell(hide_code=True)
def layout_footnotes_doc(mo):
    mo.md(r"""
    #### Footnotes

    Attach notes to source fields with `.footnote(...)`. Matching cells receive
    superscript symbols and their notes appear below the table.
    """)
    return


@app.cell
def layout_footnotes(EvidentialTable, con, layout_frame, col):
    EvidentialTable(
        con.sql("SELECT product, units, sales, note FROM orders"),
        columns=[
            col.text("product").footnote("note"),
            col.integer("units"),
            col.currency("sales", decimals=0),
        ],
        settings=layout_frame,
    )
    return


@app.cell(hide_code=True)
def layout_lines_on_doc(mo):
    mo.md(r"""
    #### Row lines on

    Horizontal rules separate each detail row. The outer frame is controlled
    separately with `border`.
    """)
    return


@app.cell
def layout_lines_on(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=True,
    )
    return


@app.cell(hide_code=True)
def layout_lines_off_doc(mo):
    mo.md(r"""
    #### Row lines off

    Keep the header and final table rules while removing the lines between rows.
    """)
    return


@app.cell
def layout_lines_off(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
    )
    return


@app.cell(hide_code=True)
def layout_frame_doc(mo):
    mo.md(r"""
    #### Outer frame

    An outer border can enclose the table even when internal row lines are off.
    """)
    return


@app.cell
def layout_frame(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=True,
        row_lines=False,
    )
    return


@app.cell(hide_code=True)
def layout_shading_off_doc(mo):
    mo.md(r"""
    #### Row shading off

    Use a plain background without row lines or an outer frame.
    """)
    return


@app.cell
def layout_shading_off(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_shading=False,
    )
    return


@app.cell(hide_code=True)
def layout_shading_one_doc(mo):
    mo.md(r"""
    #### Shade alternate rows

    `row_shading=1` alternates one shaded row with one unshaded row.
    """)
    return


@app.cell
def layout_shading_one(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_shading=1,
    )
    return


@app.cell(hide_code=True)
def layout_shading_three_doc(mo):
    mo.md(r"""
    #### Shade blocks of three

    `row_shading=3` alternates three shaded rows with three unshaded rows.
    """)
    return


@app.cell
def layout_shading_three(EvidentialTable, con, layout_frame, layout_columns):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_shading=3,
    )
    return


@app.cell(hide_code=True)
def layout_headings_doc(mo):
    mo.md(r"""
    #### Group headings

    Introduce each region with a display-only heading. `section_indent=1` insets
    the product names by one rem beneath it. The six source records remain the
    detail data.
    """)
    return


@app.cell
def layout_headings(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        section_indent=1,
        row_layout=rows.group_by("region").section(rule="below"),
    )
    return


@app.cell(hide_code=True)
def layout_headings_centered_doc(mo):
    mo.md(r"""
    #### Centered group headings

    Center a heading across the full table width, with a rule above and below.
    This style keeps the detail labels flush left and has no heading value cells.
    """)
    return


@app.cell
def layout_headings_centered(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_layout=rows.group_by("region").section(align="center", rule="both"),
    )
    return


@app.cell(hide_code=True)
def layout_headings_column_doc(mo):
    mo.md(r"""
    #### Group labels in their own column

    Keep the region in bold beside its products, showing it only on the first
    detail row of each run. `.repeat_values(False)` blanks repeated display
    values without changing the data. Labels reappear at the start of each page and after a
    heading or summary; filtering and sorting use the full values.
    """)
    return


@app.cell
def layout_headings_column(EvidentialTable, con, layout_frame, col, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=[
            col.text("region").bold().repeat_values(False),
            col.text("product"),
            col.integer("units"),
            col.currency("sales", decimals=0),
        ],
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_layout=rows.group_by("region"),
    )
    return


@app.cell(hide_code=True)
def layout_heading_values_doc(mo):
    mo.md(r"""
    #### Headings with counts and totals

    A heading can combine a formatted label with aggregate values in the other
    columns. Here it shows the product count, total units and total sales, with
    indented product names underneath.
    """)
    return


@app.cell
def layout_heading_values(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        section_indent=1,
        row_layout=rows.group_by("region").section(
            label=lambda group: f"{group[0]['region']} · {len(group)} products",
            values={"units": "sum", "sales": "sum"},
            rule="below",
        ),
    )
    return


@app.cell(hide_code=True)
def layout_summary_top_doc(mo):
    mo.md(r"""
    #### Summaries before each group

    Place the region total above its detail rows. A summary can act as the group
    heading without an additional section row. Indent the product names beneath
    that summary with `section_indent=1`.
    """)
    return


@app.cell
def layout_summary_top(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        section_indent=1,
        row_layout=rows.group_by("region").summary(
            label=lambda group: f"{group[0]['region']} total",
            values={"units": "sum", "sales": "sum"},
            position="top",
            rule="below",
        ),
    )
    return


@app.cell(hide_code=True)
def layout_summary_bottom_doc(mo):
    mo.md(r"""
    #### Summary footers and subtotals

    Put a subtotal after each region, with a heading before the indented details.
    Headings and subtotal labels stay aligned at the left edge.
    """)
    return


@app.cell
def layout_summary_bottom(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        section_indent=1,
        row_layout=rows.group_by("region")
        .section()
        .summary("Region total", values={"units": "sum", "sales": "sum"}),
    )
    return


@app.cell(hide_code=True)
def layout_grand_total_doc(mo):
    mo.md(r"""
    #### Grand total

    Add one final summary across all source records, without group headings or
    subtotals.
    """)
    return


@app.cell
def layout_grand_total(EvidentialTable, con, layout_frame, layout_columns, Rows):
    EvidentialTable(
        con.sql("SELECT product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        row_layout=Rows().grand_summary("Grand total", values={"units": "sum", "sales": "sum"}),
    )
    return


@app.cell(hide_code=True)
def layout_combined_totals_doc(mo):
    mo.md(r"""
    #### Group summaries and a grand total

    Combine headings, indented details, region subtotals and a final grand total.
    Summaries read the detail records, so the grand total never counts subtotals
    twice.
    """)
    return


@app.cell
def layout_combined_totals(EvidentialTable, con, layout_frame, layout_columns, rows):
    EvidentialTable(
        con.sql("SELECT region, product, units, sales FROM orders"),
        columns=layout_columns,
        settings=layout_frame,
        border=False,
        row_lines=False,
        section_indent=1,
        row_layout=rows.group_by("region")
        .section()
        .summary("Region total", values={"units": "sum", "sales": "sum"})
        .grand_summary("Grand total", values={"units": "sum", "sales": "sum"}),
    )
    return


@app.cell(hide_code=True)
def layout_groups_one_doc(mo):
    mo.md(r"""
    #### Column groups: one level

    Place related columns under shared spanners. The product column remains an
    independent row label.
    """)
    return


@app.cell
def layout_groups_one(EvidentialTable, con, layout_frame, col):
    EvidentialTable(
        con.sql("SELECT product, units, target_units, sales, cost FROM orders"),
        settings=layout_frame,
        columns=[
            col.text("product"),
            col.group("Volume", [
                col.integer("units", title="Actual"),
                col.integer("target_units", title="Target"),
            ]),
            col.group("Money", [
                col.currency("sales", decimals=0),
                col.currency("cost", decimals=0),
            ]),
        ],
        border=False,
        row_lines=False,
    )
    return


@app.cell(hide_code=True)
def layout_groups_two_doc(mo):
    mo.md(r"""
    #### Column groups: two levels

    Nest spanners to describe a hierarchy. Here **Operations** contains **Volume**
    and **Money**, each with two leaf columns.
    """)
    return


@app.cell
def layout_groups_two(EvidentialTable, con, layout_frame, col):
    EvidentialTable(
        con.sql("SELECT product, units, target_units, sales, cost FROM orders"),
        settings=layout_frame,
        columns=[
            col.text("product"),
            col.group("Operations", [
                col.group("Volume", [
                    col.integer("units", title="Actual"),
                    col.integer("target_units", title="Target"),
                ]),
                col.group("Money", [
                    col.currency("sales", decimals=0),
                    col.currency("cost", decimals=0),
                ]),
            ]),
        ],
        border=False,
        row_lines=False,
    )
    return


if __name__ == "__main__":
    app.run()
