# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Dumbbells: ordered endpoints, negative range colors and direction markers."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, mo, settings


@app.cell
def introduction(mo):
    mo.md("""
    # Dumbbell plots

    A dumbbell combines a range with two independently styled points. The first
    field is **before** and the second is **after**: their order carries meaning,
    even when the second value is smaller.

    Add `color_negative=` to color a decrease, and `direction_marker=True` to
    place a chevron halfway along the connecting line. Both are optional.
    Blue dots show before; red dots show after. These sales are illustrative.
    """)
    return


@app.cell
def example_data():
    sales = [
        {"country": "Finland", "before": 29, "after": 94},
        {"country": "Sweden", "before": 76, "after": 41},
        {"country": "Norway", "before": 27, "after": 47},
        {"country": "Denmark", "before": 15, "after": 19},
        {"country": "Iceland", "before": 10, "after": 20},
    ]
    return (sales,)


@app.cell
def chart_style(col, settings):
    report = settings(
        border=False,
        row_lines=False,
        row_shading=True,
        search=False,
        page_size=0,
        width=440,
    )

    def sales_column(**options):
        return (
            col.range("before", "after", color="#222222", size=2, **options)
               .point("before", color="#6699ee", outline="#2f5fa8", size=12)
               .point("after", color="#ff6666", outline="#cc1111", size=12)
               .title("Weekly Sales").align("center")
               .scale(domain=(0, 100), axis=True, axis_position="bottom")
        )

    return report, sales_column


@app.cell
def comparison(EvidentialTable, col, mo, report, sales, sales_column):
    plain = mo.ui.anywidget(
        EvidentialTable(
            sales,
            settings=report,
            title="Plain dumbbells",
            columns=[col.text("country"), sales_column()],
        )
    )
    negative = mo.ui.anywidget(
        EvidentialTable(
            sales,
            settings=report,
            title="Color decreases",
            columns=[col.text("country"), sales_column(color_negative="#cc1111")],
        )
    )
    mo.hstack([plain, negative], justify="start", gap=3, wrap=True)
    return


@app.cell
def reference_style(EvidentialTable, col, mo, report, sales, sales_column):
    directed = mo.ui.anywidget(
        EvidentialTable(
            sales,
            settings=report,
            title="Color and direction",
            subtitle="Chevron points from before to after",
            columns=[
                col.text("country"),
                sales_column(color_negative="#cc1111", direction_marker=True)
            ],
        )
    )
    mo.vstack([directed])
    return


@app.cell
def signed_changes(EvidentialTable, col, mo, report):
    signed = mo.ui.anywidget(
        EvidentialTable(
            [
                {"case": "Increase below zero", "before": -8, "after": -3},
                {"case": "Decrease below zero", "before": -3, "after": -8},
                {"case": "No change", "before": 4, "after": 4},
                {"case": "Missing after", "before": 3, "after": None},
            ],
            settings=report,
            title="Direction follows the change",
            subtitle="Negative values can still increase; equal values have no chevron",
            columns=[
                col.text("case"),
                col.range("before", "after", color="#222222", color_negative="#cc1111", size=2, direction_marker=True)
                .point("before", color="#6699ee", outline="#2f5fa8", size=12)
                .point("after", color="#ff6666", outline="#cc1111", size=12)
                .title("Before → After").align("center")
                .scale(domain=(-10, 10), axis=True, axis_position="bottom"),
            ],
        )
    )
    mo.vstack([signed])
    return


@app.cell
def notes(mo):
    mo.md("""
    ```python
    (
        col.range("before", "after", color="black", color_negative="red",
                  direction_marker=True, size=2)
        .point("before", color="#6699ee", size=12)
        .point("after", color="#ff6666", size=12)
    )
    ```

    - `color_negative` compares **after < before**, rather than checking if
      either endpoint is negative. It also accepts `"@column"` or a callable.
    - Equal endpoints have no direction marker. Missing endpoints suppress the
      connecting range; any available endpoint dot remains visible.
    - The chevron follows the displayed direction, including on a logarithmic
      or reversed scale. It is independent of endpoint caps and overflow arrows.
    - Point colors remain independent of the connecting range's colors.
    """)
    return


@app.cell(hide_code=True)
def overlapping_values_doc(mo):
    mo.md("""
    ## Overlapping endpoints and comparison points

    These illustrative values are printed beside the graphic. Opaque dots whose
    centres fit within **one CSS pixel** become one segmented circle: halves,
    thirds or quarters. Hover it for every named value. The nearly-equal row
    also merges at this width. Resize the table and pixel-space clusters update.

    The separate example uses translucent dots, so its ordinary colour compositing is
    preserved. A sequence of small steps does not form one long cluster: the
    **whole cluster**, rather than just each adjacent gap, must fit inside 1px.
    Different-sized dots also retain their size encoding.
    """)
    return


@app.cell
def overlapping_values(EvidentialTable, col, mo, settings):
    overlap_values = [
        {"case": "Two equal", "before": 50, "after": 50, "target": None, "forecast": None},
        {"case": "Three equal", "before": 50, "after": 50, "target": 50, "forecast": None},
        {"case": "Four equal", "before": 50, "after": 50, "target": 50, "forecast": 50},
        {"case": "Nearly equal", "before": 50, "after": 50.01, "target": 50.02, "forecast": 50.03},
        {"case": "Two separate pairs", "before": 30, "after": 30, "target": 70, "forecast": 70},
        {"case": "All separated", "before": 20, "after": 40, "target": 60, "forecast": 80},
        {"case": "Small steps, bounded clusters", "before": 50, "after": 50.2, "target": 50.4, "forecast": 50.6},
    ]
    overlap_table = mo.ui.anywidget(
        EvidentialTable(
            overlap_values,
            columns=[
                col.text("case"),
                col.number("before", format="num2"),
                col.number("after", format="num2"),
                col.number("target", format="num2"),
                col.number("forecast", format="num2"),
                col.points({"before": "Before", "after": "After", "target": "Target", "forecast": "Forecast"},
                    palette=["#2563eb", "#dc2626", "#16a34a", "#9333ea"], size=18, connect=True)
                .title("Comparison").fmt("num2").scale(domain=(0, 100), axis=True, axis_position="bottom")
                .legend(),
            ],
            settings=settings(border=False, row_lines=False, row_shading=True, search=False, page_size=0, width=1000),
            title="Equal and nearly equal points",
            caption="Illustrative values. Translucent colours are shown separately below.",
        )
    )
    transparent_table = mo.ui.anywidget(
        EvidentialTable(
            [{"case": "Translucent", "before": 50.3, "after": 50.6, "target": 50.9}],
            columns=[col.text("case"), col.points({"before": "Before", "after": "After", "target": "Target"},
                palette=["#2563eb80", "#dc262680", "#16a34a80"], size=18)
                .title("Translucent points").scale(domain=(0, 100), axis=True, axis_position="bottom").legend()],
            settings=settings(border=False, row_lines=False, page_size=0, width=600),
        )
    )
    mo.vstack([overlap_table, transparent_table])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
