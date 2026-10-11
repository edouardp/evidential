"""The Makefile help stays grouped, ordered and colour-free when piped."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SECTIONS = (
    "Setup and Installation",
    "Frontend",
    "Notebooks",
    "Preview",
    "marimo Studio",
    "Code Quality",
    "Testing",
    "Dependencies",
    "Build",
    "Cleanup",
    "Validation",
)


def test_make_help_groups_targets_by_section_without_ansi() -> None:
    result = subprocess.run(["make", "help"], cwd=ROOT, capture_output=True, text=True, check=True)
    output = result.stdout

    positions = [output.index(f"\n  {section}\n") for section in SECTIONS]
    assert positions == sorted(positions)
    assert "lint" in output
    assert "test-browser" in output
    assert "validate" in output
    assert "\x1b[" not in output


def test_validate_depends_on_lint_and_tests() -> None:
    makefile = (ROOT / "Makefile").read_text()
    validate = next(line for line in makefile.splitlines() if line.startswith("validate:"))
    assert "lint" in validate
    assert "test" in validate
