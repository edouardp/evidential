# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""gt-inspired features: nested spanners, a stub, markdown titles, and
location-based style/format/transform rules."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import (
        EvidentialTable,
        cells_body,
        tab_format,
        tab_style,
        text_transform,
    )

    return EvidentialTable, cells_body, mo, tab_format, tab_style, text_transform


@app.cell
def _(mo):
    mo.md("""
    # gt-inspired parts

    - **Nested spanners** — `column_group=["2021", "Sales"]` gives multi-level
      column headers.
    - **Stub** — `stub="product"` marks the row-label column; `stub_head` labels it.
    - **Markdown titles** — inline `**bold**`, `*italic*`, `` `code` ``.
    - **Location rules** — `tab_style` / `tab_format` / `text_transform` target
      sets of cells via `cells_body(columns, rows)`, where `rows` is indices or a
      Python predicate on the row.
    """)
    return


@app.cell
def _():
    rows = [
        {"product": "Widget", "sales_2021": 1200, "orders_2021": 40, "sales_2022": 1500, "orders_2022": 52},
        {"product": "Gadget", "sales_2021": 900, "orders_2021": 30, "sales_2022": 700, "orders_2022": 22},
        {"product": "Gizmo", "sales_2021": 1500, "orders_2021": 50, "sales_2022": 2100, "orders_2022": 70},
    ]

    columns = [
        {"name": "product", "type": "string"},
        {"name": "sales_2021", "type": "number", "title": "Sales", "column_group": ["2021", "Sales"]},
        {"name": "orders_2021", "type": "number", "title": "Orders", "column_group": ["2021", "Orders"]},
        {"name": "sales_2022", "type": "number", "title": "Sales", "column_group": ["2022", "Sales"]},
        {"name": "orders_2022", "type": "number", "title": "Orders", "column_group": ["2022", "Orders"]},
    ]
    return columns, rows


@app.cell
def _(EvidentialTable, cells_body, mo, rows, tab_format, tab_style, text_transform, columns):
    mo.ui.anywidget(
        EvidentialTable(
            rows,
            columns=columns,
            title="**Annual** performance",
            subtitle="Nested spanners · stub · location rules",
            stub="product",
            stub_head="Product",
            row_shading=True,
            rules=[
                # highlight products whose 2022 sales fell below 2021
                tab_style(
                    cells_body(
                        columns=["sales_2022"],
                        rows=lambda row: row["sales_2022"] < row["sales_2021"],
                    ),
                    background="#fee2e2",
                    color="#b91c1c",
                    font_weight="600",
                ),
                # format both sales columns as currency
                tab_format(cells_body(columns=["sales_2021", "sales_2022"]), "usd0"),
                # normalise the stub labels
                text_transform(cells_body(columns="product"), str.upper),
            ],
        )
    )
    return


if __name__ == "__main__":
    app.run()
