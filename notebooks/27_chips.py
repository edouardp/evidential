# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidence-tables",
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

    from evidence_tables import EvidenceTable

    return EvidenceTable, mo


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
def _(EvidenceTable, mo, records):
    aqi_chip = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="A numeric chip with a colour scale",
            subtitle="color_scale from green to red, clamped to 0-250",
            row_shading=True,
            row_lines=False,
            column_config={
                "rank": {"title": "#", "align": "left"},
                "city": {"title": "Major city", "align": "left"},
                "aqi": {
                    "title": "AQI (US)",
                    "viz": "chip",
                    "fmt": "num0",
                    "color_scale": ["#16a34a", "#f59e0b", "#dc2626", "#7e22ce"],
                    "color_options": {"min": 0, "max": 250},
                },
                "status": {"hide": True},
                "status_color": {"hide": True},
            },
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
def _(EvidenceTable, mo, records):
    status_chip = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="A text chip with conditional colours",
            subtitle="color_options={'conditional_colors': 'status_color'}",
            row_shading=True,
            column_config={
                "rank": {"title": "#", "align": "left"},
                "city": {"title": "Major city", "align": "left"},
                "status": {
                    "title": "Status",
                    "viz": "chip",
                    "color_options": {"conditional_colors": "status_color"},
                },
                "aqi": {"hide": True},
                "status_color": {"hide": True},
            },
        )
    )
    status_chip
    return


@app.cell
def _(EvidenceTable, mo, records):
    neutral_chip = mo.ui.anywidget(
        EvidenceTable(
            records,
            title="A chip without a colour scale",
            subtitle="No colour options: a neutral fill, centred",
            row_shading=True,
            column_config={
                "rank": {"hide": True},
                "city": {"align": "left"},
                "status": {"title": "Category", "viz": "chip"},
                "aqi": {"hide": True},
                "status_color": {"hide": True},
            },
        )
    )
    neutral_chip
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `viz="chip"` reuses `viz="color"`'s options: `color_scale`, `color_stops`,
      `conditional_colors`, `scale_column`, `min`/`max`/`midpoint`.
    - The text is black or white by the fill's luminance, so it stays legible.
    - Chips are centred unless the column sets `align` (`left` or `right`).
    - `content_type="chip"` is an alias for `viz="chip"`.
    """)
    return


if __name__ == "__main__":
    app.run()
