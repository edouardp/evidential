# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""Colour scales and conditional formatting (`viz="color"`)."""

import marimo

__generated_with = "0.20.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb

    from evidential import EvidentialTable

    return EvidentialTable, duckdb, mo


@app.cell
def _(duckdb):
    connection = duckdb.connect()
    _ = connection.execute(
        """
        CREATE TABLE demo AS
        SELECT * FROM (VALUES
            ('A',   0,  5, '#fecaca'),
            ('B',  15, 20, '#fecaca'),
            ('C',  35, 60, '#fef08a'),
            ('D',  50, 50, '#fef08a'),
            ('E',  65, 90, '#bbf7d0'),
            ('F',  85, 30, '#bbf7d0'),
            ('G', 100, 70, '#bbf7d0')
        ) AS t(label, value, other, band)
        """
    )
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Colour scales

    `viz="color"` shades a cell by its value. `color_options` controls the
    palette, bounds, midpoint, explicit stops and the column used for scaling;
    `conditional_colors` uses per-row hex values from another column instead.

    Every column below shades the same 0–100 `value`, so you can compare the
    effect of each option.
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    scales = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(
                """
                SELECT
                    label,
                    value,
                    value AS default_scale,
                    value AS custom_list,
                    value AS named_preset,
                    value AS bounded,
                    value AS diverging,
                    value AS stops,
                    value AS scaled_by_other,
                    value AS conditional,
                    other,
                    band
                FROM demo
                """
            ),
            title="Color scale options",
            page_size=10,
            row_lines=False,
            column_config={
                "label": {"title": "Row", "align": "left"},
                "value": {"title": "Value", "fmt": "num0", "align": "right"},
                # default two-colour scale
                "default_scale": {"title": "Default", "fmt": "num0", "viz": "color"},
                # explicit list of colours
                "custom_list": {
                    "title": "Custom list",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": ["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
                },
                # named preset
                "named_preset": {
                    "title": "Preset (blue)",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": "blue",
                },
                # clamp values above the max
                "bounded": {
                    "title": "Bounded 0–50",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": ["#eff6ff", "#1d4ed8"],
                    "color_options": {"min": 0, "max": 50},
                },
                # diverging scale anchored at 50
                "diverging": {
                    "title": "Diverging @50",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": ["#dc2626", "#f8fafc", "#16a34a"],
                    "color_options": {"midpoint": 50, "min": 0, "max": 100},
                },
                # explicit value→colour breakpoints
                "stops": {
                    "title": "Color stops",
                    "fmt": "num0",
                    "viz": "color",
                    "color_options": {
                        "color_stops": [
                            {"value": 0, "color": "#7f1d1d"},
                            {"value": 50, "color": "#fbbf24"},
                            {"value": 100, "color": "#065f46"},
                        ]
                    },
                },
                # scale by a different column than the displayed value
                "scaled_by_other": {
                    "title": "Scaled by 'other'",
                    "fmt": "num0",
                    "viz": "color",
                    "color_scale": "purple",
                    "color_options": {"scale_column": "other", "min": 0, "max": 100},
                },
                # per-row colours (conditional_colors names the hex column)
                "conditional": {
                    "title": "Conditional colors",
                    "fmt": "num0",
                    "viz": "color",
                    "color_options": {"conditional_colors": "band"},
                },
                "other": {"hide": True},
                "band": {"hide": True},
            },
        )
    )
    scales
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - `color_scale` accepts a list of colours or a named preset
      (`green`, `blue`, `red`, `orange`, `purple`, `grey`).
    - `min`/`max` clamp the domain; `midpoint` anchors a diverging palette.
    - `color_stops` pins colours to specific values (takes precedence).
    - `scale_column` shades a cell using another column's value (here `value`
      is shaded by `other`).
    - `conditional_colors` names a column of hex colours computed in SQL, e.g.
      `CASE WHEN sales > 1000 THEN '#dcfce7' ELSE '#fee2e2' END`.
    """)
    return


if __name__ == "__main__":
    app.run()
