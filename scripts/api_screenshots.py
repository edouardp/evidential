#!/usr/bin/env python
"""Render the API documentation screenshots.

Builds the illustrative :class:`~evidential.EvidentialTable` objects referenced
from ``docs/api/API.md``, mounts each against the committed static bundle in a
headless Chromium, and writes one PNG per example to ``docs/api/images/``.

Run it with::

    uv run python scripts/api_screenshots.py

It needs the ``playwright`` dev dependency and a Chromium-based browser
(Edge/Chrome/Chromium) — the same requirement as ``tests/browser``. The output
is committed, so re-run it only when an example or the renderer changes;
``make lint`` checks the formatting of this file like any other script.
"""

from __future__ import annotations

import datetime as dt
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING

import duckdb

from evidential import (
    EvidentialTable,
    cells_body,
    col,
    cols_merge_n_pct,
    cols_merge_range,
    cols_merge_uncert,
    comparison_table,
    grouped_table,
    pivot_table,
    query_table,
    settings,
    tab_style,
    text_transform,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "api" / "images"
HTML = ROOT / "__api_examples.html"
SAMPLE = ROOT / "notebooks" / "sample_data" / "needful_things" / "orders.parquet"
NOW = dt.datetime.now().replace(microsecond=0)


def _ago(**delta: int) -> str:
    return (NOW - dt.timedelta(**delta)).strftime("%Y-%m-%d %H:%M:%S")


def _orders() -> duckdb.DuckDBPyConnection:
    """An in-memory DuckDB with Evidence's sample orders view."""
    connection = duckdb.connect()
    connection.execute("CREATE SCHEMA needful_things")
    connection.execute(f"CREATE VIEW needful_things.orders AS SELECT * FROM read_parquet('{SAMPLE}')")
    return connection


# --------------------------------------------------------------------------
# The examples, in the order they appear in API.md.


def quickstart() -> EvidentialTable:
    rows = [
        {"city": "Boston", "trips": 1284, "revenue": 48120.50, "tip_rate": 0.183},
        {"city": "New York", "trips": 3502, "revenue": 142880.25, "tip_rate": 0.171},
        {"city": "Chicago", "trips": 2118, "revenue": 76540.00, "tip_rate": 0.164},
        {"city": "San Francisco", "trips": 1907, "revenue": 98320.75, "tip_rate": 0.196},
        {"city": "Seattle", "trips": 1463, "revenue": 61140.10, "tip_rate": 0.188},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("city", title="City"),
            col.integer("trips", title="Trips"),
            col.currency("revenue", title="Revenue"),
            col.percent("tip_rate", decimals=1, title="Tip rate"),
        ],
        settings=settings(
            title="Tipping by city",
            caption="Illustrative sample orders.",
            width="620px",
        ),
    )


def kinds() -> EvidentialTable:
    rows = [
        {
            "item": "Espresso",
            "count": 1240,
            "price": 3.50,
            "share": 0.42,
            "day": "2024-03-04",
            "origin": "ITA",
            "active": True,
        },
        {
            "item": "Cortado",
            "count": 861,
            "price": 4.25,
            "share": 0.29,
            "day": "2024-03-05",
            "origin": "ESP",
            "active": True,
        },
        {
            "item": "Cold brew",
            "count": 512,
            "price": 5.00,
            "share": 0.17,
            "day": "2024-03-07",
            "origin": "USA",
            "active": False,
        },
        {
            "item": "Matcha",
            "count": 344,
            "price": 5.75,
            "share": 0.12,
            "day": "2024-03-09",
            "origin": "JPN",
            "active": True,
        },
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("item", title="Item"),
            col.integer("count", title="Count"),
            col.currency("price", title="Price"),
            col.percent("share", decimals=0, title="Share"),
            col.date("day", title="Day"),
            col.flag("origin", title="Origin"),
            col.boolean("active", title="Active"),
        ],
        settings=settings(title="Column kinds", width="760px"),
    )


def relative_time() -> EvidentialTable:
    rows = [
        {"event": "Deploy", "at": _ago(hours=2)},
        {"event": "Backup", "at": _ago(days=1)},
        {"event": "Report", "at": _ago(days=6)},
        {"event": "Audit", "at": _ago(weeks=3)},
        {"event": "Renewal", "at": _ago(days=200)},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("event", title="Event"),
            col.datetime("at", relative=True, title="When"),
        ],
        settings=settings(title="Relative time", width="420px"),
    )


def symbols() -> EvidentialTable:
    rows = [
        {"country": "Ireland", "gold": 4, "score": 3},
        {"country": "Cyprus", "gold": 3, "score": 2},
        {"country": "France", "gold": 2, "score": 4},
        {"country": "Sweden", "gold": 2, "score": 1},
        {"country": "Slovenia", "gold": 1, "score": 5},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("country", title="Country"),
            col.symbols("gold", symbol="■", color="#d97706", title="Glyph"),
            col.symbols("gold", shape="square", color="#d97706", title="Squares"),
            col.symbols("gold", shape="circle", color="#d97706", title="Circles"),
            col.rating("score", title="Rating"),
        ],
        settings=settings(
            title="Repeated symbols",
            width="720px",
            row_lines=False,
            border=False,
        ),
    )


