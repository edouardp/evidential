"""Measure the bundled renderer with real label fitting, clustering and layout."""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import threading
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import sync_playwright

from evidential import EvidentialTable, col, label
from scripts.api_screenshots import _launch

ROOT = Path(__file__).resolve().parents[1]


def scenario(count: int, samples: int = 5) -> dict:
    """Construct through the public API, outside the browser timing interval."""
    if samples < 1 or count < 20 * (samples + 1):
        raise ValueError("count must allow 20 rows for the initial page and each positive navigation sample")
    data = [
        {"name": f"Item {index}", "score": index % 101, "a": index % 101, "b": index % 101} for index in range(count)
    ]
    table = EvidentialTable(
        data,
        columns=[
            col.text("name"),
            col.bar("score", label=label.fmt("num0").auto_position("outside end")).scale(domain=(0, 100)),
            col.points({"a": "Before", "b": "After"}).scale(domain=(0, 100)),
        ],
        page_size=20,
        search=False,
        width="100%",
    )
    return {"rows": table.rows, "columns": table.columns, "options": table.options, "row_layout": table.row_layout}


@contextmanager
def server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as service:
        thread = threading.Thread(target=service.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{service.server_port}"
        finally:
            service.shutdown()
            thread.join(timeout=5)


def benchmark(counts: list[int], *, samples: int = 5, engine: str = "chromium") -> dict:
    if not counts or engine not in {"chromium", "webkit"}:
        raise ValueError("provide dataset sizes and a supported browser engine")
    datasets = [scenario(count, samples) for count in counts]
    with server() as url, sync_playwright() as playwright:
        browser = _launch(playwright) if engine == "chromium" else playwright.webkit.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{url}/frontend/preview.html", wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            results = [
                page.evaluate(
                    """async ({data, samples}) => {
                        const {benchmarkTable} = await import('/frontend/browser_benchmark.js');
                        return benchmarkTable(data, samples);
                    }""",
                    {"data": data, "samples": samples},
                )
                for data in datasets
            ]
            return {
                "engine": engine,
                "version": browser.version,
                "measurement": "render/click through three real animation frames; includes layout, observer callbacks and frame waits; excludes data transfer and Python preparation; not GPU paint timing",
                "results": results,
            }
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, nargs="+", default=[10000, 50000, 100000])
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    arguments = parser.parse_args()
    print(json.dumps(benchmark(arguments.rows, samples=arguments.samples, engine=arguments.engine), indent=2))
