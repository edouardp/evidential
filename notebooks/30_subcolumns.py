# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "evidential",
# ]
# ///
"""Shared-header sub-columns: aligned values, text and chips, with offline data."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo

    from evidential import EvidentialTable, col

    return EvidentialTable, col, mo


@app.cell
def introduction(mo):
    mo.md("""
    # Sub-columns

    Two or more physical columns can read as one displayed column. Give each
    member the same **`subcolumn_group`**: the table renders one shared header
    and a small gap between the members. Each retains its own formatting,
    alignment, colours and cell type.

    These examples use **illustrative offline data**, inspired by the layout
    of The Economist's economic data tables; these are not current statistics.
    """)
    return


@app.cell
def sample_data():
    records = [
        {"country": "United States", "gdp": 2.9, "quarter": "Q3", "forecast": 2.4, "inflation": 3.1, "month": "Nov", "unemployment": 3.7, "status": "Steady", "status_color": "#c4dfed"},
        {"country": "China", "gdp": 4.9, "quarter": "Q3", "forecast": 5.5, "inflation": -0.5, "month": "Nov", "unemployment": 5.0, "status": "Expanding", "status_color": "#c7e8d2"},
        {"country": "Japan", "gdp": 1.5, "quarter": "Q3", "forecast": 1.8, "inflation": 2.9, "month": "Nov", "unemployment": 2.5, "status": "Steady", "status_color": "#c4dfed"},
        {"country": "Britain", "gdp": 0.3, "quarter": "Q3", "forecast": 0.4, "inflation": 3.9, "month": "Nov", "unemployment": 4.3, "status": "Slowing", "status_color": "#ffe0c2"},
        {"country": "Germany", "gdp": -0.4, "quarter": "Q3", "forecast": -0.2, "inflation": 2.3, "month": "Nov", "unemployment": 3.1, "status": "Contracting", "status_color": "#ffc4b3"},
        {"country": "India", "gdp": 7.6, "quarter": "Q3", "forecast": 6.7, "inflation": 5.6, "month": "Nov", "unemployment": 8.1, "status": "Expanding", "status_color": "#c7e8d2"},
        {"country": "Turkey", "gdp": 5.9, "quarter": "Q3", "forecast": 4.3, "inflation": 64.8, "month": "Dec", "unemployment": 9.2, "status": "Expanding", "status_color": "#c7e8d2"},
        {"country": "Australia", "gdp": 2.1, "quarter": "Q3", "forecast": 1.9, "inflation": 5.4, "month": "Q3", "unemployment": 3.9, "status": "Steady", "status_color": "#c4dfed"},
    ]
    return (records,)


@app.cell
def economic_table(EvidentialTable, col, mo, records):
    economy = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="Economic data",
            subtitle="Value + reporting period under Latest; independent annual forecast",
            columns=[
                col.text("country", title="Country"),
                col.group("Gross domestic product", [
                        col.subcolumns("Latest", [
                                col.number("gdp", fmt="num1", align="right").neg(),
                                col.auto("quarter").align("left").font_color("#808080"),
                        ]),
                        col.number("forecast", fmt="num1", align="right", title="Annual forecast"),
                    ],
                ),
                col.group("Consumer prices", [
                        col.subcolumns("Latest", [
                                col.number("inflation", fmt="num1", align="right").neg(),
                                col.auto("month").align("left").font_color("#808080"),
                ])]),
                col.number("unemployment", fmt="num1", align="right", title="Unemployment (%)"),
            ],
            page_size="all",
            row_shading=True,
            row_lines=False,
            border=False,
            stretch=False,
            caption="Illustrative data. GDP and consumer prices: percentage change on a year earlier.",
        )
    )
    economy
    return


@app.cell
def three_part_explanation(mo):
    mo.md("""
    ## Three sub-columns: value, text, chip

    Here **Latest observation** contains three members:

    - `gdp`: `fmt="num1"`, **right** aligned, so every decimal point lines up.
    - `quarter`: **left** aligned, gray (`font_color`), immediately beside the value.
    - `status`: `viz="chip"`, **center** aligned, with a colour per row.

    Click or keyboard-activate the shared header to sort by its first visible
    member. `sort_by` on that member can select a different sort key. Search and
    CSV export continue to use each member as a separate data column.
    """)
    return


@app.cell
def three_part_table(EvidentialTable, col, mo, records):
    observations = mo.ui.anywidget(
        EvidentialTable(
            records,
            title="GDP observations",
            columns=[
                col.text("country", title="Country"),
                col.subcolumns("Latest observation", [
                        col.number("gdp", fmt="num1", align="right"),
                        col.auto("quarter").align("left").font_color("#808080"),
                        col.chip("status", align="center", conditional_colors="status_color"),
                    ],
                ),
            ],
            page_size="all",
            row_shading=True,
            row_lines=False,
            border=False,
            stretch=False,
            search=True,
            caption="Illustrative data. Chips demonstrate independently rendered content.",
        )
    )
    observations
    return


@app.cell
def economist_explanation(mo):
    mo.md("""
    ## Economist-style recreation

    A close recreation of the supplied image: the same row order and displayed
    values, compact blue striping, blue latest-value cells (salmon for negative
    values), and shared **latest** headers over value/period pairs. GDP includes
    separate quarterly and annual figures; unemployment also pairs its value
    with a reporting period.

    The figures and source note below are **transcribed from the supplied image**,
    not a current data feed. Suffix symbols follow that image. Scoped CSS in this
    cell supplies the publication-specific typography and header rules; the
    sub-column layout itself is the ordinary table renderer.
    """)
    return


@app.cell
def economist_data():
    economist_source = """United States|2.9|Q3|4.9|2.4|3.1|Nov|4.1|3.7|Nov
    China|4.9|Q3|5.3|5.5|-0.5|Nov|0.7|5.0|Nov‡§
    Japan|1.5|Q3|-2.9|1.8|2.9|Nov|3.3|2.5|Nov
    Britain|0.3|Q3|-0.5|0.4|3.9|Nov|6.8|4.3|Jun††
    Canada|0.5|Q3|-1.1|1.0|3.1|Nov|3.8|5.8|Nov
    Euro area|nil|Q3|-0.5|0.6|2.4|Nov|5.5|6.5|Oct
    Austria|-1.8|Q3|-2.1‡|-0.4|4.9|Nov|7.6|5.1|Oct
    Belgium|1.4|Q3|1.6|1.3|0.5|Dec|2.6|5.6|Oct
    France|0.6|Q3|-0.5|0.9|3.9|Nov|5.7|7.3|Oct
    Germany|-0.4|Q3|-0.5|-0.2|2.3|Nov|6.0|3.1|Oct
    Greece|1.8|Q3|0.1|2.4|2.9|Nov|4.0|9.6|Oct
    Italy|0.1|Q3|0.4|0.7|0.6|Nov|6.1|7.8|Oct
    Netherlands|-0.8|Q3|-1.2|0.2|1.4|Nov|4.4|3.5|Nov
    Spain|1.8|Q3|1.2|2.3|3.3|Nov|3.5|12.0|Oct
    Czech Republic|-1.0|Q3|-2.1|-0.5|7.3|Nov|10.6|3.0|Oct‡
    Denmark|-0.5|Q3|-2.6|1.5|0.6|Nov|3.8|2.8|Oct
    Norway|-1.9|Q3|-2.1|0.4|4.8|Nov|5.4|3.6|Oct‡‡
    Poland|0.5|Q3|6.1|0.5|6.6|Nov|11.3|5.0|Nov§
    Russia|5.5|Q3|na|2.8|7.5|Nov|6.2|2.9|Nov§
    Sweden|-1.4|Q3|-1.2|-0.6|5.8|Nov|6.0|7.1|Nov§
    Switzerland|0.3|Q3|1.1|0.8|1.4|Nov|2.2|2.1|Nov
    Turkey|5.9|Q3|1.1|4.3|64.8|Dec|53.1|9.2|Oct§
    Australia|2.1|Q3|0.9|1.9|5.4|Q3|5.7|3.9|Nov
    Hong Kong|4.1|Q3|0.3|3.4|2.5|Nov|2.2|2.9|Nov‡‡
    India|7.6|Q3|8.6|6.7|5.6|Nov|5.7|8.1|Apr
    Indonesia|4.9|Q3|na|4.9|2.6|Dec|3.7|5.3|Q3§
    Malaysia|3.3|Q3|na|4.0|1.5|Nov|2.6|3.4|Oct§
    Pakistan|nil|2023**|na|nil|29.7|Dec|31.4|6.3|2021
    Philippines|5.9|Q3|13.9|5.4|4.1|Nov|6.0|4.2|Q4§
    Singapore|2.8|Q4|7.0|0.9|3.6|Nov|4.9|2.0|Q3
    South Korea|1.3|Q3|2.5|1.3|3.2|Dec|3.6|2.3|Nov§
    Taiwan|2.3|Q3|7.8|1.2|2.9|Nov|2.5|3.4|Nov
    Thailand|1.5|Q3|3.1|2.5|-0.4|Nov|1.4|0.9|Oct§
    Argentina|-0.8|Q3|11.3|-1.1|161|Nov|135|5.7|Q3§
    Brazil|2.0|Q3|0.6|3.0|4.7|Nov|4.6|7.5|Nov§‡‡
    Chile|0.6|Q3|1.3|nil|4.8|Nov|7.6|8.7|Nov§‡‡
    Colombia|-0.3|Q3|1.0|1.2|10.1|Nov|11.7|9.0|Nov§
    Mexico|3.3|Q3|4.3|3.4|4.3|Nov|5.5|2.8|Nov
    Peru|-1.0|Q3|-1.1|-0.5|3.2|Dec|6.3|7.3|Nov§
    Egypt|2.7|Q3|na|3.8|34.6|Nov|37.7|7.1|Q3§
    Israel|3.3|Q3|2.5|0.9|3.3|Nov|4.3|2.8|Nov
    Saudi Arabia|8.7|2022|na|-1.1|1.7|Nov|2.3|5.1|Q3
    South Africa|-0.7|Q3|-1.0|0.6|5.6|Nov|6.0|31.9|Q3§"""
    economist_keys = [
        "country", "gdp", "gdp_period", "gdp_quarter", "gdp_annual",
        "cpi", "cpi_period", "cpi_annual", "unemployment", "unemployment_period",
    ]
    economist_records = []
    for line in economist_source.splitlines():
        observation = dict(zip(economist_keys, line.split("|"), strict=True))
        for key in ("gdp", "gdp_annual", "cpi", "cpi_annual", "unemployment"):
            if observation[key] not in {"nil", "na"}:
                observation[key] = float(observation[key])
        for key in ("gdp", "cpi"):
            value = observation[key]
            observation[f"{key}_color"] = (
                "#ffc1ae" if isinstance(value, float) and value < 0 else "#acd0df"
            ) if value != "nil" else "transparent"
        for key in ("cpi", "cpi_annual"):
            value = observation[key]
            observation[f"{key}_format"] = "num0" if isinstance(value, float) and value >= 100 else "num1"
        economist_records.append(observation)
    return (economist_records,)


@app.cell(expand_output=True)
def economist_recreation(EvidentialTable, col, economist_records, mo):
    economist = mo.ui.anywidget(
        EvidentialTable(
            economist_records,
            columns=[
                col.text("country", title=" "),
                col.group(
                    "Gross domestic product\n% change on year ago:",
                    [
                        col.subcolumns(
                            "latest",
                            [
                                col.number("gdp", fmt="num1").color(conditional_colors="gdp_color"),
                                col.auto("gdp_period").fmt("@").font_color("#808080"),
                            ],
                        ),
                        col.number("gdp_quarter", fmt="num1", title="quarter*"),
                        col.number("gdp_annual", fmt="num1", title="2023†"),
                    ],
                ),
                col.group(
                    "Consumer prices\n% change on year ago:",
                    [
                        col.subcolumns(
                            "latest",
                            [
                                col.number("cpi", fmt_column="cpi_format").color(
                                    conditional_colors="cpi_color"
                                ),
                                col.auto("cpi_period").font_color("#808080"),
                            ],
                        ),
                        col.number("cpi_annual", fmt_column="cpi_annual_format", title="2023†"),
                    ],
                ),
                col.group(
                    "Unemployment\nrate",
                    [
                        col.subcolumns(
                            "%",
                            [
                                col.number("unemployment", fmt="num1"),
                                col.auto("unemployment_period").fmt("@").font_color("#808080"),
                            ],
                        ),
                    ],
                ),
            ],
            title="Economic data",
            subtitle="1 of 2",
            page_size="all",
            sortable=False,
            download=False,
            row_shading=True,
            row_lines=False,
            border=False,
            width=835,
            theme={
                "background": "#ffffff", "text": "#242424", "muted": "#808080",
                "header_bg": "#ffffff", "header_text": "#242424",
                "header_border": "#808080", "shading": "#d5e7ef",
                "hover": "#d5e7ef", "font_size": "14px",
            },
            caption=(
                "Source: Haver Analytics. ∗% change on previous quarter, annual rate. "
                "†The Economist Intelligence Unit estimate/forecast. §Not seasonally adjusted. "
                "‡New series. ∗∗Year ending June. ††Latest 3 months. ‡‡3-month moving average. "
                "Note: Euro area consumer prices are harmonised."
            ),
        )
    )
    economist_css = """
    <style>
    .economist-recreation { max-width: 835px; font-family: 'Arial Narrow', Arial, sans-serif; }
    .economist-recreation .et-root { line-height: 1.25; }
    .economist-recreation .et-title { font-size: 21px; font-weight: 700; }
    .economist-recreation .et-subtitle { font-size: 17px; color: #242424; }
    .economist-recreation .et-titlebar { margin-bottom: 4px; }
    .economist-recreation .et-th { font-weight: 400; color: #808080; padding: 2px 5px; text-align: left; }
    .economist-recreation .et-th-group { text-align: left; color: #242424; font-weight: 700; letter-spacing: 0; font-size: 17px; border-left: 1px solid #808080; }
    .economist-recreation .et-th-group .et-th-title { white-space: nowrap; }
    .economist-recreation .et-th-group .et-th-line:not(:first-child) { color: #808080; font-size: 14px; font-weight: 400; }
    .economist-recreation .et-th-subcolumns .et-th-inner { display: flex; }
    .economist-recreation .et-th-group:last-child .et-th-line { font-size: 17px; font-weight: 700; color: #242424; }
    .economist-recreation .et-th-group::after { display: none; }
    .economist-recreation .et-th-group-blank { border-left: none; }
    .economist-recreation .et-th { cursor: default; }
    .economist-recreation .et-th:hover { background: #ffffff; }
    .economist-recreation .et-td { padding-top: 1px; padding-bottom: 1px; }
    .economist-recreation .et-td:first-child { width: 29%; padding-left: 7px; }
    .economist-recreation .et-row:not(.et-row-shaded) .et-td:not(.et-color-cell) { background: #d5e7ef; }
    .economist-recreation .et-row-shaded .et-td:not(.et-color-cell) { background: #ffffff; }
    .economist-recreation .et-td[data-column-index='2'],
    .economist-recreation .et-td[data-column-index='6'],
    .economist-recreation .et-td[data-column-index='9'] { font-size: 11px; }
    .economist-recreation .et-row:nth-child(6) .et-td,
    .economist-recreation .et-row:nth-child(15) .et-td,
    .economist-recreation .et-row:nth-child(23) .et-td { border-top: 1px solid #808080; }
    .economist-recreation .et-caption { color: #808080; font-size: 12px; margin-top: 3px; }
    .economist-recreation .et-table-actions { display: none; }
    </style>
    """
    mo.Html(f'{economist_css}<div class="economist-recreation">{economist.text}</div>')
    return


if __name__ == "__main__":
    app.run()
