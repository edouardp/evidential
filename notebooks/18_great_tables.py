# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Great Tables-inspired ideas: column merging, substitutions, special formatters.

The merge sources are ordinary columns; you can build them in SQL (including
hidden helper columns) and only render the derived column.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    from evidential import (
        EvidentialTable,
        col,
        cols_merge_n_pct,
        cols_merge_range,
        cols_merge_uncert,
        sub_large_vals,
        sub_missing,
        sub_small_vals,
        sub_values,
        sub_zero,
    )

    return (
        EvidentialTable,
        col,
        cols_merge_n_pct,
        cols_merge_range,
        cols_merge_uncert,
        mo,
        sub_large_vals,
        sub_missing,
        sub_small_vals,
        sub_zero,
    )


@app.cell
def _(mo):
    mo.md("""
    # Great Tables-inspired features

    - **Column merging** (`cols_merge_*`): combine source columns into one
      rendered column (`low–high`, `value ± uncert`, `n (pct)`). Sources can be
      hidden helper columns produced in SQL.
    - **Substitutions** (`sub_*`): replace missing / zero / small / large /
      specific values with text at display time.
    - **Special formatters**: `bytes`, `duration`, `roman`, `flag` (an ISO
      3166-1 **alpha-2 or alpha-3** country code), plus cell `markdown`.
      `footnote_marks` and `all_caps` tweak presentation.
    """)
    return


@app.cell
def _():
    measurements = [
        {"site": "Alpha", "low": 10, "high": 20, "value": 5.0, "uncert": 0.2, "n": 120, "pct": 0.31, "size": 1536000, "elapsed": 3725, "year": 2024, "country": "AUS"},
        {"site": "Beta", "low": 8, "high": 12, "value": 9.4, "uncert": 0.5, "n": 80, "pct": 0.12, "size": 512, "elapsed": 95, "year": 1999, "country": "USA"},
        {"site": "Gamma", "low": 30, "high": 45, "value": 41.0, "uncert": 1.1, "n": 210, "pct": 0.57, "size": 1048576, "elapsed": 86400, "year": 2021, "country": "JPN"},
    ]
    return (measurements,)


@app.cell
def _(
    EvidentialTable,
    col,
    cols_merge_n_pct,
    cols_merge_range,
    cols_merge_uncert,
    measurements,
    mo,
):
    merged = mo.ui.anywidget(
        EvidentialTable(
            measurements,
            title="Column merging & special formatters",
            all_caps=True,
            columns=[
                col.text("site"),
                col.merge("range", cols_merge_range("low", "high", fmt="num0")),
                col.merge("measurement", cols_merge_uncert("value", "uncert", fmt="num1", title="Value")),
                col.merge("share", cols_merge_n_pct("n", "pct")),
                col.number("size", fmt="bytes"),
                col.number("elapsed", fmt="duration"),
                col.number("year", fmt="roman"),
                col.flag("country"),
            ],
        )
    )
    merged
    return


@app.cell
def _(mo):
    mo.md("""
    ## Substitutions and cell markdown

    Values are replaced at display time; the underlying data (and any
    visualisation) is untouched. `sub_missing`/`sub_zero`/`sub_small_vals`/
    `sub_large_vals`/`sub_values` run in order.
    """)
    return


@app.cell
def _():
    readings = [
        {"sensor": "S1", "amount": None, "status": "**nominal**"},
        {"sensor": "S2", "amount": 0.0, "status": "idle"},
        {"sensor": "S3", "amount": 0.4, "status": "`low`"},
        {"sensor": "S4", "amount": 42.0, "status": "nominal"},
        {"sensor": "S5", "amount": 2_500_000.0, "status": "*over range*"},
    ]
    return (readings,)


@app.cell
def _(
    EvidentialTable,
    col,
    mo,
    readings,
    sub_large_vals,
    sub_missing,
    sub_small_vals,
    sub_zero,
):
    substituted = mo.ui.anywidget(
        EvidentialTable(
            readings,
            title="Substitutions",
            footnote_marks="letters",
            columns=[
                col.text("sensor"),
                col.number("amount", fmt="num1", title="Reading"),
                col.markdown("status"),
            ],
            rules=[
                sub_missing(columns="amount", missing_text="n/a"),
                sub_zero(columns="amount", zero_text="—"),
                sub_small_vals(columns="amount", threshold=1, small_text="<1"),
                sub_large_vals(columns="amount", threshold=1_000_000, large_text=">1M"),
            ],
        )
    )
    substituted
    return


if __name__ == "__main__":
    app.run()
