import pytest

from scripts.benchmark_browser import scenario

pytestmark = pytest.mark.browser


def test_browser_benchmark_exercises_layout_labels_and_clusters(page, live_server):
    page.goto(f"{live_server}/frontend/preview.html", wait_until="networkidle")
    report = page.evaluate(
        """async data => {
            const {benchmarkTable} = await import('/frontend/browser_benchmark.js');
            return benchmarkTable(data, 1);
        }""",
        scenario(40, 1),
    )
    assert report["rows"] == 40
    assert report["visible_rows"] == 20
    assert report["fitted_labels"] == 20
    assert report["point_clusters"] == 20
    assert report["initial_ms"] > 0
    assert report["navigation_median_ms"] > 0
    assert page.locator(".et-table").count() == 0  # cleanup runs, including observers
