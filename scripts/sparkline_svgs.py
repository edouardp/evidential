#!/usr/bin/env python
"""Render standalone sparkline SVGs for documentation.

The sparkline renderer builds its SVG in the DOM, so the most faithful way to get
a standalone file is to ask the *committed* renderer for one: this script mounts
an :class:`~evidential.EvidentialTable` with one row per series and one column
per style in a headless Chromium, pulls the ``<svg>`` back out of each cell,
resolves the CSS variables, and writes ``line-N.svg`` / ``area-N.svg`` /
``bar-N.svg`` (one of each style per series) to ``docs/img/sparklines/``. An
``index.html`` gallery is written alongside them.

Run it with::

    uv run python scripts/sparkline_svgs.py

It needs the ``playwright`` dev dependency and a Chromium-based browser
(Edge/Chrome/Chromium) — the same requirement as ``tests/browser``. The output
is committed, so re-run it only when an option or the renderer changes.
"""

from __future__ import annotations

import json
import math
import random
import threading
import xml.etree.ElementTree as ET
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from evidential import EvidentialTable, col, settings

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img" / "sparklines"
HTML = ROOT / "__sparklines.html"
WIDTH, HEIGHT = 120, 32

# Five series, 24 points each: half a named shape, half a seeded random walk, so
# the set has real variety but regenerates identically.


def _shape(name: str, t: float, level: float, amp: float) -> float:
    if name == "rise":
        return level + amp * (2 * t - 1)
    if name == "fall":
        return level + amp * (1 - 2 * t)
    if name == "wave":
        return level + amp * math.sin(t * math.tau * 1.75)
    if name == "steps":
        return level + amp * (0.6 if int(t * 5) % 2 else -0.6)
    return level  # "flat"


def _series(seed: int, shape: str, *, level: float, amp: float, n: int = 24) -> list[float]:
    rng = random.Random(seed)
    walk = 0.0
    values = []
    for index in range(n):
        t = index / (n - 1)
        walk = walk * 0.85 + rng.uniform(-1, 1) * amp * 0.3
        values.append(round(0.5 * _shape(shape, t, level, amp) + 0.5 * (level + walk), 1))
    return values


SERIES: dict[str, list[float]] = {
    "orders": _series(1, "rise", level=24, amp=16),
    "revenue": _series(2, "fall", level=60, amp=26),
    "sessions": _series(3, "wave", level=64, amp=26),
    "aov": _series(4, "steps", level=200, amp=60),
    "conversion": _series(5, "flat", level=12, amp=6),
}

# The three styles, with the colours the notebooks use.
STYLES: list[tuple[str, dict[str, Any]]] = [
    ("line", {"type": "line", "color": "#2563eb"}),
    ("area", {"type": "area", "color": "#53768a"}),
    ("bar", {"type": "bar", "color": "#97ba99"}),
]


class _Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:  # noqa: D102 - silence the log
        pass


def _serve(directory: Path) -> tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Handler, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def _table() -> EvidentialTable:
    """One row per series, one column per style — so every series gets all three."""
    rows = [{name: list(values) for name, _ in STYLES} for values in SERIES.values()]
    columns = [col.sparkline(name, title=name, width=WIDTH, height=HEIGHT, **options) for name, options in STYLES]
    return EvidentialTable(rows, columns=columns, settings=settings(stretch=False))


