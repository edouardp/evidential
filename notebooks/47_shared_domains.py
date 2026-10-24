# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Compare bars, heatmaps and change sequences using shared numeric domains."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import marimo as mo
    from evidential import EvidentialTable, col, domain, label

    return EvidentialTable, col, domain, label, mo


@app.cell
def introduction(mo):
    mo.md("""
    # Shared numeric domains

    Give columns the same `.domain("name")` to pool their values, independently
    of header groups. A reusable `domain.numeric("name")` can also specify
    `.include_zero()`, `.bounds(low, high)`, `.palette(...)`, and `.midpoint(...)`.

    All members contribute before pagination, including hidden columns.
    Filtering recomputes inferred bounds; fixed bounds stay fixed. Palette
    settings affect color encodings; a bar's fill remains an independent choice.
    """)
    return


@app.cell
def shared_counts(domain):
    payments = domain.numeric("payments").include_zero().palette("Blues")
    observations = [
        {"region": "North", "card": 20, "cash": 20, "today": 20, "yesterday": 20},
        {"region": "South", "card": 100, "cash": 50, "today": 150, "yesterday": 200},
        {"region": "East", "card": 0, "cash": 30, "today": None, "yesterday": 80},
    ]
    return observations, payments


@app.cell
def count_example(EvidentialTable, col, label, mo, observations, payments):
    counts = mo.ui.anywidget(
        EvidentialTable(
            observations,
            title="Payment counts · one domain, different encodings",
            subtitle="The combined range is 0–200. Every 20 has the same bar proportion or background color.",
            border=False,
            search=True,
            page_size=0,
            width=900,
            row_lines=False,
            row_shading=True,
            columns=[
                col.text("region"),
                col.group(
                    "Payment type",
                    [
                        col.bar("card", title="Card", format="num0", label=label.auto_position("inside end"))
                           .domain(payments)
                           .scale(axis=True),
                        col.bar("cash", title="Cash", format="num0", label=label.auto_position("inside end"))
                           .domain("payments")
                           .scale(axis=True),
                    ],
                ),
                col.group(
                    "Volume",
                    [
                        col.integer("today").color().domain(payments),
                        col.integer("yesterday").color().domain("payments"),
                    ],
                ),
            ],
        )
    )
    mo.vstack([counts])
    return


@app.cell
def fixed_example(EvidentialTable, col, domain, label, mo):
    changes = domain.numeric("changes").bounds(-10, 10).palette(["#b2182b", "#b8bcc2", "#2166ac"])
    change_table = mo.ui.anywidget(
        EvidentialTable(
            [
                {"metric": "Demand", "current": 4, "previous": 4, "history": [-4, 0, 0.2, 4, 8]},
                {"metric": "Capacity", "current": -2, "previous": -2, "history": [-2, -0.3, 0, 2, 1]},
            ],
            title="Fixed bounds · bars, heatmaps and change sparklines",
            subtitle="Shared range: −10 to +10. Values in −0.5 to +0.5 share the gray neutral color.",
            search=False,
            page_size=0,
            border=False,
            width=900,
            row_lines=False,
            columns=[
                col.text("metric"),
                col.bar("current", center=True, label=label.fmt("num0").auto_position("outside start")).domain(changes),
                col.number("previous").color().domain("changes"),
                col.sparkline("history", type="change", steady=(-0.5, 0.5), width=144).domain(changes),
            ],
        )
    )
    mo.vstack([change_table])
    return


if __name__ == "__main__":
    app.run()
