# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Shared geometric markers for points, legends, repeated symbols and ratings."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, mo, settings


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # Distinguishable marker shapes

    Points default to circles. Choose `circle`, `square`, `rounded`, `triangle`,
    `diamond`, `cross`, `star` or `bar`. The triangle is equilateral and points up;
    the diamond is narrower than a square rotated by 45°. Rotation is separate:
    `shape="cross", angle=45` makes an X; `shape="triangle", angle=270` points left.
    The bar is vertical by default; `shape="bar", angle=90` makes it horizontal.
    Positive angles turn clockwise. Size is the nominal unrotated bounding box, in pixels
    for points and em for repeated symbols; a rotated mark can extend beyond it.

    Every shape accepts `outline=True` (the theme outline), `False`, or a colour.
    Legends use the same shape, angle and outline as the mark. Array points and
    named point series use the same options. Repeated geometric symbols and star
    ratings use these paths too, rather than depending on font glyphs.

    The data here is illustrative. The small-marker table helps judge which
    shapes work at normal table sizes; stars usually benefit from a little room.
    """)
    return


@app.cell
def sampler(EvidentialTable, col, mo, settings):
    marker_shapes = ["circle", "square", "rounded", "triangle", "diamond", "cross", "star", "bar"]
    def shape_column(size):
        markers = col.point("circle", size=size, color="#2563eb", outline="#172554")
        for shape in marker_shapes[1:]:
            markers = markers.point(shape, shape=shape, size=size, color="#2563eb", outline="#172554")
        return markers.title("Markers").scale(domain=(0, 9)).legend(column_names=False)

    samples = {shape: index + 1 for index, shape in enumerate(marker_shapes)}
    small_shapes = mo.ui.anywidget(EvidentialTable(
        [{"sample": "7 px", **samples}],
        columns=[col.text("sample"), shape_column(7)],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=960),
        title="Small markers",
    ))
    large_shapes = mo.ui.anywidget(EvidentialTable(
        [{"sample": "12 px", **samples}],
        columns=[col.text("sample"), shape_column(12)],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=960),
        title="Larger markers",
    ))
    mo.vstack([small_shapes, large_shapes])
    return


@app.cell
def rotated_markers(EvidentialTable, col, mo, settings):
    rotation_table = mo.ui.anywidget(EvidentialTable(
        [{"up": 1, "right": 2, "down": 3, "left": 4, "plus": 5, "x": 6, "horizontal": 7, "vertical": 8}],
        columns=[
            col.point("up", shape="triangle", size=11)
            .point("right", shape="triangle", angle=90, size=11)
            .point("down", shape="triangle", angle=180, size=11)
            .point("left", shape="triangle", angle=270, size=11)
            .point("plus", shape="cross", size=11)
            .point("x", shape="cross", angle=45, size=11)
            .point("horizontal", shape="bar", angle=90, size=11)
            .point("vertical", shape="bar", size=11)
            .title("Markers").scale(domain=(0, 9)).legend(column_names=False),
        ],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=960),
        title="Rotation without multiplying shape names",
    ))
    rotation_table
    return


@app.cell
def point_series(EvidentialTable, col, mo, settings):
    shape_series = mo.ui.anywidget(EvidentialTable(
        [{"metric": "Latency", "samples": [12, 18, 24, 38, 56], "before": 20, "after": 70, "named_before": 20, "named_after": 70},
         {"metric": "Render time", "samples": [10, 25, 36, 42, 48], "before": 35, "after": 55, "named_before": 35, "named_after": 55}],
        columns=[
            col.text("metric"),
            col.points("samples", shape="diamond", size=9, outline="#1e3a8a").scale(domain=(0, 100)),
            col.point("before", shape="square", size=10, color="#2563eb", outline="black")
            .point("after", shape="triangle", angle=270, size=10, color="#dc2626", outline=False)
            .title("Two observations").scale(domain=(0, 100)).legend(),
            col.points({"named_before": "Before", "named_after": "After"}, shape="star", connect=True, size=11, outline=True)
            .title("Named series").scale(domain=(0, 100)).legend(),
        ],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=960),
        title="Arrays, overlays and matching legend keys",
    ))
    shape_series
    return


@app.cell(hide_code=True)
def symbols_description(mo):
    mo.md("""
    ## Repeated shapes, symbols and ratings

    Use `col.number("count").symbols(...)`, or the equivalent `col.symbols(...)`
    / `col.shapes(...)` factory. `col.number(...)` alone does not select a symbol
    graphic. Familiar geometric glyphs (`■`, `●`, `▲`, `◆`, `★`, `☆`, `+`, `×`)
    resolve to the same font-independent shapes. Other text and emoji remain text.
    Empty `☆` slots in a rating are hollow stars. With `shape="square"`, those
    same rating slots become hollow squares. `outline=False` suppresses strokes,
    including hollow slots. Repeated shape `size` is applied once, in em.
    """)
    return


@app.cell
def repeated_shapes(EvidentialTable, col, mo, settings):
    repeated_table = mo.ui.anywidget(EvidentialTable(
        [{"team": "A", "medals": 3, "twice": 2, "rating": 4, "custom": 2},
         {"team": "B", "medals": 2, "twice": 2, "rating": 2, "custom": 1}],
        columns=[
            col.text("team"),
            col.number("medals").symbols(shape="square", color="#f0a500", size=0.8, outline="#92400e"),
            col.symbols("twice", symbol="■", color="#2EC1D3", size=0.8, outline="#155e75"),
            col.rating("rating", shape="star", size=1),
            col.symbols("custom", symbol="🐟", max=3, empty="·"),
        ],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=780),
        title="Shared geometry, custom symbols still welcome",
    ))
    repeated_table
    return


@app.cell
def overlapping_shapes(EvidentialTable, col, mo, settings):
    overlap_shapes = ["circle", "square", "triangle", "star", "bar"]
    overlap_table = mo.ui.anywidget(EvidentialTable(
        [{"case": name, **{f"{shape}_{endpoint}": value
           for shape in overlap_shapes for endpoint, value in (("before", a), ("after", b))}}
         for name, a, b in [("Exact overlap", 50, 50), ("Within a pixel", 50, 50.4), ("Separated", 30, 70)]],
        columns=[col.text("case"), *[
            col.point(f"{shape}_before", shape=shape, size=12, color="#2563eb", outline="black")
            .point(f"{shape}_after", shape=shape, size=12, color="#dc2626", outline="black")
            .title(shape.title()).scale(domain=(0, 100)) for shape in overlap_shapes
        ]],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=1100),
        title="Overlapping colours retain their marker shape",
        caption="Matching shapes, angles and sizes combine within one pixel. Bar colours stack top-to-bottom.",
    ))
    overlap_table
    return


@app.cell
def sparkline_markers(EvidentialTable, col, mo, settings):
    sparkline_table = mo.ui.anywidget(EvidentialTable(
        [{"series": [2, 5, 3, None, 4, 7, 5]}],
        columns=[
            col.sparkline("series", type="points", shape="star", outline="#1e3a8a", title="Star observations"),
            col.sparkline("series", type="line", markers=True, shape="triangle", angle=90, title="Triangle markers"),
            col.sparkline("series", type="area", markers="ends", shape="cross", angle=45, title="X endpoints"),
        ],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=780),
        title="Sparkline points and optional line/area markers",
        caption="Hover inspection also includes observations without a visible marker.",
    ))
    sparkline_table
    return


@app.cell(hide_code=True)
def bar_overlap_description(mo):
    mo.md("""
    ## Overlapping bars stack their colours

    Two colours occupy the top and bottom halves; three or more occupy equal
    bands along the bar. The first declared point starts at the top. Rotating
    the bar rotates those bands too. Outlines and all tooltip values survive.
    Other shapes keep their pie sectors, and the whole cluster still has to fit
    within one screen pixel.
    """)
    return


@app.cell
def overlapping_bars(EvidentialTable, col, mo, settings):
    def bar_column(count, angle, title):
        fields = ["a", "b", "c", "d"][:count]
        colors = ["#2563eb", "#dc2626", "#16a34a", "#eab308"][:count]
        column = col.point(fields[0], shape="bar", angle=angle, size=18, color=colors[0], outline="#172554")
        for field, color in zip(fields[1:], colors[1:], strict=True):
            column = column.point(field, shape="bar", angle=angle, size=18, color=color, outline="#172554")
        return column.title(title).scale(domain=(0, 100))

    bar_overlap_table = mo.ui.anywidget(EvidentialTable(
        [{"case": "Exact overlap", "a": 50, "b": 50, "c": 50, "d": 50},
         {"case": "Within a pixel", "a": 50, "b": 50.1, "c": 50.2, "d": 50.3},
         {"case": "Separated", "a": 20, "b": 40, "c": 60, "d": 80}],
        columns=[
            col.text("case"),
            bar_column(2, 0, "Two colours"),
            bar_column(3, 0, "Three colours"),
            bar_column(4, 0, "Four colours"),
            bar_column(3, 90, "Horizontal"),
            bar_column(3, 45, "Rotated 45°"),
        ],
        settings=settings(border=False, row_lines=False, search=False, page_size=0, width=1100),
        title="Bar colours split along the marker",
    ))
    bar_overlap_table
    return


if __name__ == "__main__":
    app.run()
