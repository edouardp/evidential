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

    from evidential import EvidentialTable, col

    return EvidentialTable, col, duckdb, mo


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
def _(EvidentialTable, col, connection, mo):
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
            columns=[
                col.text("label", title="Row"),
                col.number("value", fmt="num0", title="Value"),
                # default two-colour scale
                col.number("default_scale", fmt="num0", title="Default").color(),
                # explicit list of colours
                col.number("custom_list", fmt="num0", title="Custom list").color(
                    scale=["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"]
                ),
                # named preset
                col.number("named_preset", fmt="num0", title="Preset (blue)").color(scale="blue"),
                # clamp values above the max
                col.number("bounded", fmt="num0", title="Bounded 0–50").color(
                    scale=["#eff6ff", "#1d4ed8"], min=0, max=50
                ),
                # diverging scale anchored at 50
                col.number("diverging", fmt="num0", title="Diverging @50").color(
                    scale=["#dc2626", "#f8fafc", "#16a34a"], min=0, max=100, midpoint=50
                ),
                # explicit value→colour breakpoints
                col.number("stops", fmt="num0", title="Color stops").color(
                    stops=[
                        {"value": 0, "color": "#7f1d1d"},
                        {"value": 50, "color": "#fbbf24"},
                        {"value": 100, "color": "#065f46"},
                    ]
                ),
                # scale by a different column than the displayed value
                col.number("scaled_by_other", fmt="num0", title="Scaled by 'other'").color(
                    scale="purple", scale_column="other", min=0, max=100
                ),
                # per-row colours (conditional_colors names the hex column)
                col.number("conditional", fmt="num0", title="Conditional colors").color(
                    conditional_colors="band"
                ),
                col.auto("other").hide(),
                col.auto("band").hide(),
            ],
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