def visualizations() -> EvidentialTable:
    rows = [
        {
            "region": "West",
            "revenue": 142000,
            "growth": 0.12,
            "share": 0.38,
            "trend": [3, 4, 4, 6, 7, 9, 11],
        },
        {
            "region": "East",
            "revenue": 98000,
            "growth": -0.04,
            "share": 0.26,
            "trend": [9, 8, 8, 6, 5, 5, 4],
        },
        {
            "region": "South",
            "revenue": 76000,
            "growth": 0.07,
            "share": 0.21,
            "trend": [4, 5, 5, 6, 6, 7, 7],
        },
        {
            "region": "North",
            "revenue": 54000,
            "growth": 0.02,
            "share": 0.15,
            "trend": [6, 6, 6, 5, 6, 6, 6],
        },
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("region", title="Region"),
            col.bar("revenue", title="Revenue"),
            col.bar("growth", center=True, title="Growth"),
            col.color("share", title="Share"),
            col.chip("region", title="Chip"),
            col.sparkline("trend", type="area", title="Trend"),
            col.percent("growth", decimals=0, title="Δ").delta(),
        ],
        settings=settings(title="Visualisations", width="860px"),
    )


def styling() -> EvidentialTable:
    rows = [
        {"metric": "Revenue", "q1": 48120.50, "q2": 51240.00, "change": 0.065},
        {"metric": "Costs", "q1": -31400.00, "q2": -29180.00, "change": 0.071},
        {"metric": "Margin", "q1": 16720.50, "q2": 22060.00, "change": 0.319},
        {"metric": "Headcount", "q1": -124, "q2": -131, "change": -0.056},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("metric", title="Metric").bold(),
            col.currency("q1", decimals=0, title="Q1").neg(),
            col.currency("q2", decimals=0, title="Q2").neg(bracket=True),
            col.percent("change", decimals=1, title="Change").neg().italic(),
            col.percent("change", decimals=1, title="Δ %").bold().highlight("#fef3c7"),
        ],
        settings=settings(
            title="Body-cell styling",
            align_decimals=True,
            font_size="+1",
            width="600px",
        ),
    )


def groups() -> EvidentialTable:
    rows = [
        {"region": "North", "revenue": 48120.5, "cost": -19800.0, "profit": 28320.5},
        {"region": "South", "revenue": 36740.0, "cost": -16120.0, "profit": 20620.0},
        {"region": "East", "revenue": 51280.0, "cost": -21500.0, "profit": 29780.0},
        {"region": "West", "revenue": 29860.0, "cost": -13240.0, "profit": 16620.0},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("region", title="Region"),
            col.group(
                "Financials",
                [
                    col.currency("revenue", title="Revenue"),
                    col.currency("cost", title="Cost"),
                    col.currency("profit", title="Profit"),
                ],
            ),
        ],
        settings=settings(title="Grouped headers", width="520px"),
    )


def subcolumns() -> EvidentialTable:
    rows = [
        {"country": "Ireland", "gdp": 2.4, "quarter": "Q4", "forecast": 2.1, "cpi": 1.8, "month": "Dec"},
        {"country": "Portugal", "gdp": 3.1, "quarter": "Q4", "forecast": 2.6, "cpi": 2.4, "month": "Dec"},
        {"country": "Greece", "gdp": 2.8, "quarter": "Q3", "forecast": 2.3, "cpi": 3.2, "month": "Nov"},
        {"country": "Spain", "gdp": 1.9, "quarter": "Q4", "forecast": 2.0, "cpi": 2.1, "month": "Dec"},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("country", title="Country"),
            col.group(
                "Gross domestic product",
                [
                    col.subcolumns(
                        "Latest",
                        [
                            col.number("gdp", fmt="num1", align="right").neg(),
                            col.auto("quarter").align("left").font_color("#94a3b8"),
                        ],
                    ),
                    col.number("forecast", fmt="num1", align="right", title="Annual forecast"),
                ],
            ),
            col.group(
                "Consumer prices",
                [
                    col.subcolumns(
                        "Latest",
                        [
                            col.number("cpi", fmt="num1", align="right").neg(),
                            col.auto("month").align("left").font_color("#94a3b8"),
                        ],
                    )
                ],
            ),
        ],
        settings=settings(title="Sub-columns inside groups", width="760px"),
        row_lines=False,
        border=False,
    )


def merged() -> EvidentialTable:
    rows = [
        {"site": "Alpha", "low": 12, "high": 48, "value": 30.2, "uncert": 1.4, "n": 842, "pct": 0.62},
        {"site": "Beta", "low": 8, "high": 31, "value": 19.6, "uncert": 0.9, "n": 511, "pct": 0.38},
        {"site": "Gamma", "low": 21, "high": 60, "value": 42.1, "uncert": 2.0, "n": 1204, "pct": 0.89},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("site", title="Site"),
            col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
            col.merge(
                "measurement",
                cols_merge_uncert("value", "uncert", fmt="num1", title="Value"),
            ),
            col.merge("share", cols_merge_n_pct("n", "pct", title="Share")),
        ],
        settings=settings(title="Merged columns", width="560px"),
    )


