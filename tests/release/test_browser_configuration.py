import runpy
from pathlib import Path
from unittest.mock import Mock

import pytest

launch = runpy.run_path(str(Path(__file__).parents[1] / "browser/conftest.py"))["_launch"]


def test_required_browser_does_not_silently_skip() -> None:
    playwright = Mock()
    playwright.chromium.launch.side_effect = RuntimeError("not installed")
    assert launch(playwright) is None
    with pytest.raises(pytest.fail.Exception, match="required"):
        launch(playwright, required=True)


def test_browser_falls_back_to_playwright_chromium() -> None:
    playwright = Mock()
    browser = Mock()
    playwright.chromium.launch.side_effect = [RuntimeError(), RuntimeError(), browser]
    assert launch(playwright, required=True) is browser
    assert playwright.chromium.launch.call_args.kwargs == {"headless": True}
