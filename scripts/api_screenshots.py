#!/usr/bin/env python
"""Capture the documentation screenshots from a marimo notebook.

``notebooks/49_api_screenshots.py`` owns the API examples and README hero;
``notebooks/50_graphics_gallery.py`` owns the README graphic gallery and
``notebooks/51_table_layouts.py`` owns the layout gallery. The Studio table
comes from ``notebooks/21_studio_dashboard.py``. Each table
lives in a named cell, and the cell name is the image slug. This script starts
each notebook with ``marimo run --headless`` and uses Playwright to screenshot
the ``.et-root`` output of every target cell.

Run it with::

    make api-screenshots

It needs the ``playwright`` dev dependency and a Chromium-based browser
(Edge/Chrome/Chromium) — the same requirement as ``tests/browser``. The output
is committed, so re-run only when an API example or the renderer changes.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebooks" / "49_api_screenshots.py"
GALLERY_NOTEBOOK = ROOT / "notebooks" / "50_graphics_gallery.py"
STUDIO_NOTEBOOK = ROOT / "notebooks" / "21_studio_dashboard.py"
LAYOUT_NOTEBOOK = ROOT / "notebooks" / "51_table_layouts.py"
OUT = ROOT / "docs" / "api" / "images"
PREVIEW = ROOT / "docs" / "preview.png"
GALLERY_OUT = ROOT / "docs" / "img" / "graphics"
LAYOUT_OUT = ROOT / "docs" / "img" / "layouts"

#: (image slug, marimo cell name), in API.md order.
SHOTS: list[tuple[str, str]] = [
    ("quickstart", "quickstart"),
    ("kinds", "kinds"),
    ("relative-time", "relative_time"),
    ("symbols", "symbols"),
    ("visualizations", "visualizations"),
    ("back-to-back", "back_to_back"),
    ("styling", "styling"),
    ("groups", "groups"),
    ("subcolumns", "subcolumns"),
    ("merged", "merged"),
    ("grouped-table", "grouped_totals"),
    ("pivot-table", "pivoted_columns"),
    ("comparison-table", "prior_comparison"),
    ("rules", "rules"),
    ("query-table", "ad_hoc_query"),
]

#: (image path, marimo cell name) for screenshots outside the API reference.
EXTRAS: list[tuple[Path, str]] = [
    (PREVIEW, "preview"),
]

#: (image path, marimo cell name) for the README graphic gallery.
GALLERY: list[tuple[Path, str]] = [
    (GALLERY_OUT / "bar.png", "graphic_bar"),
    (GALLERY_OUT / "bar-centered.png", "graphic_bar_centered"),
    (GALLERY_OUT / "bar-overlay.png", "graphic_bar_overlay"),
    (GALLERY_OUT / "bar-back-to-back.png", "graphic_bar_back_to_back"),
    (GALLERY_OUT / "dumbbell.png", "graphic_dumbbell"),
    (GALLERY_OUT / "points.png", "graphic_points"),
    (GALLERY_OUT / "point-overlaps.png", "graphic_point_overlaps"),
    (GALLERY_OUT / "boxplot.png", "graphic_boxplot"),
    (GALLERY_OUT / "distribution.png", "graphic_distribution"),
    (GALLERY_OUT / "stacked-bar.png", "graphic_stacked_bar"),
    (GALLERY_OUT / "stack-likert.png", "graphic_stack_likert"),
    (GALLERY_OUT / "strip.png", "graphic_strip"),
    (GALLERY_OUT / "color.png", "graphic_color"),
    (GALLERY_OUT / "chip.png", "graphic_chip"),
    (GALLERY_OUT / "delta.png", "graphic_delta"),
    (GALLERY_OUT / "sparklines.png", "graphic_sparklines"),
    (GALLERY_OUT / "football-form.png", "graphic_football_form"),
    (GALLERY_OUT / "symbols.png", "graphic_symbols"),
    (GALLERY_OUT / "boolean-icons.png", "graphic_boolean_icons"),
    (GALLERY_OUT / "reference.png", "graphic_reference"),
]

#: Named layout examples, in README order. Prose/call excerpts live in notebook 51.
LAYOUTS: list[tuple[Path, str]] = [
    (LAYOUT_OUT / f"{name.replace('_', '-')}.png", f"layout_{name}")
    for name in (
        "simple",
        "titles",
        "footnotes",
        "lines_on",
        "lines_off",
        "frame",
        "shading_off",
        "shading_one",
        "shading_three",
        "headings",
        "headings_centered",
        "headings_column",
        "heading_values",
        "summary_top",
        "summary_bottom",
        "grand_total",
        "combined_totals",
        "groups_one",
        "groups_two",
    )
]


@contextmanager
def _server(notebook: Path) -> Iterator[str]:
    """Start a screenshot notebook and yield its local URL."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "marimo",
                "run",
                str(notebook),
                "--headless",
                "--no-token",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(url, timeout=0.5):
                        yield url
                        return
                except (urllib.error.URLError, TimeoutError):
                    if process.poll() is not None:
                        log.seek(0)
                        raise RuntimeError(f"marimo exited before serving:\n{log.read()}") from None
                    time.sleep(0.1)
            raise RuntimeError("the screenshot notebook did not start within 30 seconds")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _launch(playwright):
    """Prefer an installed browser so no download is required locally."""
    for kwargs in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            return playwright.chromium.launch(headless=True, **kwargs)
        except Exception:  # pragma: no cover - depends on the machine
            continue
    raise RuntimeError("A Chromium-based browser is required; run `uv run playwright install chromium`")


