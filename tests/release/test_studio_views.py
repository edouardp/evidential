"""Committed marimo Studio views stay valid and resolve against their notebook.

These checks are intentionally dependency-light: they parse the view manifest
and the notebook's AST instead of requiring ``marimo-studio`` to be installed,
so they run in the normal local unit suite.
"""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STUDIO_ROOT = ROOT / "notebooks" / "studio"
KNOWN_PROVIDERS = {
    "marimo-studio/vanilla",
    "marimo-studio/deno-react",
    "marimo-studio/svelte",
    "marimo-studio/deno-svelte",
    "marimo-studio/observable-notebook-kit",
}
CELL_PROJECTIONS = re.compile(r"<(?:marimo-cell|marimo-output)\s+name=\"([^\"]+)\"")
VALUE_PROJECTIONS = re.compile(r"\bmo-value=\"([^\"]+)\"")
BASE_IDENTIFIER = re.compile(r"^([A-Za-z_][\w]*)")


def _view_projects() -> list[tuple[Path, Path, str]]:
    """Return ``(notebook, view_dir, view_name)`` for every committed view."""
    projects = []
    for manifest in sorted(STUDIO_ROOT.glob("*/*/view.toml")):
        view_dir = manifest.parent
        view_name = view_dir.name
        notebook = ROOT / "notebooks" / f"{view_dir.parent.name}.py"
        projects.append((notebook, view_dir, view_name))
    return projects


def _defined_symbols(path: Path) -> set[str]:
    """Every function, assignment and import name in a notebook."""
    tree = ast.parse(path.read_text())

    def target_names(node: ast.AST):
        if isinstance(node, ast.Name):
            yield node.id
        elif isinstance(node, (ast.Tuple, ast.List)):
            for element in node.elts:
                yield from target_names(element)

    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                symbols.update(target_names(target))
        elif isinstance(node, ast.AnnAssign):
            symbols.update(target_names(node.target))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                symbols.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.add((alias.asname or alias.name).split(".")[0])
    return symbols


def test_there_is_at_least_one_committed_view() -> None:
    assert _view_projects(), "notebooks/studio must contain a committed view"


@pytest.mark.parametrize("notebook,view_dir,view_name", _view_projects(), ids=lambda value: str(value))
def test_view_manifest_is_valid(notebook: Path, view_dir: Path, view_name: str) -> None:
    assert notebook.is_file(), f"missing notebook for view {view_name}: {notebook}"
    manifest = tomllib.loads((view_dir / "view.toml").read_text())
    assert manifest.get("schema") == 1
    assert manifest.get("provider") in KNOWN_PROVIDERS, manifest.get("provider")


@pytest.mark.parametrize("notebook,view_dir,view_name", _view_projects(), ids=lambda value: str(value))
def test_view_projections_resolve_against_the_notebook(notebook: Path, view_dir: Path, view_name: str) -> None:
    symbols = _defined_symbols(notebook)
    html = (view_dir / "index.html").read_text()
    targets = CELL_PROJECTIONS.findall(html)
    targets += [match.group(1).split(".")[0] for match in VALUE_PROJECTIONS.finditer(html)]
    assert targets, f"{view_name}/index.html has no projections"
    unresolved = sorted({target for target in targets if target not in symbols})
    assert not unresolved, f"{view_name} references unknown notebook targets: {unresolved}"


@pytest.mark.parametrize("notebook,view_dir,view_name", _view_projects(), ids=lambda value: str(value))
def test_notebook_declares_a_studio_config(notebook: Path, view_dir: Path, view_name: str) -> None:
    source = notebook.read_text()
    assert "[tool.marimo-studio]" in source
    assert "view_root" in source
    assert "# [tool.marimo-studio.cells]" in source
