"""Exercise the two-table notebook through Marimo's real widget connection."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import duckdb
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def football_notebook(tmp_path):
    parquet = tmp_path / "football.parquet"
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE games AS SELECT * FROM (VALUES
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2023-01-01', 2, 0, 'a', 'national'),
                ('Foreign', 'Alpha', 'Foreign (B)', 'Alpha (A)', 'b', 'a', DATE '2023-02-01', 1, 2, 'Cup', 'international'),
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2024-01-01', 1, 1, 'a', 'national'),
                ('Alpha', 'Foreign', 'Alpha (A)', 'Foreign (B)', 'a', 'b', DATE '2024-02-01', 0, 3, 'Cup', 'international')
            ) AS t(home,away,home_ident,away_ident,home_country,away_country,date,gh,ga,competition,level)
        """)
        connection.execute("COPY games TO ? (FORMAT PARQUET)", [str(parquet)])
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    with (tmp_path / "marimo.log").open("w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "marimo",
                "run",
                str(ROOT / "notebooks/46_change_sparklines.py"),
                "--headless",
                "--no-token",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env={**os.environ, "FOOTBALL_PARQUET": str(parquet)},
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(url, timeout=0.5):
                        break
                except (urllib.error.URLError, TimeoutError):
                    if process.poll() is not None:
                        log.seek(0)
                        pytest.fail(log.read())
                    time.sleep(0.1)
            else:
                pytest.fail("The football notebook server did not start")
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def test_team_click_year_change_and_gradient_keep_two_stable_widgets(page, football_notebook):
    page.goto(football_notebook, wait_until="networkidle")
    roots = page.locator(".et-root")
    expect(roots).to_have_count(2, timeout=30000)
    top, bottom = roots.nth(0), roots.nth(1)
    expect(top.locator("tbody tr")).to_have_count(2)
    expect(bottom.locator(".et-empty-body")).to_be_visible()
    expect(top.locator(".et-sparkline-change")).to_have_count(2)
    expect(bottom.locator(".et-sparkline-change")).to_have_count(0)
    top.get_by_role("searchbox").fill("Alpha")
    expect(top.locator("tbody tr")).to_have_count(1)
    top.locator("tbody tr").click()
    expect(bottom.locator("tbody tr")).to_have_count(2)
    expect(bottom.locator(".et-title")).to_have_text("Alpha · 2023")
    expect(bottom.locator("tbody")).to_contain_text("Cup")
    expect(bottom.locator(".et-mark-bar")).to_have_count(2)
    expect(bottom.locator(".et-mark-label")).to_have_count(2)
    # Mark stable widget nodes: changing the filters must update their models.
    top.evaluate("el => el.dataset.originalWidget = 'top'")
    bottom.evaluate("el => el.dataset.originalWidget = 'bottom'")
    year = page.get_by_role("combobox").first
    year.select_option("2024")
    expect(bottom.locator(".et-title")).to_have_text("Alpha · 2024")
    expect(bottom.locator("tbody")).to_contain_text("2024-01-01")
    expect(bottom.locator("tbody")).not_to_contain_text("2023-")
    expect(top.get_by_role("searchbox")).to_have_value("Alpha")
    page.get_by_role("switch", name="Color by goal margin").click()
    expect(top.locator("rect[data-state=steady]")).to_have_attribute("fill", "#b8bcc2")
    assert top.get_attribute("data-original-widget") == "top"
    assert bottom.get_attribute("data-original-widget") == "bottom"
    expect(roots).to_have_count(2)
    top.locator("tbody tr").click()
    expect(bottom.locator(".et-empty-body")).to_be_visible()
    expect(bottom.locator(".et-title")).to_have_text("Match details")
    if path := os.environ.get("EVIDENTIAL_REVIEW_SCREENSHOT"):
        page.screenshot(path=str(Path(path).with_name("football-explorer.png")), full_page=True)
