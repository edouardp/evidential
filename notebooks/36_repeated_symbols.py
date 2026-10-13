# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Repeated symbols — ``col.symbols`` / ``col.repeat`` / ``col.rating``.

A numeric value drawn as that many repeated glyphs, emoji or images: The
Economist's repeated squares, a medal table, star ratings.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, mo, settings


@app.cell
def _(mo):
    mo.md("""
    # Repeated symbols

    `col.symbols(name, ...)` turns a numeric value into that many repeated
    **glyphs, emoji or images**. The usual `align` applies, so a column of these
    can sit left, right or centered.

    ```python
    col.symbols("twice", symbol="■", color="#2EC1D3")        # 13 -> ■×13
    col.symbols("rating", symbol="★", empty="☆", max=5)      # 3 -> ★★★☆☆
    col.rating("stars", max=5)                                # the same, with defaults
    col.repeat("thrice", symbol="■")                          # alias for col.symbols
    ```

    | option | meaning |
    | --- | --- |
    | `symbol` | the filled glyph (default `"●"`) — `"■"`, `"★"`, `"▲"`, any emoji |
    | `empty` | the glyph for the unfilled slots (used with `max`) |
    | `max` | draw this many slots; `value` filled, the rest `empty` |
    | `image` | an image URL to repeat instead of a glyph |
    | `color` / `empty_color` | the filled / unfilled colour |
    | `size` / `gap` | glyph size and spacing, in `em` |
    | `align` | `"left"`, `"right"` or `"center"` |
    """)
    return


@app.cell
def _():
    repeats = [
        {"country": "Spain", "twice": 13, "thrice": 2, "avg": 0.441},
        {"country": "France", "twice": 8, "thrice": 0, "avg": 0.476},
        {"country": "Britain", "twice": 5, "thrice": 0, "avg": 0.584},
        {"country": "United States", "twice": 5, "thrice": 0, "avg": 0.598},
        {"country": "Australia", "twice": 5, "thrice": 0, "avg": 0.635},
        {"country": "Belgium", "twice": 3, "thrice": 0, "avg": 0.644},
        {"country": "Switzerland", "twice": 4, "thrice": 0, "avg": 0.646},
        {"country": "Canada", "twice": 4, "thrice": 0, "avg": 0.654},
        {"country": "Netherlands", "twice": 6, "thrice": 0, "avg": 0.657},
        {"country": "South Africa", "twice": 6, "thrice": 0, "avg": 0.684},
        {"country": "Austria", "twice": 9, "thrice": 1, "avg": 0.713},
        {"country": "Italy", "twice": 7, "thrice": 0, "avg": 0.714},
        {"country": "Czech Republic", "twice": 2, "thrice": 0, "avg": 0.757},
        {"country": "Portugal", "twice": 4, "thrice": 0, "avg": 0.760},
        {"country": "China", "twice": 7, "thrice": 1, "avg": 0.766},
    ]
    return (repeats,)


@app.cell
def _(EvidentialTable, col, mo, repeats, settings):
    # A number beside its repeated squares, under a shared header.
    counts = mo.ui.anywidget(
        EvidentialTable(
            repeats,
            settings=settings(
                title="Stuck on repeat",
                subtitle="Quarterly GDP growth rates, same rate in consecutive quarters",
                caption="Illustrative data, in the style of The Economist.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                width="820px",
            ),
            columns=[
                col.text("country"),
                col.group(
                    "Same rate in consecutive quarters",
                    [
                        col.subcolumns(
                            "Twice",
                            [
                                col.integer("twice"),
                                col.symbols("twice", symbol="■", color="#2EC1D3", align="left"),
                            ],
                        ),
                        col.symbols("thrice", symbol="■", color="#2EC1D3", align="center"),
                        
                    ],
                ),
                col.number("avg", fmt="num3", title="Average difference")
                .bar(color="#8ECAE6", fit_to_data=False)
                .align("left"),
            ],
        )
    )
    counts
    return


