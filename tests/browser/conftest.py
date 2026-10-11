"""Fixtures for real-browser functional tests.

These tests serve the repository over HTTP (so the bundled ESM module loads)
and drive a Chromium-based browser through Playwright. They use an installed
Edge/Chrome when available, so no browser download is required.
"""

from __future__ import annotations

import functools
import http.server
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


def _launch(playwright):
    """Prefer an installed browser so tests need no `playwright install`."""
    for kwargs in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            return playwright.chromium.launch(headless=True, **kwargs)
        except Exception:  # pragma: no cover - depends on the machine
            continue
    return None


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = _launch(playwright)
        if browser is None:
            pytest.skip("No Chromium-based browser (msedge/chrome/chromium) available")
        yield browser
        browser.close()


@pytest.fixture()
def page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    yield page
    page.close()
