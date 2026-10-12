"""Distribution integrity: the shipped wheel/sdist are complete and clean."""

from __future__ import annotations

from pathlib import Path

from scripts import check_artifact as gate

ROOT = Path(__file__).resolve().parents[2]


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


def test_inspect_accepts_a_complete_archive() -> None:
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
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