@app.cell
def _(mo):
    mo.md("""
    ## A medal table

    One row per country; a `col.symbols` column per medal, each a different
    colour and glyph. `align="left"` keeps the squares against the left edge.
    """)
    return


@app.cell
def _():
    medals = [
        {"country": "Ireland", "gold": 4, "silver": 1, "bronze": 0},
        {"country": "Malta", "gold": 3, "silver": 0, "bronze": 1},
        {"country": "Cyprus", "gold": 3, "silver": 2, "bronze": 0},
        {"country": "Denmark", "gold": 3, "silver": 1, "bronze": 1},
        {"country": "France", "gold": 2, "silver": 3, "bronze": 0},
        {"country": "Sweden", "gold": 2, "silver": 1, "bronze": 2},
        {"country": "Romania", "gold": 1, "silver": 3, "bronze": 1},
        {"country": "Germany", "gold": 1, "silver": 1, "bronze": 3},
        {"country": "Slovenia", "gold": 1, "silver": 1, "bronze": 3},
        {"country": "Hungary", "gold": 0, "silver": 1, "bronze": 4},
    ]
    return (medals,)


@app.cell
def _(EvidentialTable, col, medals, mo, settings):
    medal_table = mo.ui.anywidget(
        EvidentialTable(
            medals,
            settings=settings(
                title="Final medals table",
                subtitle="Awarded across five areas",
                caption="Illustrative data, in the style of The Economist.",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                width="620px",
            ),
            columns=[
                col.text("country"),
                col.symbols("gold", symbol="■", color="#f0a500", size=1.5),
                col.symbols("silver", symbol="■", color="#9e9e9e", size=1.5),
                col.symbols("bronze", symbol="■", color="#f4a582", size=1.5),
            ],
        )
    )
    medal_table
    return


@app.cell
def _(mo):
    mo.md("""
    ## Ratings

    `max=` turns the column into `max` slots: the value is filled, the rest use
    the `empty` glyph — a star rating. Without `max`, exactly `value` glyphs are
    drawn. `col.rating("stars", max=5)` is the shorthand (`★` / `☆`, amber).
    """)
    return


@app.cell
def _():
    ratings = [
        {"place": "Café A", "stars": 5, "score": 9},
        {"place": "Café B", "stars": 4, "score": 8},
        {"place": "Café C", "stars": 3, "score": 6},
        {"place": "Café D", "stars": 2, "score": 4},
        {"place": "Café E", "stars": 1, "score": 2},
    ]
    return (ratings,)


@app.cell
def _(EvidentialTable, col, mo, ratings, settings):
    # A data-URI SVG, so the image repeat needs no network.
    dot = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12'>"
        "<circle cx='6' cy='6' r='5' fill='%230ea5e9'/></svg>"
    )
    rating_table = mo.ui.anywidget(
        EvidentialTable(
            ratings,
            settings=settings(
                title="Ratings",
                row_shading=True,
                row_lines=False,
                border=False,
                stretch=False,
                width="720px",
            ),
            columns=[
                col.text("place"),
                col.rating("stars", max=5, title="Of 5"),
                col.rating("score", max=10, title="Of 10", color="#eab308"),
                col.symbols("score", symbol="⭐", title="Emoji"),
                col.number("score").title("Image").symbols(image=dot, gap=0.1),
            ],
        )
    )
    rating_table
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - It is a **visualisation** (`viz="symbols"`), not a format: the value is
      still a number, so sorting, search, statistics and export are unchanged.
    - `max` is a **floor** on the slots, not a cap — a value above `max` simply
      draws more (a 7 with `max=5` draws seven filled stars).
    - A non-numeric or missing value shows the column's null text.
    - `image` repeats an `<img>` instead of a glyph (a URL or a data-URI), sized
      to `1em`; `symbol` accepts any character, including emoji.
    - Pair a number with its squares by giving both the same column under a
      `col.subcolumns(...)` group, as the "Twice" / "Thrice" columns above do.
    """)
    return


if __name__ == "__main__":
    app.run()