def _wait_for_tables(page, targets: list[tuple[Path, str]]) -> None:
    for cell in [cell for _, cell in targets]:
        page.locator(f'[data-cell-name="{cell}"] .et-table').wait_for(state="visible", timeout=60_000)
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_timeout(500)


# These cells deliberately demonstrate a transient interaction in their image.
# All other screenshots are captured with the pointer outside the table.
HOVER_TARGETS = {"graphic_point_overlaps": ".et-point-composite"}


def _capture(page, cell: str, path: Path) -> Path:
    root = page.locator(f'[data-cell-name="{cell}"] .et-root')
    root.scroll_into_view_if_needed()
    # Let the table keep its configured width while the screenshot gains the
    # same 20px white border the documentation used to draw around each table.
    root.evaluate(
        """el => {
            el.style.padding = '20px';
            el.style.background = '#fff';
            el.style.boxSizing = 'content-box';
        }"""
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if selector := HOVER_TARGETS.get(cell):
        # Padding changes layout. Settle it before opening a transient popover.
        root.scroll_into_view_if_needed()
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        root.locator(selector).first.hover()
        root.locator(".et-tooltip").wait_for(state="visible")
        bounds = root.bounding_box()
        scroll = page.evaluate("({x: scrollX, y: scrollY})")
        # Element screenshots may scroll again and dismiss the tooltip. Capture
        # the page compositor (including the top layer) at the same bounds.
        page.screenshot(
            path=str(path),
            full_page=True,
            clip={
                "x": bounds["x"] + scroll["x"],
                "y": bounds["y"] + scroll["y"],
                "width": bounds["width"],
                "height": bounds["height"],
            },
        )
    else:
        root.screenshot(path=str(path))
    page.mouse.move(0, 0)
    return path


def _notebook_targets() -> list[tuple[Path, list[tuple[Path, str]]]]:
    api_targets = [(OUT / f"{slug}.png", cell) for slug, cell in SHOTS]
    return [
        (NOTEBOOK, [*api_targets, *EXTRAS]),
        (GALLERY_NOTEBOOK, GALLERY),
        (STUDIO_NOTEBOOK, [(ROOT / "docs" / "img" / "studio-table.png", "revenue_table")]),
        (LAYOUT_NOTEBOOK, LAYOUTS),
    ]


def render(*, output_root: Path = ROOT) -> Iterator[Path]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = _launch(playwright)
        try:
            for notebook, targets in _notebook_targets():
                with _server(notebook) as url:
                    context = browser.new_context(
                        viewport={"width": 1600, "height": 1000},
                        device_scale_factor=2,
                        color_scheme="light",
                    )
                    page = context.new_page()
                    page.goto(url, wait_until="networkidle")
                    _wait_for_tables(page, targets)
                    for path, cell in targets:
                        yield _capture(page, cell, output_root / path.relative_to(ROOT))
                    context.close()
        finally:
            browser.close()


def main() -> None:
    for path in render():
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
