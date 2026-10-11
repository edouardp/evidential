"""Documentation stays valid: examples parse, images exist, fences balance."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ("README.md", "docs/design-and-dx.md", "docs/technical-architecture.md")


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
