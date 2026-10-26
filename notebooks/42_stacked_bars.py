# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Stacked bars and percentage support.

A `col.stacked_bar(...)` is a distinct encoding: segment coordinates are
cumulative. `normalize="percent"` divides each row by its own total, `size=`
sets the stack's height, `labels="percent"` writes each segment's share, and
`diverge_at=` centres a neutral segment for a Likert chart.
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
def _():
    counts = [
        {"region": "Americas", "new": 42, "renewal": 61, "expansion": 18},
        {"region": "EMEA", "new": 30, "renewal": 74, "expansion": 22},
        {"region": "APAC", "new": 26, "renewal": 48, "expansion": 31},
        {"region": "LATAM", "new": 12, "renewal": 21, "expansion": 9},
    ]
    return (counts,)


@app.cell
def _(mo):
    mo.md("""
    # Stacked bars

    Each `source` is a **segment magnitude**; `colors` is positional. Stacking
    uses the raw additive values and does **not** normalise automatically — the
    scale is the row's cumulative total.
    """)
    return


@app.cell
def _(EvidentialTable, col, counts, mo, settings):
    absolute = mo.ui.anywidget(
        EvidentialTable(
            counts,
            settings=settings(
                title="Revenue by type",
                subtitle="Absolute values — the bar is scaled to the largest total",
                row_lines=False,
                border=False,
                stretch=False,
            ),
            columns=[
                col.text("region"),
                col.stacked_bar(
                    "new",
                    "renewal",
                    "expansion",
                    colors=["#2563eb", "#60a5fa", "#bfdbfe"],
                    labels=True,
                    size=0.6,
                    title="New · Renewal · Expansion",
                ),
            ],
        )
    )
    absolute
    return


@app.cell
def _(mo):
    mo.md("""
    ## Percent stacks

    `normalize="percent"` divides each row by its own total, so every bar spans
    0–100%. `labels="percent"` writes each segment's share; with
    `.scale(domain=(0, 100), axis=True, gridlines=True)` the axis reads the same
    0–100% scale.
    """)
    return


@app.cell
def _(EvidentialTable, col, counts, mo):
    percent = mo.ui.anywidget(
        EvidentialTable(
            counts,
            title="Mix by region",
            subtitle="Each row sums to 100%",
            row_lines=False,
            border=False,
            stretch=True, #width=600,
            columns=[
                col.text("region"),
                col.stacked_bar(
                        "new",
                        "renewal",
                        "expansion",
                        colors=["#2563eb", "#60a5fa", "#bfdbfe"],
                        labels="percent",
                        label_align="begin",
                        size=1,
                        normalize="percent",
                        title="Share")
                    .scale(domain=(0, 100), axis=True, gridlines=True),
            ],
        )
    )
    percent
    return


@app.cell
def _(mo):
    mo.md("""
    ## A diverging (Likert) stack

    `diverge_at="neutral", neutral="split"` splits the named segment around a
    central origin; the categories before it grow left and those after grow
    right. With `normalize="percent"` each row is still a share of its own
    total, and the two arms are scaled to the larger one.
    """)
    return


@app.cell
def _():
    questions = [
        {
            "question": "Ease of use",
            "strongly_disagree": 4,
            "disagree": 9,
            "neutral": 12,
            "agree": 41,
            "strongly_agree": 34,
        },
        {
            "question": "Value for money",
            "strongly_disagree": 11,
            "disagree": 18,
            "neutral": 20,
            "agree": 36,
            "strongly_agree": 15,
        },
        {
            "question": "Support",
            "strongly_disagree": 3,
            "disagree": 6,
            "neutral": 10,
            "agree": 44,
            "strongly_agree": 37,
        },
        {
            "question": "Reliability",
            "strongly_disagree": 7,
            "disagree": 12,
            "neutral": 14,
            "agree": 39,
            "strongly_agree": 28,
        },
    ]
    return (questions,)


@app.cell
def _(EvidentialTable, col, mo, questions):
    likert = mo.ui.anywidget(
        EvidentialTable(
            questions,
            title="How do you feel about…?",
            subtitle="A neutral-centred five-part stack",
            row_lines=False,
            border=False,
            stretch=True, width=600,
            columns=[
                col.text("question"),
                col.stacked_bar(
                    "strongly_disagree",
                    "disagree",
                    "neutral",
                    "agree",
                    "strongly_agree",
                    colors=["#b91c1c", "#fca5a5", "#e5e7eb", "#86efac", "#16a34a"],
                    labels="percent",
                    label_align="begin",
                    diverge_at="neutral",
                    neutral="split",
                    normalize="percent",
                    size=1,
                    title="Response",
                ),
            ],
        )
    )
    likert
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - This is a **distinct encoding**: a bar is one magnitude from an origin, a
      stack's segments are cumulative coordinates.
    - `normalize` is explicit. Values that already sum to 100 can use
      `normalize=None` and `.scale(domain=(0, 100))` if that is clearer.
    - `labels=True` writes the raw value; `labels="percent"` writes the segment's
      share (`label_align="begin"` left-aligns it inside the segment).
    - `size=` sets the stack's height fraction, so a stack can sit above or
      below other marks in the same cell.
    - `colors` is positional and accepts callables or a per-row column too.
    """)
    return


if __name__ == "__main__":
    app.run()