def _page(table: EvidentialTable) -> str:
    data = {"rows": table.rows, "columns": table.columns, "options": table.options}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="/src/evidential/static/table.css" />
  <style>body {{ margin: 20px; background: #fff; }}</style>
</head>
<body>
  <div id="t"></div>
  <script type="module">
    import widget from "/src/evidential/static/table.js";
    const data = {json.dumps(data)};
    widget.render({{
      model: {{ get: (k) => data[k], on() {{}}, off() {{}}, save_changes() {{}} }},
      el: document.getElementById("t"),
    }});
  </script>
</body>
</html>
"""


def _fetch(table: EvidentialTable) -> list[str]:
    """Mount the table with the committed renderer and pull out each sparkline SVG."""
    from playwright.sync_api import sync_playwright

    HTML.write_text(_page(table), encoding="utf-8")
    server, port = _serve(ROOT)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 640, "height": 200}, device_scale_factor=2)
            page.goto(f"http://127.0.0.1:{port}/{HTML.name}", wait_until="load")
            page.wait_for_selector("#t tbody .et-sparkline", timeout=20_000)
            page.wait_for_timeout(200)
            svgs = page.eval_on_selector_all("#t tbody .et-sparkline", "els => els.map((el) => el.outerHTML)")
            browser.close()
            return svgs
    finally:
        server.shutdown()
        HTML.unlink(missing_ok=True)


def _content_bbox(root: ET.Element) -> tuple[float, float, float, float]:
    """The painted bounds of a sparkline, including the stroke half-width."""
    x0 = y0 = float("inf")
    x1 = y1 = float("-inf")

    def add(x: float, y: float) -> None:
        nonlocal x0, y0, x1, y1
        x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)

    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag in ("polyline", "polygon"):
            half = float(el.get("stroke-width") or 0) / 2
            for point in el.get("points", "").split():
                px, py = (float(value) for value in point.split(","))
                add(px - half, py - half)
                add(px + half, py + half)
        elif tag == "rect":
            x, y, width, height = (float(el.get(key)) for key in ("x", "y", "width", "height"))
            add(x, y)
            add(x + width, y + height)
    return x0, y0, x1, y1


def _standalone(svg: str, color: str) -> str:
    """Make one renderer SVG a self-contained graph: resolve the CSS, drop the
    interaction layer (the invisible hover targets and their tooltips), add a
    namespace, and size the viewBox to the content.

    The declared ``width``/``height`` stay at the renderer's nominal 120x32, but
    the ``viewBox`` is *expanded* to contain the nominal area *and* the painted
    content plus a safety margin past the anti-aliased stroke — so a consumer
    that lays out by the file size, or clips to the viewBox, never cuts the
    graph.
    """
    svg = svg.replace("var(--et-accent, #2563eb)", color)
    svg = svg.replace("color-mix(in srgb, CanvasText 20%, transparent)", "#0f172a33")
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    root = ET.fromstring(svg)
    for parent in root.iter():
        for child in list(parent):
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "title" or (tag == "circle" and child.get("fill") == "transparent"):
                parent.remove(child)
    margin = 1.5
    x0, y0, x1, y1 = _content_bbox(root)
    ux0, uy0 = min(x0, 0.0), min(y0, 0.0)
    ux1, uy1 = max(x1, float(WIDTH)), max(y1, float(HEIGHT))
    box = (ux0 - margin, uy0 - margin, (ux1 - ux0) + margin * 2, (uy1 - uy0) + margin * 2)
    root.set("viewBox", " ".join(f"{value:g}" for value in box))
    root.set("width", str(WIDTH))
    root.set("height", str(HEIGHT))
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    return ET.tostring(root, encoding="unicode") + "\n"


def _names() -> list[str]:
    """File names in DOM extraction order (row-major: series, then style)."""
    return [f"{style}-{index}" for index in range(1, len(SERIES) + 1) for style, _ in STYLES]


def _gallery_html(svgs: dict[str, str]) -> str:
    sections = []
    for style, _ in STYLES:
        cells = "\n".join(
            f"        <figure><div>{svgs[f'{style}-{index}']}</div>"
            f"<figcaption>{style}-{index}.svg</figcaption></figure>"
            for index in range(1, len(SERIES) + 1)
        )
        sections.append(f'  <h2>{style}</h2>\n  <div class="row">\n{cells}\n  </div>')
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>evidential sparkline gallery</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 32px; color: #0f172a; }}
    h1 {{ margin: 0 0 4px; }}
    h2 {{ font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.08em;
         color: #64748b; margin: 28px 0 10px; }}
    .row {{ display: flex; flex-wrap: wrap; gap: 16px; }}
    figure {{ margin: 0; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; }}
    figcaption {{ margin-top: 10px; font-size: 0.8rem; color: #64748b; }}
  </style>
</head>
<body>
  <h1>Sparkline gallery</h1>
  <p>Generated by <code>scripts/sparkline_svgs.py</code> from the committed renderer.</p>
{body}
</body>
</html>
"""


def main() -> None:
    colours = dict(STYLES)
    names = _names()
    raw = _fetch(_table())
    OUT.mkdir(parents=True, exist_ok=True)
    svgs: dict[str, str] = {}
    for name, svg in zip(names, raw, strict=True):
        style = name.rsplit("-", 1)[0]
        text = _standalone(svg, str(colours[style].get("color") or "#2563eb"))
        (OUT / f"{name}.svg").write_text(text, encoding="utf-8")
        svgs[name] = text
    print(f"wrote {len(svgs)} SVGs to {OUT.relative_to(ROOT)}")
    (OUT / "index.html").write_text(_gallery_html(svgs), encoding="utf-8")
    print(f"wrote {(OUT / 'index.html').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
