"""Documentation stays valid: examples parse, images exist, fences balance."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = (
    "README.md",
    "docs/design-and-dx.md",
    "docs/technical-architecture.md",
    "docs/marimo-studio.md",
    "docs/RELEASE_PROCESS.md",
    "docs/api/API.md",
)


@pytest.mark.parametrize("relative", DOCS)
def test_python_examples_parse(relative: str) -> None:
    text = (ROOT / relative).read_text()
    blocks = re.findall(r"^```python\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    assert blocks, f"{relative} should keep executable-looking examples"
    for code in blocks:
        ast.parse(code)


@pytest.mark.parametrize("relative", DOCS)
def test_fences_are_balanced(relative: str) -> None:
    text = (ROOT / relative).read_text()
    assert text.count("```") % 2 == 0, f"unbalanced code fences in {relative}"


@pytest.mark.parametrize("relative", DOCS)
def test_local_images_exist(relative: str) -> None:
    text = (ROOT / relative).read_text()
    base = (ROOT / relative).parent
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://")):
            continue
        assert (base / target).exists(), f"{relative}: missing image {target}"


@pytest.mark.parametrize("relative", DOCS)
def test_mermaid_blocks_are_present_and_balanced(relative: str) -> None:
    text = (ROOT / relative).read_text()
    blocks = re.findall(r"^```mermaid\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    for block in blocks:
        assert block.strip(), f"empty mermaid block in {relative}"
        assert block.count("{") == block.count("}"), relative


def test_api_images_match_the_screenshot_script() -> None:
    """Every committed API image is referenced from API.md, and vice versa."""
    doc = ROOT / "docs" / "api" / "API.md"
    referenced = {
        Path(target).name
        for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", doc.read_text())
        if target.startswith("images/")
    }
    committed = {path.name for path in (ROOT / "docs" / "api" / "images").glob("*.png")}
    assert referenced == committed, (
        f"only in API.md: {sorted(referenced - committed)}; only on disk: {sorted(committed - referenced)}"
    )


@pytest.mark.parametrize("name", ("line", "area", "bar"))
def test_sparkline_svgs_are_standalone_graphs(name: str) -> None:
    """The committed sparkline SVGs are valid, self-contained graphics."""
    svg = ROOT / "docs" / "img" / "sparklines" / f"{name}.svg"
    root = ElementTree.parse(svg).getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg", root.tag
    assert root.get("viewBox"), "a standalone SVG should scale via viewBox"
    # Just the graph: no tooltips and no transparent hover targets.
    assert not root.findall(".//{http://www.w3.org/2000/svg}title")
    assert all(el.get("fill") != "transparent" for el in root.iter())
