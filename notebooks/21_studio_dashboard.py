# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
#     "evidence-tables",
#     "marimo-studio==0.3.0",
# ]
#
# [tool.uv.sources]
# # Not on PyPI yet: in a sandboxed run, install the local checkout instead.
# evidence-tables = { path = "..", editable = true }
#
# [tool.marimo-studio]
# default = "dashboard"
# view_root = "studio/21_studio_dashboard"
# runtime = "server"
# runtimes = ["server"]
#
# [tool.marimo-studio.cells]
# ///
"""One notebook, an EvidenceTable dashboard, and a marimo Studio view.

Run it with Studio so the view can project the notebook's cells and values::

    uv run --with "marimo-studio[deno]" marimo edit notebooks/21_studio_dashboard.py

The committed view lives in ``notebooks/studio/21_studio_dashboard/dashboard``.
It projects the live ``EvidenceTable`` widget through ``<marimo-cell>`` and the
KPI dictionary through ``mo-value``; because the widget is interactive, the view
uses Studio's **Server** runtime.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def intro(mo):
    mo.md("""
    # Studio dashboard

    A self-contained notebook (no database, no network) that a marimo Studio
    view projects: a live `EvidenceTable`, a region filter, and a KPI strip.
    Change the filter and both the table and the KPIs update everywhere.
    """)
    return


@app.cell
def _():
    import marimo as mo

    from evidence_tables import EvidenceTable

    return EvidenceTable, mo


@app.cell
def orders():
    orders = [
        {"region": "Americas", "city": "New York", "trips": 12040, "revenue": 412300, "tip_rate": 0.21},
        {"region": "Americas", "city": "Los Angeles", "trips": 8320, "revenue": 287100, "tip_rate": 0.16},
        {"region": "Americas", "city": "Chicago", "trips": 5310, "revenue": 141900, "tip_rate": 0.09},
        {"region": "Europe", "city": "London", "trips": 15600, "revenue": 523400, "tip_rate": 0.33},
        {"region": "Europe", "city": "Paris", "trips": 6890, "revenue": 198200, "tip_rate": 0.07},
        {"region": "Asia", "city": "Tokyo", "trips": 9800, "revenue": 355800, "tip_rate": 0.0},
        {"region": "Asia", "city": "Singapore", "trips": 7420, "revenue": 301500, "tip_rate": 0.12},
    ]
    return (orders,)


@app.cell
def region_filter(mo, orders):
    # Project this cell into the view to render a live native control.
    region = mo.ui.dropdown(
        options=["All regions", *sorted({row["region"] for row in orders})],
        value="All regions",
        label="Region",
    )
    region
    return (region,)


@app.cell
def filtered(orders, region):
    if region.value == "All regions":
        filtered = list(orders)
    else:
        filtered = [row for row in orders if row["region"] == region.value]
    return (filtered,)


@app.cell
def kpis(filtered):
    # mo-value projections read individual entries of this dictionary.
    total_revenue = sum(row["revenue"] for row in filtered)
    total_trips = sum(row["trips"] for row in filtered)
    avg_tip = (
        sum(row["tip_rate"] * row["trips"] for row in filtered) / total_trips if total_trips else 0.0
    )
    kpis = {
        "cities": len(filtered),
        "trips": total_trips,
        "revenue": total_revenue,
        "avg_tip": round(avg_tip * 100, 1),
    }
    return (kpis,)


@app.cell
def revenue_table(EvidenceTable, filtered):
    # The live EvidenceTable widget is this cell's output; <marimo-cell
    # name="revenue_table"> mounts it in the view.
    EvidenceTable(
        filtered,
        title="Revenue by city",
        subtitle="Bars, colour scales and deltas",
        row_shading=True,
        column_config={
            "region": {"title": "Region", "align": "left"},
            "city": {"title": "City", "align": "left"},
            "trips": {"title": "Trips", "fmt": "num0"},
            "revenue": {"title": "Revenue", "fmt": "usd0", "viz": "bar"},
            "tip_rate": {
                "title": "Tip rate",
                "fmt": "pct1",
                "viz": "color",
                "color_scale": ["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
                "color_options": {"min": 0, "max": 0.35},
            },
        },
    )
    return


if __name__ == "__main__":
    app.run()
