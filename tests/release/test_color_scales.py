"""The Python colour-scale list stays in sync with the frontend."""

from __future__ import annotations

import re
from pathlib import Path

from evidential.configuration import COLOR_SCALES

ROOT = Path(__file__).resolve().parents[2]
COLOR_JS = ROOT / "frontend" / "src" / "color.js"


def _keys(block: str) -> set[str]:
    """The lowercase keys of a JS object literal of ``key: [...]`` entries."""
    return set(re.findall(r"^\s{2}([a-z][a-z0-9]*):\s*\[", block, re.M))


def test_python_color_scales_match_the_frontend() -> None:
    source = COLOR_JS.read_text()
    presets = re.search(r"export const COLOR_PRESETS = \{(.*?)\n\};", source, re.S).group(1)
    cmaps = re.search(r"export const COLORMAPS = \{(.*?)\n\};", source, re.S).group(1)
    js = _keys(presets) | _keys(cmaps)
    assert js == set(COLOR_SCALES), f"differs: {js ^ set(COLOR_SCALES)}"