def grouped() -> EvidentialTable:
    return grouped_table(
        _orders(),
        "SELECT category AS category, sales FROM needful_things.orders",
        dimensions=["category"],
        measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
        dimension_config={"category": col.text("category")},
        measure_config={
            "sales": col.currency("sales", decimals=0),
            "orders": col.integer("orders"),
        },
        title="Grouped totals",
        page_size=10,
        width="560px",
    )


def pivot() -> EvidentialTable:
    return pivot_table(
        _orders(),
        "SELECT category, year(order_datetime) AS year, sales FROM needful_things.orders",
        dimensions=["category"],
        pivots=["year"],
        measures=["round(sum(sales), 0) AS sales"],
        dimension_config={"category": col.text("category")},
        measure_config={"sales": col.currency("sales", decimals=0)},
        title="Pivoted columns",
        page_size=10,
        width="640px",
    )


def comparison() -> EvidentialTable:
    return comparison_table(
        _orders(),
        "SELECT category, order_datetime, sales FROM needful_things.orders",
        dimensions=["category"],
        measures=["round(sum(sales), 0) AS sales"],
        date_column="order_datetime",
        compare_vs="prior year",
        measure_config={"sales": col.currency("sales", decimals=0)},
        title="Prior-period comparison",
        page_size=10,
        width="820px",
    )


def rules() -> EvidentialTable:
    rows = [
        {"category": "Widgets", "sales": 128400.0},
        {"category": "Gadgets", "sales": 96210.0},
        {"category": "Gizmos", "sales": 54180.0},
        {"category": "Doohickeys", "sales": 21760.0},
    ]
    return EvidentialTable(
        rows,
        columns=[
            col.text("category", title="Category"),
            col.number("sales", fmt="usd0", title="Sales").bar(),
        ],
        rules=[
            text_transform(cells_body("category"), str.upper),
            tab_style(cells_body("sales"), color="#b45309"),
        ],
        settings=settings(title="Display rules", width="480px"),
    )


def query() -> EvidentialTable:
    return query_table(
        _orders(),
        "SELECT category, item, round(sum(sales), 0) AS sales FROM needful_things.orders GROUP BY category, item",
        order="sales DESC",
        limit=6,
        columns=[col.text("category"), col.text("item"), col.currency("sales", decimals=0)],
        title="Ad-hoc query",
        width="620px",
    )


EXAMPLES: list[tuple[str, Callable[[], EvidentialTable]]] = [
    ("quickstart", quickstart),
    ("kinds", kinds),
    ("relative-time", relative_time),
    ("symbols", symbols),
    ("visualizations", visualizations),
    ("styling", styling),
    ("groups", groups),
    ("subcolumns", subcolumns),
    ("merged", merged),
    ("grouped-table", grouped),
    ("pivot-table", pivot),
    ("comparison-table", comparison),
    ("rules", rules),
    ("query-table", query),
]


# --------------------------------------------------------------------------
# Rendering


class _Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:  # noqa: D102 - silence the log
        pass


def _serve(directory: Path) -> tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Handler, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def _page(tables: list[tuple[str, EvidentialTable]]) -> str:
    panels = "\n".join(f'  <div class="shot" id="{slug}"></div>' for slug, _ in tables)
    data = {slug: {"rows": t.rows, "columns": t.columns, "options": t.options} for slug, t in tables}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="src/evidential/static/table.css" />
  <style>
    body {{ margin: 0; background: #f8fafc; font-family: ui-sans-serif, system-ui, sans-serif; }}
    .shot {{ display: inline-block; margin: 0; padding: 20px; background: #fff; }}
  </style>
</head>
<body>
{panels}
  <script type="module">
    import widget from "./src/evidential/static/table.js";
    const DATA = {json.dumps(data)};
    const model = (d) => ({{ get: (k) => d[k], set() {{}}, on() {{}}, off() {{}}, save_changes() {{}} }});
    for (const [slug, d] of Object.entries(DATA)) {{
      widget.render({{ model: model(d), el: document.getElementById(slug) }});
    }}
  </script>
</body>
</html>
"""


def render(tables: list[tuple[str, EvidentialTable]]) -> Iterator[Path]:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    HTML.write_text(_page(tables), encoding="utf-8")
    server, port = _serve(ROOT)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 1500, "height": 1000}, device_scale_factor=2)
            page.goto(f"http://127.0.0.1:{port}/{HTML.name}", wait_until="load")
            for slug, _ in tables:
                page.wait_for_selector(f"#{slug} .et-table", timeout=20_000)
            page.wait_for_timeout(600)
            for slug, _ in tables:
                path = OUT / f"{slug}.png"
                page.locator(f"#{slug}").screenshot(path=str(path))
                yield path
            browser.close()
    finally:
        server.shutdown()
        HTML.unlink(missing_ok=True)


def main() -> None:
    tables = [(slug, build()) for slug, build in EXAMPLES]
    for path in render(tables):
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
