# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Chips: a value in a rounded rectangle, coloured like a colour cell.

``viz="chip"`` renders the formatted value in a rounded rectangle. The fill
follows the same rules as ``viz="color"`` — a ``color_scale`` over the column's
range, or ``color_options={"conditional_colors": "<colour column>"}`` — and the
text colour is picked from the fill (white on darker fills, black on lighter
ones). Chips are centred by default; set ``align`` for another alignment.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col

    return EvidentialTable, col, mo


@app.cell
def _(mo):
    mo.md("""
    # Chips

    `viz="chip"` puts a value in a rounded rectangle. The fill uses the **same
    rules as `viz="color"`**:

    - a `color_scale` over the column's range (`color_options` for `min`/`max`,
      a midpoint, or explicit stops), or
    - `color_options={"conditional_colors": "<column>"}`, where that column
      holds a hex colour per row.

    The text colour reacts to the fill — white on darker fills, black on lighter
    ones — and chips are centred by default (set `align` to override).
    """)
    return


@app.cell
def _():
    records = [
        {"rank": 1, "city": "Singapore", "aqi": 217, "status": "Very unhealthy", "status_color": "#7e22ce"},
        {"rank": 2, "city": "Kuala Lumpur", "aqi": 210, "status": "Very unhealthy", "status_color": "#7e22ce"},
        {"rank": 3, "city": "Lahore", "aqi": 186, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 4, "city": "Hanoi", "aqi": 175, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 5, "city": "Dhaka", "aqi": 172, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 6, "city": "Kolkata", "aqi": 172, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 7, "city": "Delhi", "aqi": 169, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 8, "city": "Kinshasa", "aqi": 163, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 9, "city": "Beijing", "aqi": 163, "status": "Unhealthy", "status_color": "#dc2626"},
        {"rank": 10, "city": "Sydney", "aqi": 54, "status": "Moderate", "status_color": "#f59e0b"},
        {"rank": 11, "city": "Wellington", "aqi": 32, "status": "Good", "status_color": "#16a34a"},
    ]
    return (records,)


@app.cell
def _(EvidentialTable, col, mo, records):
    aqi_chip = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="A numeric chip with a colour scale",
            subtitle="color_scale from green to red, clamped to 0-250",
            row_shading=True,
            row_lines=False,
            stretch=False,
            columns=[
                col.text("rank", title="#"),
                col.text("city", title="Major city"),
                col.number("aqi", fmt="num0", title="AQI (US)").chip(
                    scale=["#16a34a", "#f59e0b", "#dc2626", "#7e22ce"], min=0, max=250
                )
            ],
        )
    )
    aqi_chip
    return


@app.cell
def _(mo):
    mo.md("""
    ## Conditional colours

    A **text** chip can take its colour from a per-row column
    (`conditional_colors`), or use no colour at all and fall back to a neutral
    fill. The colour column is hidden.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, records):
    status_chip = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="A text chip with conditional colours",
            subtitle="`color_options={'conditional_colors': 'status_color'}`",
            row_shading=True,
            stretch=False,
            columns=[
                col.text("rank", title="#"),
                col.text("city", title="Major city"),
                col.chip("status", title="Status", scale="@status_color"),
                col.auto("aqi").hide(),
                col.auto("status_color").hide(),
            ],
        )
    )
    status_chip
    return


@app.cell
def _(EvidentialTable, col, mo, records):
    neutral_chip = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="A chip without a colour scale",
            subtitle="No colour options: a neutral fill, centred",
            row_shading=True,
            stretch=False,
            columns=[
                col.auto("rank").hide(),
                col.text("city"),
                col.chip("status", title="Category"),
            ],
        )
    )
    neutral_chip
    return


@app.cell
def _(EvidentialTable, col, mo, records):
    sized_chip = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="Chips with a minimum width",
            subtitle='`chip_options={"min_width": 72}` — short values are padded, long ones expand',
            row_shading=True,
            stretch=False,
            columns=[
                col.text("city"),
                col.number("aqi", title="AQI (US)").chip(
                    min_width=72, scale="ylorrd", min=0, max=250
                ),
                col.chip("status", title="Status", min_width=72, scale="@status_color"),
            ],
        )
    )
    sized_chip
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `viz="chip"` reuses `viz="color"`'s options: `color_scale`, `color_stops`,
      `conditional_colors`, `scale_column`, `min`/`max`/`midpoint`.
    - `scale` takes a list of colours, a **named scale** — the Evidence presets
      plus the 30 matplotlib colormaps (`viridis`, `RdBu`, `ylorrd`, …) — or
      `"@column"` to shade each chip from another column.
    - The text is black or white by the fill's luminance, so it stays legible.
    - Chips are centred unless the column sets `align` (`left` or `right`).
    - `chip_options={"min_width": 72}` gives a column of chips a common minimum
      width (the whole chip, padding included); a longer value still expands the
      chip. `chip_min_width` is a top-level alias.
    - `content_type="chip"` is an alias for `viz="chip"`.
    """)
    return


if __name__ == "__main__":
    app.run()
