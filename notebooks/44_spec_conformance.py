# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Visual acceptance examples for the declarative table API and design system."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import EvidentialTable, col, rows, settings

    return EvidentialTable, col, mo, rows, settings


@app.cell
def _(mo):
    mo.md("""
    # Design conformance

    These examples exercise shared coordinates, missing observations, labels,
    structured series and synthetic rows. Hover over a mark to inspect its
    original values, including labels hidden because their segment is too small.
    Labels inside fills choose white or dark text automatically; an explicit
    `.label(color=...)` overrides that choice.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo, settings):
    sales = [
        {"country": "Finland", "before": 29, "after": 94},
        {"country": "Sweden", "before": 76, "after": 41},
        {"country": "Norway", "before": 27, "after": 47},
        {"country": "Denmark", "before": 15, "after": 19},
        {"country": "Iceland", "before": 10, "after": 20},
    ]
    sales_marks = (
        col.range("before", "after", color="#222222", size=2)
        .point("before", color="#6699ee", size=12)
        .point("after", color="#ef4444", size=12)
        .title("Weekly Sales")
        .scale(domain=(0, 100), axis=True)
    )
    report_style = settings(border=False, row_lines=False, row_shading=True, search=False, page_size=0, width=440)
    scale_gallery = [
        mo.ui.anywidget(
            EvidentialTable(
                sales,
                settings=report_style,
                title="Axis below",
                columns=[
                    col.text("country"),
                    sales_marks.scale(axis_position="bottom"),
                ],
            )
        ),
        mo.ui.anywidget(
            EvidentialTable(
                sales,
                settings=report_style,
                title="Axis above",
                columns=[
                    col.text("country"),
                    sales_marks,
                ],
            )
        ),
        mo.ui.anywidget(
            EvidentialTable(
                sales,
                settings=report_style,
                title="Gridlines",
                columns=[
                    col.text("country"),
                    sales_marks.scale(gridlines=True),
                ],
            )
        ),
        mo.ui.anywidget(
            EvidentialTable(
                sales,
                settings=report_style,
                title="Reference at 50",
                columns=[
                    col.text("country"),
                    sales_marks.reference_line(50, color="#ef4444"),
                ],
            )
        ),
    ]
    mo.vstack([mo.hstack(scale_gallery[:2], justify="start"), mo.hstack(scale_gallery[2:], justify="start")])
    return


@app.cell
def _(EvidentialTable, col, mo):
    missing_marks = mo.ui.anywidget(
        EvidentialTable(
            [
                {"case": "Complete", "value": 15, "lo": 12, "hi": 19, "target": 18},
                {"case": "Missing value and interval", "value": None, "lo": None, "hi": 19, "target": 18},
            ],
            title="Fixed domain and independent missingness",
            border=False,
            row_lines=False,
            row_shading=True,
            search=False,
            page_size=0,
            width=800,
            columns=[
                col.text("case"),
                col.bar("value", size=0.45)
                .range("lo", "hi", fill=True)
                .point("target")
                .scale(domain=(10, 20), axis=True, gridlines=True),
            ],
        )
    )
    mo.vstack([missing_marks])
    return


@app.cell
def _(EvidentialTable, col, mo):
    shared_stacks = mo.ui.anywidget(
        EvidentialTable(
            [
                {"case": "Balanced", "against": 10, "neutral": 0, "for": 10},
                {"case": "More support", "against": 10, "neutral": 0, "for": 30},
            ],
            title="The same magnitude has the same width in every row",
            border=False,
            search=False,
            page_size=0,
            width=800,
            columns=[
                col.text("case"),
                col.stacked_bar(
                    "against",
                    "neutral",
                    "for",
                    colors=["#ef4444", "#e5e7eb", "#2563eb"],
                    diverge_at="neutral",
                    labels=True,
                ).scale(axis=True, gridlines=True),
            ],
        )
    )
    mo.vstack([shared_stacks])
    return


@app.cell
def _(EvidentialTable, col, mo):
    irregular = mo.ui.anywidget(
        EvidentialTable(
            [
                {
                    "case": "Irregular x with a gap",
                    "series": [
                        {"x": 0, "y": 2},
                        {"x": 1, "y": 4},
                        {"x": 2, "y": None},
                        {"x": 8, "y": 3},
                        {"x": 10, "y": 6},
                    ],
                }
            ],
            title="Structured sparkline",
            search=False,
            page_size=0,
            border=False,
            columns=[col.text("case"), col.sparkline("series", x="x", y="y", markers=True, width=240)],
        )
    )
    mo.vstack([irregular])
    return


@app.cell
def _(EvidentialTable, col, mo, rows):
    detail = [
        {"region": "North", "country": "Canada", "arr": 210},
        {"region": "North", "country": "Mexico", "arr": 135},
        {"region": "South", "country": "Brazil", "arr": 100},
    ]
    sections = mo.ui.anywidget(
        EvidentialTable(
            detail,
            row_layout=rows.group_by("region").section(values={"arr": "sum"}).summary("Subtotal").grand_summary(),
            title="Combined section totals with pagination",
            page_size=1,
            section_indent=1,
            stub="country",
            border=False,
            row_lines=False,
            row_shading=True,
            width=800,
            columns=[col.text("country"), col.integer("arr")],
            caption="Next page repeats the section label. Named summaries recalculate over matching detail records when you search.",
        )
    )
    mo.vstack([sections])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Point outlines

    Use `outline=False` for a plain filled point, or `outline="#334155"` for a
    colored ring independent of the fill. Omit it (or use `True`) for the
    default outline. The same options work with arrays drawn by `col.points`.
    """)
    return


@app.cell
def _(EvidentialTable, col, mo):
    point_outlines = mo.ui.anywidget(
        EvidentialTable(
            [{"case": "Sample", "value": 45, "samples": [25, 45, 70]}],
            title="Default, hidden, and custom point outlines",
            columns=[
                col.text("case"),
                col.point("value", title="Default", color="#93c5fd", size=12),
                col.point("value", title="No outline", color="#93c5fd", size=12, outline=False),
                col.point("value", title="Dark outline", color="#93c5fd", size=12, outline="#334155"),
                col.points("samples", title="Array, no outline", color="#93c5fd", size=10, outline=False),
                col.points("samples", title="Array, dark outline", color="#93c5fd", size=10, outline="#334155"),
            ],
            search=False,
            page_size=0,
            border=False,
            width=1000,
        )
    )
    point_outlines
    return


if __name__ == "__main__":
    app.run()
