# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidence-tables",
# ]
# ///
"""Highlight an entire column or column group with a colour.

A column's ``highlight`` paints a vertical band — its header and every cell —
with a background colour. A whole column group can be highlighted by giving the
``column_groups`` entry a ``highlight`` (which applies it to each column, and the
spanner once they all share it). A column highlight wins over its group's.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidence_tables import EvidenceTable

    return EvidenceTable, mo


@app.cell
def _(mo):
    mo.md("""
    # Column highlights

    Set a column's `highlight` to a colour and it paints a **vertical band** —
    the header and every cell — like a "projection" or "total" column:

    ```python
    column_config={"usd_2020": {"title": "2020 Projection", "highlight": "#fde8d0"}}
    ```

    A whole **column group** can be highlighted by giving its `column_groups`
    entry a highlight:

    ```python
    column_groups={"Billions of USD": {"columns": [...], "highlight": "#eef2ff"}}
    ```

    The spanner is filled only when every column it spans shares the highlight,
    so a single highlighted column inside a group does not tint the spanner.
    """)
    return


@app.cell
def _():
    records = [
        {"country": "Australia", "usd_2017": -35, "usd_2018": -29, "usd_2019": 8, "usd_2020": 15, "pct_2017": -2.6, "pct_2018": -2.0, "pct_2019": 0.6, "pct_2020": 1.2},
        {"country": "Canada", "usd_2017": -46, "usd_2018": -43, "usd_2019": -35, "usd_2020": -57, "pct_2017": -2.8, "pct_2018": -2.5, "pct_2019": -2.0, "pct_2020": -3.7},
        {"country": "Germany", "usd_2017": 297, "usd_2018": 292, "usd_2019": 275, "usd_2020": 199, "pct_2017": 7.8, "pct_2018": 7.4, "pct_2019": 7.1, "pct_2020": 5.6},
        {"country": "Japan", "usd_2017": 203, "usd_2018": 177, "usd_2019": 184, "usd_2020": 157, "pct_2017": 4.2, "pct_2018": 3.6, "pct_2019": 3.6, "pct_2020": 3.2},
        {"country": "United Kingdom", "usd_2017": -99, "usd_2018": -111, "usd_2019": -107, "usd_2020": -88, "pct_2017": -3.5, "pct_2018": -3.9, "pct_2019": -3.8, "pct_2020": -3.5},
        {"country": "United States", "usd_2017": -440, "usd_2018": -491, "usd_2019": -498, "usd_2020": -402, "pct_2017": -2.3, "pct_2018": -2.4, "pct_2019": -2.3, "pct_2020": -2.0},
    ]
    return (records,)


@app.cell
def _(EvidenceTable, mo, records):
    projection = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="Selected economies: current account balance, 2017-20",
            subtitle="The 2020 Projection column is highlighted in both groups",
            row_shading=True,
            column_groups={
                "Billions of USD": ["usd_2017", "usd_2018", "usd_2019", "usd_2020"],
                "Percent of GDP": ["pct_2017", "pct_2018", "pct_2019", "pct_2020"],
            },
            column_config={
                "country": {"align": "left"},
                "usd_2017": {"title": "2017", "fmt": "num0"},
                "usd_2018": {"title": "2018", "fmt": "num0"},
                "usd_2019": {"title": "2019", "fmt": "num0"},
                "usd_2020": {"title": "2020\nProjection", "fmt": "num0", "highlight": "#fde8d0"},
                "pct_2017": {"title": "2017", "fmt": "num1"},
                "pct_2018": {"title": "2018", "fmt": "num1"},
                "pct_2019": {"title": "2019", "fmt": "num1"},
                "pct_2020": {"title": "2020\nProjection", "fmt": "num1", "highlight": "#fde8d0"},
            },
        )
    )
    projection
    return


@app.cell
def _(mo):
    mo.md("""
    ## Highlighting a whole group

    A `column_groups` entry can be a mapping with its `columns` and a
    `highlight`. Every column in the group, and the spanner above them, take the
    colour.
    """)
    return


@app.cell
def _(EvidenceTable, mo, records):
    group_band = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="The projected years, highlighted as a group",
            row_shading=True,
            column_groups={
                "History": ["usd_2017", "usd_2018", "usd_2019"],
                "Projected": {"columns": ["usd_2020"], "highlight": "#eef2ff"},
            },
            column_config={
                "country": {"align": "left"},
                "usd_2017": {"title": "2017", "fmt": "num0"},
                "usd_2018": {"title": "2018", "fmt": "num0"},
                "usd_2019": {"title": "2019", "fmt": "num0"},
                "usd_2020": {"title": "2020", "fmt": "num0"},
                "pct_2017": {"hide": True},
                "pct_2018": {"hide": True},
                "pct_2019": {"hide": True},
                "pct_2020": {"hide": True},
            },
        )
    )
    group_band
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `highlight` is a column option (also `highlightColor` / `highlight_color`);
      it paints the header and every data cell.
    - A group highlight sets `highlight` on each of its columns unless the column
      already has one — so a column can override its group.
    - The band sits above `row_shading` (it is painted inline), so it stays a
      continuous vertical stripe; hovering a row still tints it.
    """)
    return


if __name__ == "__main__":
    app.run()
