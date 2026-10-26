"""Documentation stays valid: examples parse, images exist, fences balance."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[2]
README_ASSET_ROOT = "https://raw.githubusercontent.com/edouardp/evidential/main/"
DOCS = (
    "README.md",
    "docs/design-and-dx.md",
    "docs/technical-architecture.md",
    "docs/marimo-studio.md",
    "docs/RELEASE_PROCESS.md",
    "docs/api/API.md",
)


def test_notebooks_and_documentation_use_bar_marks_instead_of_scalar_decorators():
    sources = [(str(path.relative_to(ROOT)), path.read_text()) for path in (ROOT / "notebooks").glob("*.py")]
    for relative in DOCS:
        blocks = re.findall(r"^```python\n(.*?)^```$", (ROOT / relative).read_text(), re.MULTILINE | re.DOTALL)
        sources.extend((relative, block) for block in blocks)
    for relative, source in sources:
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "bar":
                continue
            root = node.func.value
            while (
                isinstance(root, ast.Call)
                and isinstance(root.func, ast.Attribute)
                and isinstance(root.func.value, ast.Call)
            ):
                root = root.func.value
            if (
                isinstance(root, ast.Call)
                and isinstance(root.func, ast.Attribute)
                and isinstance(root.func.value, ast.Name)
            ):
                assert not (
                    root.func.value.id == "col"
                    and root.func.attr in {"number", "integer", "currency", "percent", "auto"}
                ), f"{relative}:{node.lineno}: use col.bar(source, format=..., label=True)"


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
        if target.startswith(README_ASSET_ROOT):
            assert (ROOT / target.removeprefix(README_ASSET_ROOT)).exists(), f"{relative}: missing image {target}"
            continue
        if target.startswith(("http://", "https://")):
            continue
        assert (base / target).exists(), f"{relative}: missing image {target}"


def test_readme_images_are_absolute_for_pypi():
    targets = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", (ROOT / "README.md").read_text())
    assert targets
    assert all(target.startswith("https://") for target in targets), "PyPI cannot resolve repository-relative images"


@pytest.mark.parametrize("relative", DOCS)
def test_mermaid_blocks_are_present_and_balanced(relative: str) -> None:
    text = (ROOT / relative).read_text()
    blocks = re.findall(r"^```mermaid\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    for block in blocks:
        assert block.strip(), f"empty mermaid block in {relative}"
        assert block.count("{") == block.count("}"), relative


def test_api_images_match_the_screenshot_script() -> None:
    """API.md, the capture script and the committed images use the same slugs."""
    from scripts.api_screenshots import SHOTS

    doc = ROOT / "docs" / "api" / "API.md"
    referenced = {
        Path(target).name
        for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", doc.read_text())
        if target.startswith("images/")
    }
    committed = {path.name for path in (ROOT / "docs" / "api" / "images").glob("*.png")}
    expected = {f"{slug}.png" for slug, _ in SHOTS}
    assert referenced == expected == committed, (
        f"only in API.md: {sorted(referenced - expected)}; "
        f"only in SHOTS: {sorted(expected - referenced)}; "
        f"only on disk: {sorted(committed - expected)}"
    )


def test_screenshots_have_a_named_notebook_cell() -> None:
    """Every capture target points at a cell in its screenshot notebook."""
    from scripts.api_screenshots import EXTRAS, GALLERY, GALLERY_NOTEBOOK, NOTEBOOK, SHOTS

    for notebook, targets in ((NOTEBOOK, [*SHOTS, *EXTRAS]), (GALLERY_NOTEBOOK, GALLERY)):
        tree = ast.parse(notebook.read_text())
        cells = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        names = [cell for _, cell in targets]
        missing = [cell for cell in names if cell not in cells]
        assert not missing, f"missing screenshot cell(s) in {notebook.name}: {missing}"
        assert len(set(names)) == len(names), f"screenshot cell names in {notebook.name} must be unique"


def test_gallery_images_match_readme_and_capture_targets() -> None:
    """The README references every captured gallery image, and vice versa."""
    from scripts.api_screenshots import GALLERY

    referenced = {
        path
        for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", (ROOT / "README.md").read_text())
        if (path := target.removeprefix(README_ASSET_ROOT)).startswith("docs/img/graphics/")
    }
    expected = {str(path.relative_to(ROOT)) for path, _ in GALLERY}
    committed = {str(path.relative_to(ROOT)) for path in (ROOT / "docs" / "img" / "graphics").glob("*.png")}
    assert referenced == expected == committed, (
        f"only in README: {sorted(referenced - expected)}; "
        f"only in GALLERY: {sorted(expected - referenced)}; "
        f"only on disk: {sorted(committed - expected)}"
    )


@pytest.mark.parametrize(
    "name",
    [f"{style}-{index}" for style in ("line", "area", "bar") for index in range(1, 6)],
)
def test_sparkline_svgs_are_standalone_graphs(name: str) -> None:
    """The sparkline SVGs are valid, self-contained, unclipped graphics."""
    svg = ROOT / "docs" / "img" / "sparklines" / f"{name}.svg"
    ns = "{http://www.w3.org/2000/svg}"
    root = ElementTree.parse(svg).getroot()
    assert root.tag == f"{ns}svg", root.tag
    assert not root.findall(f".//{ns}title"), "just the graph: no tooltips"
    assert all(el.get("fill") != "transparent" for el in root.iter())
    # The viewBox is tight but contains every painted point, with a clear safety
    # margin, so a consumer that clips to the box cannot cut the graph.
    view = [float(value) for value in (root.get("viewBox") or "").replace(",", " ").split()]
    assert len(view) == 4, root.get("viewBox")
    x0, y0, width, height = view
    margin = 1.0
    xs: list[float] = []
    ys: list[float] = []
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag in ("polyline", "polygon"):
            half = float(el.get("stroke-width") or 0) / 2
            for point in el.get("points", "").split():
                px, py = (float(value) for value in point.split(","))
                xs += [px - half, px + half]
                ys += [py - half, py + half]
        elif tag == "rect":
            x, y, w, h = (float(el.get(key)) for key in ("x", "y", "width", "height"))
            xs += [x, x + w]
            ys += [y, y + h]
    assert x0 + margin <= min(xs) and max(xs) <= x0 + width - margin, f"{name} too close to the edge"
    assert y0 + margin <= min(ys) and max(ys) <= y0 + height - margin, f"{name} too close to the edge"
