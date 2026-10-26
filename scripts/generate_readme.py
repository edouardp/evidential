"""Generate README examples and screenshots from named marimo cells.

Run ``make readme`` to refresh, or ``make readme-check`` to check without a browser.
Only regions delimited by ``<!-- notebook: path#cell -->`` and
``<!-- /notebook -->`` are replaced. Each table cell has a ``<cell>_doc``
Markdown cell; the screenshot registry in api_screenshots supplies its image.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import re
import tempfile
import textwrap
import tomllib
from pathlib import Path

from scripts.api_screenshots import ROOT, _notebook_targets, render

README = ROOT / "README.md"
MANIFEST = ROOT / "docs" / "readme-snapshots.json"
PYPI_README = ROOT / "docs" / "PYPI_README.md"
ASSET_ROOT = "https://raw.githubusercontent.com/edouardp/evidential/main/"
REPO_ROOT = "https://github.com/edouardp/evidential/blob/main/"
START = re.compile(r"^<!-- notebook: ([\w/.-]+\.py)#(\w+)( image-only)? -->$", re.MULTILINE)
END = "<!-- /notebook -->"
TABLES = {"EvidentialTable", "grouped_table", "pivot_table", "comparison_table", "query_table"}


def _cell(source: str, name: str) -> ast.FunctionDef:
    cells = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(cells) != 1:
        raise ValueError(f"Expected one named cell {name!r}; found {len(cells)}")
    cell = cells[0]
    if not any(
        ast.unparse(decorator.func if isinstance(decorator, ast.Call) else decorator) == "app.cell"
        for decorator in cell.decorator_list
    ):
        raise ValueError(f"{name!r} must be a marimo @app.cell")
    return cell


def markdown(source: str, cell: str) -> str:
    """Read a literal mo.md cell without executing notebook code."""
    calls = [
        node
        for node in ast.walk(_cell(source, f"{cell}_doc"))
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "mo.md"
    ]
    if len(calls) != 1 or len(calls[0].args) != 1:
        raise ValueError(f"{cell}_doc must contain exactly one mo.md(literal_string)")
    value = calls[0].args[0]
    if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
        raise ValueError(f"{cell}_doc: use a literal Markdown string, not interpolation")
    return inspect.cleandoc(value.value)


def _fragment(source: str, node: ast.AST) -> str:
    # AST offsets select the original source, preserving comments, parentheses,
    # quotes and fluent chains. Dedent the enclosing cell, not the inner list.
    segment = ast.get_source_segment(source, node)
    assert segment is not None
    return textwrap.dedent(" " * node.col_offset + segment).strip()


def column_code(source: str, cell: str) -> str:
    """Extract columns=[...] or the aggregate helper call that configures them."""
    calls = [
        node
        for node in ast.walk(_cell(source, cell))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in TABLES
    ]
    if len(calls) != 1:
        raise ValueError(f"{cell}: expected one table call; found {len(calls)}")
    call = calls[0]
    columns = next((keyword for keyword in call.keywords if keyword.arg == "columns"), None)
    if columns is not None:
        if not isinstance(columns.value, ast.List):
            raise ValueError(f"{cell}: inline the columns=[...] list so the excerpt is self-contained")
        return _fragment(source, columns)
    if call.func.id == "EvidentialTable":
        raise ValueError(f"{cell}: provide columns=[...] for the documented table")
    return _fragment(source, call)


def generate(text: str, root: Path = ROOT) -> str:
    """Replace generated regions; preserve every byte outside them."""
    images = {
        (str(notebook.relative_to(ROOT)), cell): str(image.relative_to(ROOT))
        for notebook, targets in _notebook_targets()
        for image, cell in targets
    }
    chunks: list[str] = []
    cursor = 0
    seen: set[tuple[str, str]] = set()
    for match in START.finditer(text):
        if match.start() < cursor:
            raise ValueError("Nested notebook regions are not supported")
        if END in text[cursor : match.start()]:
            raise ValueError("Unmatched notebook closing marker")
        end = text.find(END, match.end())
        if end < 0:
            raise ValueError(f"Missing {END} after {match.group(0)}")
        key = (match[1], match[2])
        if key in seen:
            raise ValueError(f"Duplicate README example: {key}")
        seen.add(key)
        if key not in images:
            raise ValueError(f"Register a screenshot target for {key} in scripts/api_screenshots.py")
        source = (root / match[1]).read_text()
        description = markdown(source, match[2])
        code = "" if match[3] else f"```python\n{column_code(source, match[2])}\n```\n\n"
        heading = next((line.lstrip("# ") for line in description.splitlines() if line.startswith("#")), match[2])
        alt = heading.replace("[", "").replace("]", "")
        body = f"{description}\n\n{code}![{alt}]({images[key]})\n\n[Notebook source: `{match[2]}`]({match[1]})\n"
        chunks.extend((text[cursor : match.end()], "\n\n", body, "\n", END))
        cursor = end + len(END)
    if not seen:
        raise ValueError("README must contain at least one notebook region")
    tail = text[cursor:]
    if END in tail or "<!-- notebook:" in START.sub("", text):
        raise ValueError("Unmatched or malformed notebook marker")
    chunks.append(tail)
    return "".join(chunks)


def pypi_readme(text: str) -> str:
    """Resolve repository links for PyPI without changing the repository README."""

    def absolute(match: re.Match, *, image: bool = False) -> str:
        opening, target, closing = match.groups()
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(("#", "//")):
            return match[0]
        prefix = ASSET_ROOT if image else REPO_ROOT
        return f"{opening}{prefix}{target.removeprefix('./')}{closing}"

    # Skip fenced examples: link syntax inside an example is code, not a link.
    parts = re.split(r"(^```[^\n]*\n.*?^```[ \t]*$)", text, flags=re.MULTILINE | re.DOTALL)
    for index in range(0, len(parts), 2):
        # Resolve images first, then other link targets. Matching targets also
        # handles outer links around badges, e.g. [![License](badge.svg)](LICENSE).
        parts[index] = re.sub(
            r"(!\[[^\]\n]*\]\()([^)\s]+)(\))", lambda match: absolute(match, image=True), parts[index]
        )
        parts[index] = re.sub(r"(\]\()([^)\s]+)(\))", absolute, parts[index])
    return "<!-- Generated from README.md by make readme; do not edit. -->\n\n" + "".join(parts)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _input_digest(path: Path) -> str:
    if path.name in {"pyproject.toml", "uv.lock"}:
        data = tomllib.loads(path.read_text())
        # A release bump changes no rendering. Keep dependency/configuration
        # changes in the fingerprint without making every patch release recapture.
        if path.name == "pyproject.toml":
            data.get("project", {}).pop("version", None)
        else:
            for package in data.get("package", []):
                if package.get("name") == "evidential" and package.get("source") == {"editable": "."}:
                    package.pop("version", None)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return _digest(path)


def inputs(root: Path = ROOT) -> dict[str, str]:
    """Conservative provenance: code, environment, fixture and renderer changes invalidate images."""
    paths = [
        root / "scripts/api_screenshots.py",
        root / "scripts/generate_readme.py",
        root / "pyproject.toml",
        root / "uv.lock",
        root / "notebooks/sample_data/needful_things/orders.parquet",
        *(root / notebook.relative_to(ROOT) for notebook, _ in _notebook_targets()),
        *(root / "src/evidential").rglob("*.py"),
        *(root / "src/evidential/static").glob("*.js"),
        *(root / "src/evidential/static").glob("*.css"),
    ]
    return {str(path.relative_to(root)): _input_digest(path) for path in sorted(set(paths))}


def snapshot_manifest(root: Path = ROOT) -> dict:
    return {
        "version": 1,
        "inputs": inputs(root),
        "images": {
            str(path.relative_to(ROOT)): {
                "notebook": str(notebook.relative_to(ROOT)),
                "cell": cell,
                "sha256": _digest(root / path.relative_to(ROOT)),
            }
            for notebook, targets in _notebook_targets()
            for path, cell in targets
        },
    }


def check(root: Path = ROOT) -> list[str]:
    """Report stale generated text, inputs or image bytes without starting a browser."""
    errors = []
    text = (root / "README.md").read_text()
    if generate(text, root) != text:
        errors.append("README notebook regions differ from their source cells")
    pypi = root / PYPI_README.relative_to(ROOT)
    if not pypi.exists() or pypi.read_text() != pypi_readme(text):
        errors.append("PyPI README differs from the repository README")
    manifest = root / MANIFEST.relative_to(ROOT)
    if not manifest.exists():
        return [*errors, "Screenshot provenance is missing"]
    recorded = json.loads(manifest.read_text())
    current = snapshot_manifest(root)
    if recorded.get("version") != current["version"]:
        errors.append("Screenshot manifest version changed")
    for section in ("inputs", "images"):
        before, after = recorded.get(section, {}), current[section]
        changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
        if changed:
            errors.append(f"Stale screenshot {section}: {', '.join(changed)}")
    return errors


def build() -> None:
    # Validate all prose/excerpts before launching a browser. Stage images so a
    # failed notebook never blesses a partially refreshed set of screenshots.
    original = README.read_text()
    generated = generate(original)
    before = inputs()
    with tempfile.TemporaryDirectory(prefix="evidential-readme-") as directory:
        staging = Path(directory)
        captured = list(render(output_root=staging))
        expected = {staging / path.relative_to(ROOT) for _, targets in _notebook_targets() for path, _ in targets}
        if set(captured) != expected or len(captured) != len(expected):
            raise ValueError("Capture did not return every registered screenshot exactly once")
        if before != inputs() or original != README.read_text():
            raise ValueError("Documentation sources changed during capture; rerun make readme")
        for path in captured:
            destination = ROOT / path.relative_to(staging)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
        README.write_text(generated)
        PYPI_README.write_text(pypi_readme(generated))
        manifest = snapshot_manifest()
        manifest["inputs"] = before
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Updated README and {len(captured)} notebook screenshots")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on stale README or screenshots; no browser needed")
    args = parser.parse_args()
    try:
        if args.check:
            errors = check()
            if errors:
                parser.exit(1, "\n".join(errors) + "\nRun make readme and commit the generated files.\n")
            print("README examples and notebook screenshots are current")
        else:
            build()
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
