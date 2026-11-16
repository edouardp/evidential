# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""A single set of colours in light, dark and automatic modes."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo

    from evidential import DimensionGrid, EvidentialTable, col, color, label

    return DimensionGrid, EvidentialTable, col, color, label, mo


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # One palette, two modes

    The tables below share their data and column declarations. UI colours follow
    the chosen scheme. Named palettes adapt automatically; `adapt_colors=True`
    also adapts literal data colours. It raises lightness while retaining hue,
    opacity and palette order. It never changes values or numeric domains.

    Literal white stays white: use `color.theme("neutral", alpha=0.8)` when you
    mean a partially transparent neutral surface. `color.fixed("#dc2626")`
    preserves an exact brand or reference colour even with adaptation enabled.
    Hover over the marks to compare tooltip swatches with their legends.
    """)
    return


@app.cell
def sample_data(col, color, label):
    theme_data = [
        {"region": "West", "sales": 80, "service": 20, "change": -8, "history": [3, 6, 4, 8, 9, 8]},
        {"region": "East", "sales": 65, "service": 35, "change": -3, "history": [6, 4, 8, 5, 9, 7]},
        {"region": "North", "sales": 50, "service": 50, "change": 0, "history": [2, 4, 7, 6, 5, 8]},
        {"region": "South", "sales": 30, "service": 70, "change": 7, "history": [8, 5, 4, 8, 6, 9]},
    ]
    theme_columns = [
        col.text("region", info="Illustrative sales regions"),
        col.stacked_bar(
            "sales", "service", colors=["#245a81", color.fixed("#dc2626")], title="Revenue mix", labels="percent"
        ).legend(),
        col.bar("change", center=True, label=label.fmt("num0").auto_position("outside end"))
        .gradient(scale=["#b91c1c", color.theme("neutral", alpha=0.8), "#1d4ed8"], min=-10, max=10, midpoint=0)
        .scale(domain=(-10, 10), gradient=True, axis_position="bottom"),
        col.sparkline("history", type="area", width=110, height=28, fill_opacity=(0, 0.7)).color(scale="green"),
    ]
    return theme_columns, theme_data


@app.cell(hide_code=True)
def theme_light_doc(mo):
    mo.md("""
    ### Light and dark

    Tables and DimensionGrid support `color_scheme="auto"`, `"light"` and
    `"dark"`. Automatic mode follows the notebook or host theme first, then
    the operating system. It is the default.

    These examples share one set of illustrative regional sales and the same
    columns. Named palettes adapt automatically. Set `adapt_colors=True` to
    adapt custom data colours too; otherwise literal colours stay exact.
    """)
    return


@app.cell
def theme_light(EvidentialTable, mo, theme_columns, theme_data):
    light_table = mo.ui.anywidget(
        EvidentialTable(
            theme_data,
            columns=theme_columns,
            color_scheme="light",
            adapt_colors=True,
            title="Regional sales · light",
            row_shading=True,
            border=False,
            page_size=0,
            width=800,
        )
    )
    light_table
    return (light_table,)


@app.cell(hide_code=True)
def theme_dark_doc(mo):
    mo.md("""
    The same colours in dark mode. Adaptation preserves hue, opacity, palette
    order and numeric domains. Marks, legends and tooltip swatches agree.

    Use `color.theme("neutral", alpha=0.8)` for a diverging palette's centre:
    it follows the surface and lets stripes show through. Use
    `color.fixed("#dc2626")` to preserve an exact colour, as the red segments do
    here. Both helpers come from `from evidential import color`.

    [Notebook 64](notebooks/64_light_dark.py) also demonstrates a live mode
    selector, points, chips, gradients and DimensionGrid.
    """)
    return


@app.cell
def theme_dark(EvidentialTable, mo, theme_columns, theme_data):
    dark_table = mo.ui.anywidget(
        EvidentialTable(
            theme_data,
            columns=theme_columns,
            color_scheme="dark",
            adapt_colors=True,
            title="Regional sales · dark",
            row_shading=True,
            border=False,
            page_size=0,
            width=800,
        )
    )
    dark_table
    return (dark_table,)


@app.cell
def controls(mo):
    mode = mo.ui.dropdown(["auto", "light", "dark"], value="auto", label="Colour scheme")
    adapt = mo.ui.checkbox(value=True, label="Adapt literal colours")
    mo.hstack([mode, adapt], justify="start")
    return adapt, mode


@app.cell
def interactive_tables(DimensionGrid, EvidentialTable, col, mo, theme_data):
    interactive_table = mo.ui.anywidget(
        EvidentialTable(
            theme_data,
            columns=[
                col.text("region"),
                col.number("sales").color(scale="blue"),
                col.number("service").chip(scale="purple"),
                col.points(["sales", "service"], palette="viridis", connect=True)
                .legend()
                .scale(domain=(0, 100), axis=True),
            ],
            title="Change mode without losing table state",
            search=True,
            page_size=2,
            freeze_columns=1,
            width=800,
        )
    )
    dimension_grid = mo.ui.anywidget(
        DimensionGrid(
            theme_data,
            dimensions=["region"],
            metric="sales",
            title="Filter regions",
            height=140,
        )
    )
    mo.vstack([interactive_table, dimension_grid])
    return dimension_grid, interactive_table


@app.cell
def update_mode(adapt, dimension_grid, interactive_table, mode):
    interactive_table.widget.update_options(color_scheme=mode.value, adapt_colors=adapt.value)
    dimension_grid.widget.options = {
        **dimension_grid.widget.options,
        "color_scheme": mode.value,
        "adapt_colors": adapt.value,
    }
    return


if __name__ == "__main__":
    app.run()
