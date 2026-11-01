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

__generated_with = "0.25.1"
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
                    value AS mpl_viridis,
                    value AS mpl_rdbu,
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
                col.number("value", fmt="num0"),
                # default two-colour scale
                col.number("default_scale", fmt="num0", title="Default").color(),
                # explicit list of colours
                col.number("custom_list", fmt="num0", title="Custom list").color(
                    scale=["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"]
                ),
                # named preset
                col.number("named_preset", fmt="num0", title="Preset (green)").color(scale="green"),
                # matplotlib colormaps (perceptually uniform, and diverging)
                col.number("mpl_viridis", fmt="num0", title="viridis").color(scale="viridis"),
                col.number("mpl_rdbu", fmt="num0", title="RdBu @50").color(scale="rdbu", midpoint=50),
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
                col.number("conditional", fmt="num0", title="Conditional colors").color(conditional_colors="band"),
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

    - `color_scale` accepts a list of colours, or a named scale. Named scales are
      the six presets (`green`, `blue`, `red`, `orange`, `purple`, `grey`) plus
      **30 matplotlib colormaps** (`viridis`, `magma`, `plasma`, `inferno`,
      `cividis`, the sequential `Blues`…`YlOrRd`, and the diverging `RdBu`,
      `RdYlBu`, `coolwarm`, `bwr`, `Spectral`, …). Names are case-insensitive.
    - `min`/`max` clamp the domain; `midpoint` anchors a diverging palette (used by
      the `RdBu @50` column).
    - `color_stops` pins colours to specific values (takes precedence).
    - `scale_column` shades a cell using another column's value (here `value`
      is shaded by `other`).
    - `conditional_colors` names a column of hex colours computed in SQL, e.g.
      `CASE WHEN sales > 1000 THEN '#dcfce7' ELSE '#fee2e2' END` — or `scale="@band"`.
    - An unknown scale name raises, with a suggestion.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## matplotlib colour names

    Wherever a colour is expected, matplotlib's names work too: `tab:blue` …
    `tab:cyan`, `C0`–`C9` (indexing the Tableau palette), and the single-letter
    `b g r c m y k w`. The same bars in three spellings:
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    names = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("SELECT label, value FROM demo"),
            title="matplotlib colour names",
            row_lines=False,
            columns=[
                col.text("label"),
                col.bar("value", title="tab:blue", color="tab:blue", fit_to_data=True),
                col.bar("value", title="C1", color="C1", fit_to_data=True),
                col.bar("value", title="k", color="k", fit_to_data=True),
            ],
        )
    )
    names
    return


@app.cell(hide_code=True)
def transparency_doc(mo):
    mo.md("""
    ## Translucent colors preserve row stripes

    Give individual color stops an alpha value. White at **80% opacity** is
    `rgba(255,255,255,0.8)` or `#ffffffcc`; fully transparent white is `#ffffff00`.
    The red and blue endpoints below stay opaque. Intermediate colors interpolate
    alpha too: halfway to the 80%-opaque neutral they are 90% opaque.

    ```python
    col.number("value").color(
        scale=["red", "#ffffffcc", "blue"], min=-1, max=1, midpoint=0
    )
    ```

    Compare the two zero rows: opaque white hides the stripe, 80%-opaque white
    lets 20% of it show through, and transparent white exposes the whole stripe.
    The last column uses `.cell_style(background="#ffffffcc")` instead of a
    gradient. Text and graphical marks keep their own opacity. Hover a row to
    see the row highlight through the fill as well.
    """)
    return


@app.cell
def transparent_colors(EvidentialTable, col, mo):
    _values = [
        ("Negative", -1),
        ("Halfway", -0.5),
        ("Neutral A", 0),
        ("Neutral B", 0),
        ("Halfway", 0.5),
        ("Positive", 1),
    ]
    _rows = [{"case": name, **dict.fromkeys(["opaque", "soft", "clear", "fixed"], value)} for name, value in _values]
    transparency_table = EvidentialTable(
        _rows,
        columns=[
            col.text("case"),
            col.number("opaque", title="Opaque neutral", format="num1").color(
                scale=["red", "white", "blue"], min=-1, max=1, midpoint=0
            ),
            col.number("soft", title="80% opaque neutral", format="num1").color(
                scale=["red", "#ffffffcc", "blue"], min=-1, max=1, midpoint=0
            ),
            col.number("clear", title="Transparent neutral", format="num1").color(
                scale=["red", "#ffffff00", "blue"], min=-1, max=1, midpoint=0
            ),
            col.number("fixed", title="Constant white (80%)", format="num1").cell_style(background="#ffffffcc"),
        ],
        title="Color fills over row stripes",
        caption="The stripes are deliberately darker here to make the show-through easier to see.",
        theme={"shading": "#aebdce"},
        row_shading=True,
        row_lines=False,
        border=False,
        search=False,
        sortable=False,
        page_size="all",
        width=900,
    )
    mo.ui.anywidget(transparency_table)
    return (transparency_table,)


if __name__ == "__main__":
    app.run()
