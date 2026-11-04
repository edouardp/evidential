"""Fixtures for real-browser functional tests.

These tests serve the repository over HTTP (so the bundled ESM module loads)
and drive the selected Playwright engine. Chromium prefers installed Edge/Chrome;
set EVIDENTIAL_BROWSER=webkit (or firefox) to exercise another installed engine.
"""

from __future__ import annotations

import functools
import http.server
import os
import socket
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def live_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # pragma: no cover - silence access logs
            pass

    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _launch(playwright, *, required=False, engine="chromium"):
    """Prefer an installed browser so tests need no `playwright install`."""
    if engine not in {"chromium", "webkit", "firefox"}:
        raise ValueError(f"Unsupported browser engine: {engine}")
    choices = ({"channel": "msedge"}, {"channel": "chrome"}, {}) if engine == "chromium" else ({},)
    for kwargs in choices:
        try:
            return getattr(playwright, engine).launch(headless=True, **kwargs)
        except Exception:  # pragma: no cover - depends on the machine
            continue
    if required:
        pytest.fail(f"A {engine} browser is required; run uv run playwright install {engine}")
    return None


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        engine = os.environ.get("EVIDENTIAL_BROWSER", "chromium")
        browser = _launch(playwright, required=os.environ.get("EVIDENTIAL_REQUIRE_BROWSER") == "1", engine=engine)
        if browser is None:
            pytest.skip(f"No {engine} browser available")
        yield browser
        browser.close()


@pytest.fixture()
def page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    yield page
    page.close()
