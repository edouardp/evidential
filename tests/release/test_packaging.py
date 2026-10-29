"""Distribution integrity: the shipped wheel/sdist are complete and clean."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

from packaging.requirements import Requirement

from scripts import check_artifact as gate

ROOT = Path(__file__).resolve().parents[2]


def test_build_system_is_uv_build_with_a_bounded_pin() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    build_system = pyproject["build-system"]
    assert build_system["build-backend"] == "uv_build"
    (requirement,) = build_system["requires"]
    # uv_build ships in lockstep with uv, so the pin is a bounded range.
    assert re.fullmatch(r"uv_build>=[\d.]+,<[\d.]+", requirement), requirement
    assert pyproject["tool"]["uv"]["package"] is True


def test_build_backend_range_includes_the_running_uv_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    requirement = Requirement(pyproject["build-system"]["requires"][0])
    result = subprocess.run(["uv", "--version"], check=True, capture_output=True, text=True)
    version = result.stdout.split()[1]
    assert version in requirement.specifier, f"Update uv_build's bounded range for uv {version} (ADR-034)"


def test_inspect_flags_missing_runtime_files() -> None:
    problems = gate.inspect({})
    assert any("missing evidential/table.py" in problem for problem in problems)


def test_inspect_flags_development_files() -> None:
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
    members["tests/test_table.py"] = b"x"
    members["frontend/src/table.js"] = b"x"
    problems = gate.inspect(members)
    assert any("tests/" in problem for problem in problems)
    assert any("frontend/" in problem for problem in problems)


def test_inspect_rejects_empty_renderer_assets() -> None:
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
    members["evidential/static/table.js"] = b""
    assert any("looks empty" in problem for problem in gate.inspect(members))


def test_dimension_grid_runtime_and_assets_are_required_and_nonempty() -> None:
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
    for name in (
        "evidential/dimension.py",
        "evidential/static/dimension-grid.js",
        "evidential/static/dimension-grid.css",
    ):
        assert name in gate.REQUIRED
        members[name] = b""
        assert f"empty {name}" in gate.inspect(members)
        members[name] = b"x"


def test_inspect_accepts_a_complete_archive() -> None:
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
    members["evidential/py.typed"] = b""
    assert gate.inspect(members) == []


def test_normalize_strips_sdist_prefix() -> None:
    assert gate._normalize("evidential-0.1.0/src/evidential/table.py") == "evidential/table.py"


def test_committed_renderer_assets_are_present_and_substantial() -> None:
    for name in gate.RENDERER_ASSETS:
        path = ROOT / "src" / name
        assert path.is_file(), name
        assert path.stat().st_size >= gate.MIN_RENDERER_BYTES, name


def test_type_marker_is_shipped() -> None:
    assert (ROOT / "src/evidential/py.typed").is_file()
