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


@pytest.mark.parametrize("engine", ["webkit", "firefox"])
def test_explicit_engine_never_falls_back_to_chromium(engine) -> None:
    playwright = Mock()
    selected = getattr(playwright, engine)
    assert launch(playwright, required=True, engine=engine) is selected.launch.return_value
    selected.launch.assert_called_once_with(headless=True)
    playwright.chromium.launch.assert_not_called()
    selected.launch.side_effect = RuntimeError("missing")
    with pytest.raises(pytest.fail.Exception, match=engine):
        launch(playwright, required=True, engine=engine)


def test_unknown_engine_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        launch(Mock(), engine="typo")
