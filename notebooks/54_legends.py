# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Wrapping legends for stacks, multiple charts and nine population points."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():

    import json
    from pathlib import Path

    import marimo as mo

    from evidential import EvidentialTable, col, label, settings

    return EvidentialTable, Path, col, json, label, mo, settings


@app.cell
def introduction(mo):
    mo.md("""
    # Legends

    Add `.legend()` to a mark column to put its key above the table, on the
    right of the title and subtitle. The keys use the marks' actual colours.
    Each column has its own row of keys, with grey names and square stack
    swatches. Swatch and label stay together; flexbox wraps whole keys as the
    available space changes. Try narrowing the window. Use
    `.legend(outline=True)` for a thin box around the combined key.

    Names default to source headings. Pass a list or mapping for custom names;
    `.legend(False)` removes a key and a `None` label omits an individual entry.
    Fixed-colour bars, stacks, points, ranges and categorical strips share the
    same API. A per-row colour alone cannot supply category identities.
    """)
    return


@app.cell
def illustrative_data(settings):
    services = [
        {
            "service": "Analytics",
            "storage": 1235,
            "requests": 487,
            "transfer": 211,
            "other": 85,
            "web": 61,
            "mobile": 28,
            "batch": 11,
        },
        {
            "service": "Search",
            "storage": 730,
            "requests": 920,
            "transfer": 330,
            "other": 120,
            "web": 44,
            "mobile": 49,
            "batch": 7,
        },
        {
            "service": "Media",
            "storage": 1560,
            "requests": 390,
            "transfer": 1420,
            "other": 110,
            "web": 32,
            "mobile": 58,
            "batch": 10,
        },
        {
            "service": "Archive",
            "storage": 910,
            "requests": 45,
            "transfer": 75,
            "other": 40,
            "web": 9,
            "mobile": 6,
            "batch": 85,
        },
    ]
    cost_colors = ["#1d4ed8", "#f59e0b", "#dc2626", "#94a3b8"]
    frame = settings(border=False, row_lines=False, row_shading=True, page_size=0, width="100%")
    return cost_colors, frame, services


@app.cell
def one_legend_doc(mo):
    mo.md("""
    ## One stacked-bar column

    One legend group, with names inferred from `storage`, `requests`, `transfer`
    and `other`. The column heading is **Monthly cost**; the segment names remain
    independent of that combined heading and of the percentage labels.
    These service figures are illustrative.
    """)
    return


@app.cell
def one_legend(EvidentialTable, col, cost_colors, frame, label, mo, services):
    single = mo.ui.anywidget(
        EvidentialTable(
            services,
            columns=[
                col.text("service"),
                col.stacked_bar(
                    "storage",
                    "requests",
                    "transfer",
                    "other",
                    colors=cost_colors,
                    normalize="percent",
                    format="usd0",
                    labels=label.share().fmt("pct0"),
                    title="Monthly cost",
                ).legend(),
            ],
            settings=frame,
            title="Where the cloud budget goes",
            subtitle="Illustrative service costs · share of monthly spend",
        )
    )
    single
    return


@app.cell
def two_legends_doc(mo):
    mo.md("""
    ## Two stacked-bar columns

    Each column opts in separately, with a row named after each rendered
    column. The cost key overrides `transfer`; the traffic key supplies all
    three display names in source order. The cost column requests
    `outline=True`, which puts one thin box around both rows.
    """)
    return


@app.cell
def two_legends(EvidentialTable, col, cost_colors, frame, label, mo, services):
    double = mo.ui.anywidget(
        EvidentialTable(
            services,
            columns=[
                col.text("service"),
                col.stacked_bar(
                    "storage",
                    "requests",
                    "transfer",
                    "other",
                    colors=cost_colors,
                    normalize="percent",
                    format="usd0",
                    labels=label.share().fmt("pct0"),
                    title="Monthly cost",
                ).legend({"transfer": "Data transfer"}, outline=True),
                col.stacked_bar(
                    "web",
                    "mobile",
                    "batch",
                    colors=["#0f766e", "#7c3aed", "#db2777"],
                    normalize="percent",
                    labels="percent",
                    title="Traffic mix",
                ).legend(["Web", "Mobile", "Batch jobs"]),
            ],
            settings=frame,
            title="Cost and traffic tell different stories",
            subtitle="Illustrative services · each stack totals 100%",
        )
    )
    double
    return


@app.cell
def population_doc(mo):
    mo.md("""
    ## Nine points on a line: population age structure

    Each dot shows the share of a country's total population in one age band,
    from **0–9** through **80+**. The grey line connects the smallest and largest
    shares; it is a visual span, not a time series or uncertainty interval.
    `col.points(age_labels, connect=True)` calculates that span as a display
    concern, so it needs no extra minimum/maximum fields or connector key.
    `palette="viridis"` samples nine colours in age-band order; omit it for
    an automatic categorical palette. A colour list overrides the range.
    Coincident points can overlap.

    These are genuine **2024 World Bank WDI / UN World Population Prospects**
    estimates for twelve countries spanning income groups. The committed
    snapshot keeps this example usable offline. The
    [source indicators](https://data.worldbank.org/indicator/SP.POP.0004.MA.5Y)
    give five-year bands separately for men and women, each as a percentage of
    that sex's population. The query weights those percentages by the male and
    female populations before combining them into ten-year bands. It does not
    average percentages. The final band includes everyone aged 80 and above.

    See `sql/54_population_ages.sql` and `data/README.md` for the query,
    attribution and snapshot provenance. Income groups are those recorded in
    the local October 2026 WDI bundle; they are not historical 2024 classifications.
    """)
    return


@app.cell
def population_data(Path, json):
    population = json.loads((Path(__file__).parent / "data/54_population_age_bands_2024.json").read_text())
    age_labels = {
        "age_0_9": "0–9",
        "age_10_19": "10–19",
        "age_20_29": "20–29",
        "age_30_39": "30–39",
        "age_40_49": "40–49",
        "age_50_59": "50–59",
        "age_60_69": "60–69",
        "age_70_79": "70–79",
        "age_80_plus": "80+",
    }
    return age_labels, population


@app.cell
def population_points(EvidentialTable, age_labels, col, frame, mo, population):
    age_structure = mo.ui.anywidget(
        EvidentialTable(
            population,
            columns=[
                col.text("country"), 
                col.text("income_group"), 
                col.number("population", format="compact3"), 
                col.points(age_labels, palette="viridis", connect=True, title="Population share", format="pct0")
                   .scale(domain=(0, 0.35), axis=True, axis_position="bottom", gridlines=True)
                   .legend()
            ],
            settings=frame,
            title="From younger to older populations",
            subtitle="2024 · share of total population in each age band",
            caption="Source: World Bank WDI / United Nations Population Division. CC BY 4.0. "
            "Countries ordered by their population share aged 0–9.",
        )
    )
    age_structure
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
